# pdf_tools.py - starter utilities for extracting images and converting PDFs to Markdown
from __future__ import annotations

import base64, io, os
import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import fitz  # PyMuPDF
from PIL import Image  # re-encode用（PNG固定にするため）

@dataclass
class ImageSaveResult:
    page_index: int
    xref: int
    width: int
    height: int
    saved_path: Path
    original_ext: str
    target_ext: str
    sha1: str

def _bytes_sha1(data: bytes) -> str:
    import hashlib
    return hashlib.sha1(data).hexdigest()

def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def _convert_pngs_to_svg_with_aspose_imaging(png_paths: List[Path]) -> List[Path]:
    """Aspose.Imaging を使った PNG→SVG 変換（最優先）"""
    try:
        from aspose.imaging import Image as AsposeImage
        from aspose.imaging.imageoptions import SvgOptions, SvgRasterizationOptions
    except Exception as e:
        return []
    svgs: List[Path] = []
    for p in png_paths:
        svg_path = p.with_suffix(".svg")
        with AsposeImage.load(str(p)) as img:
            opts = SvgOptions()
            opts.vectorize = False  # 画像をそのまま埋め込む（“真の”ベクタ化ではない）
            # 必要なら rasterization オプションを設定
            opts.rasterization_options = SvgRasterizationOptions()
            img.save(str(svg_path), opts)
        svgs.append(svg_path)
    return svgs  # Aspose.Imaging 公式の PNG→SVG 例に準拠。:contentReference[oaicite:3]{index=3}

def _convert_pngs_to_svg_with_aspose_words(png_paths: List[Path]) -> List[Path]:
    """Aspose.Words を使った PNG→SVG 変換（代替案）"""
    try:
        import aspose.words as aw
    except Exception:
        return []
    svgs: List[Path] = []
    for p in png_paths:
        doc = aw.Document()
        builder = aw.DocumentBuilder(doc)
        builder.insert_image(str(p))  # 画像1枚＝1ページ
        svg_path = p.with_suffix(".svg")
        doc.save(str(svg_path))       # 拡張子が .svg ならSVGで保存される。:contentReference[oaicite:4]{index=4}
        svgs.append(svg_path)
    return svgs

def _wrap_pngs_as_svg_fallback(png_paths: List[Path]) -> List[Path]:
    """Asposeが無い環境向け：<image> 埋め込みのミニマルSVGを作る"""
    svgs: List[Path] = []
    for p in png_paths:
        from PIL import Image as PILImage
        with PILImage.open(p) as im:
            w, h = im.size
        b64 = base64.b64encode(p.read_bytes()).decode("ascii")
        svg = (
            f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>"
            f"<image href='data:image/png;base64,{b64}' x='0' y='0' width='{w}' height='{h}'/>"
            f"</svg>"
        )
        svg_path = p.with_suffix(".svg")
        svg_path.write_text(svg, encoding="utf-8")
        svgs.append(svg_path)
    return svgs

def extract_images_from_pdf(
    pdf_path: str | os.PathLike,
    output_dir: str | os.PathLike,
    target_format: Optional[str] = None,
    min_size: Tuple[int, int] = (1, 1),
    dedupe: bool = True,
    convert_pngs_to_svg: bool = True,   # ★ 追加：PNGをSVG化するか
    prefer: str = "words",           # "imaging" | "words" | "fallback"
) -> List[ImageSaveResult]:
    """
    1) PDF内の埋め込み画像を抽出して PNG として保存（元がPNG以外でもPNG固定）。
    2) convert_pngs_to_svg=True の場合、同ディレクトリに SVG も作成（Aspose優先）。

    PyMuPDFの画像抽出は公式のレシピ/ドキュメントに準じる実装です。:contentReference[oaicite:5]{index=5}
    """
    pdf_path = str(pdf_path)
    out_dir = Path(output_dir)
    _ensure_dir(out_dir)

    results: List[ImageSaveResult] = []
    seen_hashes: set[str] = set()
    saved_pngs: List[Path] = []

    with fitz.open(pdf_path) as doc:
        for page_index, page in enumerate(doc):
            for img_info in page.get_images(full=True):
                xref = img_info[0]
                try:
                    img_dict = doc.extract_image(xref)  # {'image': bytes, 'ext': 'png'|'jpeg'...} :contentReference[oaicite:6]{index=6}
                except Exception:
                    continue

                image_bytes: bytes = img_dict["image"]
                width: int = img_dict.get("width", 0)
                height: int = img_dict.get("height", 0)

                if width < min_size[0] or height < min_size[1]:
                    continue

                sha1 = _bytes_sha1(image_bytes)
                if dedupe and sha1 in seen_hashes:
                    continue
                seen_hashes.add(sha1)

                # 常に PNG で保存（あとでSVGに変換する前提）
                stem = f"page{page_index+1:04d}_img{xref}_{sha1[:8]}"
                png_path = out_dir / f"{stem}.png"

                # 元がPNGならバイトそのまま、他形式はPillowでPNGへ再エンコード
                original_ext: str = img_dict.get("ext", "png").lower()
                if original_ext == "png":
                    png_path.write_bytes(image_bytes)
                else:
                    with Image.open(io.BytesIO(image_bytes)) as im:
                        if im.mode in ("RGBA", "LA", "P"):
                            im = im.convert("RGBA")  # 透過を維持
                        else:
                            im = im.convert("RGB")
                        im.save(png_path, format="PNG")

                saved_pngs.append(png_path)

                results.append(
                    ImageSaveResult(
                        page_index=page_index,
                        xref=xref,
                        width=width,
                        height=height,
                        saved_path=png_path,
                        original_ext=original_ext,
                        target_ext="png",
                        sha1=sha1,
                    )
                )

    # --- ここから PNG → SVG 変換（同ディレクトリに .svg を併置） ---
    if convert_pngs_to_svg and saved_pngs:
        made = []
        if prefer == "imaging":
            made = _convert_pngs_to_svg_with_aspose_imaging(saved_pngs)  # :contentReference[oaicite:7]{index=7}
            if not made:
                # Imagingが無ければWordsへ
                made = _convert_pngs_to_svg_with_aspose_words(saved_pngs)  # :contentReference[oaicite:8]{index=8}
        elif prefer == "words":
            made = _convert_pngs_to_svg_with_aspose_words(saved_pngs)      # :contentReference[oaicite:9]{index=9}
        # どちらも無い/失敗 → フォールバック
        if not made:
            _wrap_pngs_as_svg_fallback(saved_pngs)

    return results


def pdf_to_markdown(
    pdf_path: str | os.PathLike,
    md_output_path: str | os.PathLike,
    write_images: bool = True,
    image_dir: Optional[str | os.PathLike] = None,
    image_format: str = "png",
    page_chunks: bool = False,
    **kwargs,
) -> str:
    """
    Convert a PDF to Markdown using pymupdf4llm and save it.

    Args:
        pdf_path: Input PDF path.
        md_output_path: Where to write the resulting Markdown file.
        write_images: If True, rasterize image/graphics regions into separate image files.
        image_dir: Directory to store images (used when write_images=True).
        image_format: Format for rasterized images (e.g., 'png', 'jpg').
        page_chunks: If True, chunk Markdown per page with page headings.
        **kwargs: Passed through to pymupdf4llm.to_markdown() (e.g., page_range).

    Returns:
        The Markdown text as a string (also written to md_output_path).
    """
    import pymupdf4llm  # lazy import

    if write_images:
        if image_dir is None:
            image_dir = Path(str(md_output_path) + ".assets")
        _ensure_dir(Path(image_dir))

    md_text: str = pymupdf4llm.to_markdown(
        str(pdf_path),
        page_chunks=page_chunks,
        write_images=write_images,
        image_path=str(image_dir) if image_dir else None,
        image_format=image_format,
        dpi=1200,
        **kwargs,
    )

    md_path = Path(md_output_path)
    _ensure_dir(md_path.parent)
    md_path.write_text(md_text, encoding="utf-8")
    return md_text


def build_cli_parser() -> argparse.ArgumentParser:
    """Build a simple CLI for quick testing."""
    p = argparse.ArgumentParser(description="PDF utilities: extract images and convert to Markdown.")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_img = sub.add_parser("extract-images", help="Extract embedded images from a PDF.")
    p_img.add_argument("pdf", type=str, help="Input PDF path")
    p_img.add_argument("outdir", type=str, help="Output directory for images")
    p_img.add_argument("--format", type=str, default=None, help="Target format (e.g., png, jpg). Default = keep original")
    p_img.add_argument("--min-width", type=int, default=1, help="Minimum image width to keep")
    p_img.add_argument("--min-height", type=int, default=1, help="Minimum image height to keep")
    p_img.add_argument("--no-dedupe", action="store_true", help="Disable hash-based deduplication")

    p_md = sub.add_parser("to-markdown", help="Convert a PDF to Markdown using pymupdf4llm.")
    p_md.add_argument("pdf", type=str, help="Input PDF path")
    p_md.add_argument("md", type=str, help="Output Markdown file path")
    p_md.add_argument("--write-images", action="store_true", help="Rasterize and save images / graphics")
    p_md.add_argument("--image-dir", type=str, default=None, help="Directory to save images")
    p_md.add_argument("--image-format", type=str, default="png", help="Image format for rasterized figures")
    p_md.add_argument("--page-chunks", action="store_true", help="Chunk Markdown per page")

    return p


def main() -> None:
    """CLI entry point."""
    parser = build_cli_parser()
    args = parser.parse_args()

    if args.cmd == "extract-images":
        results = extract_images_from_pdf(
            pdf_path=args.pdf,
            output_dir=args.outdir,
            target_format=args.format,
            min_size=(args.min_width, args.min_height),
            dedupe=not args.no_dedupe,
        )
        print(f"Saved {len(results)} images to {args.outdir}")
        for r in results[:5]:
            print(f"- page {r.page_index+1}, xref {r.xref}, {r.width}x{r.height} -> {r.saved_path.name}")
        if len(results) > 5:
            print(f"... and {len(results)-5} more")
    elif args.cmd == "to-markdown":
        md_text = pdf_to_markdown(
            pdf_path=args.pdf,
            md_output_path=args.md,
            write_images=args.write_images,
            image_dir=args.image_dir,
            image_format=args.image_format,
            page_chunks=args.page_chunks,
        )
        print(f"Markdown written to: {args.md} ({len(md_text)} chars)")


if __name__ == "__main__" and "ipykernel" not in sys.modules:
    main()
