# pdf_tools.py - starter utilities for extracting images and converting PDFs to Markdown
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Tuple

import pymupdf  # PyMuPDF
import pymupdf4llm
from PIL import Image  # re-encode用（PNG固定にするため）
import shutil
import re
from typing import Union


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _sanitize_filename(name: str, max_len: int = 120) -> str:
    """
    ファイル名/ディレクトリ名に使える形に正規化する。
    半角英数字とハイフン/アンダースコア以外はアンダースコアに置換。
    空白はすべてアンダーバーに置換する。
    連続するアンダースコアはまとめ、長すぎる場合は切る。
    """
    s = name.strip()
    # 空白は全てアンダースコアに変更
    s = s.replace(" ", "_")
    # Windows 等で問題になる文字を排除
    s = re.sub(r'[<>:"/\\\\|?*\x00-\x1F]', "_", s)
    # 許可文字以外を underscore に（スペースは既に置換済み）
    s = re.sub(r'[^0-9A-Za-z\u0080-\uFFFF\-\_]+', "_", s)
    # 連続するアンダースコアをまとめる
    s = re.sub(r'_+', "_", s)
    s = s.strip("_")
    if not s:
        return "untitled"
    if len(s) > max_len:
        s = s[:max_len].rstrip("_")
    return s


def pdf_to_markdown(
    pdf_path: str | os.PathLike,
    md_output_path: str | os.PathLike,
    write_images: bool = True,
    image_dir: Optional[str | os.PathLike] = 'materials',
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

    # 入力パスを Path に統一
    src_pdf = Path(pdf_path)
    doc = pymupdf.open(str(src_pdf))
    title = doc.metadata.get("title", "")
    if title:
        print(f"Converting PDF '{title}' to Markdown...")

        # タイトル名のディレクトリを作成して元PDFを移動
        safe_title = _sanitize_filename(title)
        dest_dir = src_pdf.parent / safe_title
        _ensure_dir(dest_dir)
        dest_pdf = dest_dir / src_pdf.name
        try:
            # 既に移動済みでなければ移動する
            if src_pdf.resolve() != dest_pdf.resolve():
                shutil.move(str(src_pdf), str(dest_pdf))
                print(f"Moved PDF to '{dest_pdf}'")
                # 以降の処理は移動先のパスを使う
                src_pdf = dest_pdf
        except Exception as e:
            print(f"Warning: failed to move PDF into title directory: {e}")

        # 画像出力ディレクトリ
        if write_images and image_dir:
            image_dir = os.path.join(dest_dir, image_dir)

        md_text: str = pymupdf4llm.to_markdown(
            str(src_pdf),
            page_chunks=page_chunks,
            write_images=write_images,
            image_path=str(image_dir),
            image_format=image_format,
            dpi=1200,
            **kwargs,
        )

        # 出力先 md の絶対パスを決定
        md_output_path = os.path.join(dest_dir, md_output_path)
        md_path = Path(md_output_path)
        _ensure_dir(md_path.parent)

        # Markdown 内の画像パスが絶対パスになっている場合、md から見た相対パスに置換する
        if image_dir:
            try:
                image_dir_path = Path(image_dir)
                md_parent = md_path.parent
                # 相対パスを計算（Posix 形式）
                rel = os.path.relpath(
                    str(image_dir_path), start=str(md_parent))
                rel_posix = Path(rel).as_posix()
                if not (rel_posix.startswith(".") or rel_posix.startswith("/")):
                    rel_posix = "./" + rel_posix

                # 置換対象として絶対パス／解決済みパスを収集して置換
                abs_candidates = {image_dir_path.as_posix()}
                try:
                    abs_candidates.add(image_dir_path.resolve().as_posix())
                except Exception:
                    pass
                for p in abs_candidates:
                    md_text = md_text.replace(p, rel_posix)
            except Exception as e:
                print(
                    f"Warning: failed to adjust image paths to relative: {e}")

        md_path.write_text(md_text, encoding="utf-8")
        return {"md_text": md_text, "dest_dir": str(dest_dir)}


if __name__ == "__main__":
    pdf_to_markdown(
        pdf_path="/workspaces/PaperInterpreter/2506.13252v1.pdf",
        md_output_path="output.md",
        write_images=True,
        image_format="png",
    )
