from fastmcp import FastMCP
from tools.PDFTools import pdf_to_markdown
from tools.GoogleSearch import getSearchResponse

# Create a server instance
mcp = FastMCP(name="Interpreter Assistant Server")


@mcp.tool(name="PDF to Markdown Converter", description="Convert a PDF file to Markdown format, extracting text and images.")
def pdf_to_markdown_tool(
    pdf_path: str,
    md_output_path: str = "output.md",
    write_images: bool = True,
    image_dir: str = 'materials',
    image_format: str = "png",
    page_chunks: bool = False,
) -> dict:
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

    # Call the imported pdf_to_markdown function (from tools.PDFTools) which was shadowed before.
    md_results = pdf_to_markdown(
        pdf_path=pdf_path,
        md_output_path=md_output_path,
        write_images=write_images,
        image_dir=image_dir,
        image_format=image_format,
        page_chunks=page_chunks,
    )

    return md_results


@mcp.tool(name="Google Search", description="Perform a Google search and return a list of URLs.")
def google_search_tool(
    keyword: str,
    DATA_DIR: str
) -> list[str]:
    """
    Perform a Google search and return a list of URLs.

    Args:
        keyword (str): The search keyword.
        DATA_DIR (str, optional): Directory to save the search response. Defaults to "./data".
        GOOGLE_API_KEY (str, optional): Google API key. If None, will use environment variable. Defaults to None.
        CUSTOM_SEARCH_ENGINE_ID (str, optional): Custom Search Engine ID. If None, will use environment variable. Defaults to None.

    Returns:
        list[str]: A list of URLs from the search results.
    """
    urls = getSearchResponse(
        keyword=keyword,
        DATA_DIR=DATA_DIR,
    )
    return urls


@mcp.prompt(name="PDF to Markdown Conversion Prompt", description="Convert the provided PDF file to Markdown format, extracting text and images. Save the output to the specified path.")
def MatSci_Interpreter_prompt(pdf_path: str) -> str:

    prompt = f"""あなたは材料科学（Materials Science）の専門家チームを代表し、固体物理、結晶学、量子力学、グループ理論など周辺知見にも明るい大学教授ペルソナです。以下の条件で、与えられた論文 PDF（パス: {pdf_path}）に関して、
利用者の知識レベルに合わせた分かりやすく具体的なreport（Markdown形式、ファイル名: report.md想定）を作成してください。

---

### 出力形式と読者

- 出力は **Markdown 形式（report.md 想定）**  
- YAML ヘッダ（title, authors, source_pdf, generated_by, audience, summary_length）を先頭に含める  
- レポートは論文の内容を正確に反映しつつ、読者レベルに合わせた分かりやすい内容にすること
- 読者層：大学院 1 年生レベル。材料科学や量子力学の基礎は理解しているが、専門外の分野に関しては初心者レベル。 

---

### レポート構成（推奨セクション順）

1. Title / Authors / Citation  
2. TL;DR（3行）  
3. 要点サマリー（箇条書き）  
4-10. Interpreter mcp内のpdf_to_markdown_toolの出力 md_text の各セクション毎に、以下を含む詳細解説を順番に行う。  
   - セクションタイトル  
   - そのセクション内容を大学教授らしく、自身の担当生徒に具体的にかつ分かりやすく説明するように解説
   - 解説における重要なポイントには必ず引用元（ページ番号）を明記  
   - 数式は可能な限り `$...$` / `$$...$$` 形式で再現  
   - 解説内では図をしっかりと表示すること。図は `![](相対パス)` で Markdown に埋め込み。この際に見やすさなども考慮して図の配置を最適化すること。
   - 誤解を招く記述は避け、不確かさには明記（「〜と思われる」など）    
   - 節ごとに見直しを行い、統一語彙・表記・単位で整える  
   - 必要に応じて元 PDF を参照し、数式・表などがうまく変換されていない場合に補完する  
11. 推奨アクション  
12. 参考文献  
13. Appendix：元 Markdown 抜粋、図ファイル一覧（相対パス）

---

### 動作戦略（Agent に期待するツール利用手順）

1. **PDF → Markdown 変換**  
   - 最初にInterpreter mcp内のpdf_to_markdown_toolを呼び出す  
   - その出力 `md_text` を読み込む  
   - ただし数式・表などがうまく変換されていない可能性を念頭に置き、必要に応じて元 PDF を参照する。
   - 最終出力は `md_text` と同じくらいもしくはそれ以上の文量で出力されることを想定。  

2. **検索経由情報の取得**  
   - 原著だけで情報が足りないと判断したとき、Interpreter mcp内の google_search_tool を呼び出す
   - この際に必要となる入力変数の'DATA_DIR'は `pdf_to_markdown_tool` の出力 `dest_dir` を利用する。
   - この検索ツールは **URL リスト**を返すもの。 

3. **取得 URL の内容取得**  
   - 検索で得た URL に対して、**#fetch**（静的ページ）または **#playwright**（動的ページ）を使って本文または関連データを取得  
   - 取得後、要点を抜き出してレポート内容に統合  

4. **情報統合と最終出力**  
   - PDF 由来内容と検索由来内容を混ぜて、レポート構成に従いまとめる  
   - report.mdは `tools.PDFTools.pdf_to_markdown()` の出力 `dest_dir` に保存する。

5. **探索制御ルール**  
   - 検索回数やフェッチ数には上限を設ける（例：検索は最大 5 回、URL フェッチは上位 10 件まで）  
   - 同一 URL の重複フェッチを避ける  
   - 情報が十分と判断したら無理に検索を続けず停止  

---

### 品質チェック &注意点

- 専門用語には定義を必ず添える  
- データ・式・グラフには常に出典を付ける  
- 誤解を招く記述は避け、不確かさには明記（「〜と思われる」など）  
- コードや計算モデルが論文にあれば簡易検算や説明を添える  
- 節ごとに見直しを行い、統一語彙・表記・単位で整える  

---


"""

    return prompt


if __name__ == "__main__":
    mcp.run(transport="stdio")  # Default, so transport argument is optional
