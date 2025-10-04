from fastmcp import FastMCP
from tools.PDFTools import pdf_to_markdown
from tools.GoogleSearch import getSearchResponse

# Create a server instance
mcp = FastMCP(name="Interpreter Assistant Server")


@mcp.tool(name="PDF_to_Markdown_Converter", description="Convert a PDF file to Markdown format, extracting text and images.")
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


@mcp.tool(name="Google_Search", description="Perform a Google search and return a list of URLs.")
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

    prompt = f"""あなたは材料科学や量子力学、群論、固体物理学、統計力学などの学問の最先端の知見を有する優秀な大学教授です。
こちらの論文PDFファイル{pdf_path}について、以下の知識レベルをもつ学生にも理解できるように、具体的かつ分かりやすい丁寧な解説レポートを作成してください。

### 学生の知識レベル
- 材料科学、量子力学、群論、固体物理学、統計力学などに関する基礎的な知識は有しているが、専門的な内容については理解が浅い。
- 大学院に入りたての学生

### レポートの要件
- report.mdという名前のMarkdownファイルで出力してください。
- 論文内に数式が登場した場合は、その数式をmarkdown形式で正確に記述して詳細な解説を加えてください。
- 論文内に図が登場した場合は、その図を適切な場所に挿入し、図の説明を加えてください。
- 論文の内容を要約するだけでなく、必要に応じて学生が理解しやすいように具体例や比喩を用いて説明してください。
- 専門用語が登場した場合は、その用語の意味を簡潔に説明してください。

### 作成順序
1. 与えられたPDFファイルを読み込み、その内容をできる限り正確に理解する。
2.  InterpreterMCP の PDF_to_Markdown_Converter を使用して、PDFファイルをMarkdown形式に変換し、テキストと画像を抽出する。
    - ただし、こちらで出力されるテキストの方には、数式や画像の情報が欠落している可能性が高いので、こちらは図などの画像だデータを取り出すための用途に留めること。
    - こちらのツールを実行すると、md_textとdest_dirが得られる。md_textは変換されたMarkdownの文字列、dest_dirは元のPDFを移動した先のディレクトリのパスである。
    - 抽出画像もdest_dir内のmaterialsというディレクトリに保存される。
3. 1番の手順で理解した内容をもとに、学生の知識レベルに合わせた解説レポートを作成する。
    - レポート内で論文と同じ図を使用する場合は、pdf_to_markdown_toolで抽出した画像を適切な場所に挿入する。
    - 画像を挿入する際はreport.mdからの相対パスを指定しないと画像が表示されないので注意すること。
    - レポートを作成する上で追加情報が必要であると判断した場合は、Google_Search を使用して関連urlを収集し、それらのurlに fetch mcp や
    playwright mcpなどのツールを使って内容を取得し、レポートに反映させること。
4. 内容の正確性と分かりやすさを確認し、必要に応じて修正を加える。
5. レポートをreport.mdという名前のMarkdownファイルでdest_dir内に保存する。

"""

    return prompt


if __name__ == "__main__":
    mcp.run(transport="stdio")  # Default, so transport argument is optional
