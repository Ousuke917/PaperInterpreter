# PaperInterpreter
MCP toolset for interpreting research papers with GitHub Copilot Agent

# 機能の概要

PaperInterpreter は、研究論文 PDF を自動で解析し、Markdown レポートと図像を生成してエージェント／MCP ツールと連携するためのツール群です。github copilot agentと連携させて利用することによって、材料科学やAIに関する論文内容を基礎知識レベルをもつ人に分かりやすく伝えるためのレポートを作成します。主要な機能は以下の通りです。

- PDF → Markdown 変換（本文テキストと図像の抽出）
  - 実処理は [`tools.PDFTools.pdf_to_markdown`](tools/PDFTools.py)（実装: [tools/PDFTools.py](tools/PDFTools.py)）が行います。  
  - MCP ツールとしては [`InterpreterMCP.pdf_to_markdown_tool`](InterpreterMCP.py)（定義: [InterpreterMCP.py](InterpreterMCP.py)）を公開しています。

- Web 補助検索
  - 必要に応じて関連情報を収集するためのラッパーとして [`tools.GoogleSearch.getSearchResponse`](tools/GoogleSearch.py)（実装: [tools/GoogleSearch.py](tools/GoogleSearch.py)）を利用できます。

- MCP サーバとしての公開
  - `InterpreterMCP.py`（[InterpreterMCP.py](InterpreterMCP.py)）は FastMCP を使ってツール群とプロンプト（[`InterpreterMCP.MatSci_Interpreter_prompt`](InterpreterMCP.py)）を公開します。devcontainer 設定で常駐させてエージェントから利用できます（設定: [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)）。

- 出力フォーマットとワークフロー
  - 変換結果は指定した Markdown と画像ディレクトリ（デフォルト: `materials`）に出力され、変換関数は返り値として `{"md_text": md_text, "dest_dir": str(dest_dir)}` を返します（参照: [`tools.PDFTools.pdf_to_markdown`](tools/PDFTools.py)）。

- 開発／実行環境（devcontainer）
  - devcontainer により依存の自動インストールや Playwright ブラウザの導入が行われます（スクリプト: [.devcontainer/setup.sh](.devcontainer/setup.sh)、設定: [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)）。

# システム概要図-Ver1.0
- github copilot agentと連携した際のシステムは以下のようになっております。
- 現在はweb検索機能が不十分であります。将来的にはdeepresearchのような機能を追加して、より高度な解析を行えるようにする予定です。

# 使い方（簡易）

1. 依存をインストールして devcontainer を起動済みであることを確認してください（devcontainer の初期化は [.devcontainer/setup.sh](.devcontainer/setup.sh) が行います）。
2. ローカルで単発実行する例（Python から直接呼び出す）:
   - 例: `tools/PDFTools.pdf_to_markdown` を直接使う
     - Python REPL やスクリプトで:
       - `from tools.PDFTools import pdf_to_markdown`
       - `pdf_to_markdown("PhysRevB_68_245409/PhysRevB.68.245409.pdf", "report.md")`
     - 実装参照: [`tools.PDFTools.pdf_to_markdown`](tools/PDFTools.py)
3. MCP 経由で使う場合:
   - `InterpreterMCP.py`（[InterpreterMCP.py](InterpreterMCP.py)）を devcontainer の MCP サーバとして起動すると、エージェントから [`InterpreterMCP.pdf_to_markdown_tool`](InterpreterMCP.py) と [`InterpreterMCP.MatSci_Interpreter_prompt`](InterpreterMCP.py) を経由して処理できます。
4. 補助的に Google 検索を使う場合:
   - [`tools.GoogleSearch.getSearchResponse`](tools/GoogleSearch.py) を参照して、検索結果の URL を取得し追加情報として利用できます（実装: [tools/GoogleSearch.py](tools/GoogleSearch.py)）。
5. 出力場所と画像パスに注意:
   - `pdf_to_markdown` は元 PDF をタイトル名で安全化したディレクトリ配下に移動して処理します。出力された `report.md` から画像を参照する際は相対パスで挿入してください。
6. 理論的な表記（参考）
   - 数式は KaTeX 形式で README 等に含められます。
   - 例: 
        ```text
        $ \gamma = \dfrac{G(T,p,\{n_x\}) - \sum_x n_x \mu_x(T,p_x)}{A} $。
        ```
        ➡️ &emsp; $ \gamma = \dfrac{G(T,p,\{n_x\}) - \sum_x n_x \mu_x(T,p_x)}{A} $

# 参照
- 実装ファイル:
  - [InterpreterMCP.py](InterpreterMCP.py)（MCP ツール定義・プロンプト）
  - [tools/PDFTools.py](tools/PDFTools.py)（[`tools.PDFTools.pdf_to_markdown`](tools/PDFTools.py) 実装）
  - [tools/GoogleSearch.py](tools/GoogleSearch.py)（[`tools.GoogleSearch.getSearchResponse`](tools/GoogleSearch.py) 実装）
  - [PhysRevB_68_245409/report.md](PhysRevB_68_245409/report.md)（生成済みレポート例）
  - [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)（devcontainer 設定）  
  - [.devcontainer/setup.sh](.devcontainer/setup.sh)（初期セットアップスクリプト）

