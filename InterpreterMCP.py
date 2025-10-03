from fastmcp import FastMCP
from tools.PDFTools import pdf_to_markdown

# Create a server instance
mcp = FastMCP(name="Interpreter Assistant Server")


@mcp.tool(name="PDF to Markdown Converter", description="Convert a PDF file to Markdown format, extracting text and images.")
def pdf_to_markdown(
    pdf_path: str,
    md_output_path: str = "output.md",
    write_images: bool = True,
    image_dir: str = 'materials',
    image_format: str = "png",
    page_chunks: bool = False,
    **kwargs,
) -> str:
    """
    Convert a PDF file to Markdown format, extracting text and images.

    Args:
        pdf_path (str): Path to the input PDF file.
        md_output_path (str): Path to the output Markdown file.
        write_images (bool, optional): Whether to extract and save images. Defaults to True.
        image_dir (str, optional): Directory to save extracted images. Defaults to 'materials'.
        image_format (str, optional): Image format for extracted images. Defaults to "png".
        page_chunks (bool, optional): Whether to chunk pages. Defaults to False.
        **kwargs: Additional keyword arguments for pymupdf4llm.to_markdown.

    Returns:
        dict: 辞書型を返します。構造は {"md_text": md_text, "dest_dir": str(dest_dir)} です。
              - md_text (str): 生成された Markdown の文字列
              - dest_dir (str): 元の PDF を移動した先のディレクトリのパス
    """

    return pdf_to_markdown(
        pdf_path=pdf_path,
        md_output_path=md_output_path,
        write_images=write_images,
        image_dir=image_dir,
        image_format=image_format,
        page_chunks=page_chunks,
        **kwargs,
    )


@mcp.prompt(name="PDF to Markdown Conversion Prompt", description="Convert the provided PDF file to Markdown format, extracting text and images. Save the output to the specified path.")
def MatSci_Interpreter_prompt(pdf_path: str) -> str:

    prompt = f"""あなたは材料科学（Materials Science）の専門家チームを代表し、材料科学はもちろん、固体物理学、結晶科学、群論、量子力学などの関連分野の最先端の知見にも精通する
    優秀な大学教授です。以下の指示に従い、与えられた論文 PDF（パス: {pdf_path}）を読み取り、利用者の知識レベルに合わせた分かりやすく具体的なreport（Markdown形式、ファイル名: report.md想定）を作成してください。

1) あなたのペルソナ
   - 主査ペルソナ: 「応用材料科学の研究者（博士, 10年以上）」。技術的に厳密だが、非専門家にも説明できる能力を持つ。
   - 補助ペルソナ: 「材料試験エンジニア」「産業応用コンサルタント」「大学院生（入門）」の視点を持ち、各読者層向けに表現を調整する。

2) 読者層（audience）と詳細レベル（detail）
   - audience: 材料科学や量子力学、固体物理学の基礎を理解しているが、高度な知識は有していない「大学院1年性の学生」。
   - detail: 「high」。技術的な正確さを保ちつつ、初心者にも理解できるように詳細に説明する。

3) 出力フォーマット（必須）
   - Markdown ファイル（report.md）に YAML ヘッダを付与（title, authors, source_pdf, generated_by, audience, summary_length）。
   - セクション順序:
     1. Title / Authors / Citation（原文のメタ情報）
     2. TL;DR（3行程度）
     3. 要点サマリ（箇条書き、技術的要約）
     4. 背景（初心者向けに概説）
     5. 目的・貢献（原文の主張を簡潔に）
     6. 手法（重要な実験・計算手順、式は $...$ / $$...$$ で KaTeX 表記）
     7. 主要結果（図表のキャプションと注釈を含む）
     8. 考察（解釈、バイアス、弱点）
     9. 実用的インプリケーション（応用・産業的意義）
     10. 重要な疑問点 & 再現性チェックリスト
     11. 推奨アクション（研究者／エンジニア向け）
     12. 参考文献（原文の参照を列挙）
     13. Appendix: 元の Markdown（抜粋）や図のファイル一覧（相対パス）

4) 作業手順（ステップ）
   - (A) まず PDF を Markdown に変換（ローカルツール: call the tool that runs [`tools.PDFTools.pdf_to_markdown`](tools/PDFTools.py) を想定）。出力された md_text を使って以下を行う。
   - (B) 本文をセクション毎に要約し、重要箇所には引用元ページ/段落を付与。
   - (C) すべての図表参照は相対パス（例: ./materials/...）へ整形。画像キャプションを自動生成して図の意味を1-2文で要約。
   - (D) 技術的主張や数値はそのまま再現し、必要なら簡潔な検算／単位確認を行う。
   - (E) 読者レベル（下記の audience 指定）に応じて「表現の粒度」を調整する。

5) 出力の品質チェック（必須）
   - 技術用語の定義が不足していないか
   - 主要結論とエビデンス（ページ番号／図番号）を必ず紐づける
   - 再現性チェックリスト（データ、条件、バージョン、スクリプト）
   - 不確かな箇所には「不確か」と明記

6) 書式・表現ルール
   - 数式は $...$ / $$...$$（KaTeX）で記載。
   - 図は Markdown の相対パスで埋め込み（例: ![](./materials/figure.png)）。
   - 重要語は太字、補足はイタリックで表現。
   - 参考文献は原文の引用形式を尊重しつつ DOI/URL を併記。

7) 最終出力（要求）
   - report.md（完全版）

"""

    return prompt


if __name__ == "__main__":
    mcp.run(transport="stdio")  # Default, so transport argument is optional
