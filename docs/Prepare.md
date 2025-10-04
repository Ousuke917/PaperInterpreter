# 事前準備

以下は、このプロジェクトを devcontainer / Docker 環境で利用する際に必要な事前準備の最小項目です。開発環境は [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) に定義されており、初回起動時に [.devcontainer/setup.sh](.devcontainer/setup.sh) が実行されて依存がインストールされます（[`requirements.txt`](requirements.txt) を参照）。

1. Docker Desktop のインストール（必須）
   - Docker Desktop がホスト上で稼働していることが必要です。VS Code から devcontainer を起動する前に Docker Desktop を起動してください。
   - Windows 用インストール手順（WSL2 の準備を含む）: https://docs.docker.com/desktop/install/windows-install/
   - macOS 用インストール手順（Intel / Apple Silicon 対応）: https://docs.docker.com/desktop/install/mac-install/
   - Windows の場合は WSL2 を有効にして適切な Linux ディストリビューションをインストールしておくと安定して動作します。WSL の導入手順: https://learn.microsoft.com/windows/wsl/install

2. VS Code と Dev Containers（任意だが推奨）
   - VS Code の Remote - Containers / Dev Containers 機能を用いると、リポジトリ内の devcontainer 設定で開発環境を簡単に構築できます。詳細は公式ドキュメントを参照してください: https://code.visualstudio.com/docs/remote/containers
   - devcontainer の設定は [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json) にあります。

3. ネットワークとディスク容量
   - 初回セットアップで Python パッケージのインストールや Playwright のブラウザセットアップが行われます（スクリプト: [.devcontainer/setup.sh](.devcontainer/setup.sh)）。十分なネットワーク帯域とディスク領域を確保してください。

4. 開発ツール（ホストに無くても devcontainer 内で揃いますが事前にインストールしておくと便利）
   - Git（ソース管理）
   - VS Code（開発用エディタ）
   - Docker Desktop（必須）
   - （任意）GitHub CLI gh: devcontainer 側でも利用可能です（参照: [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)）。

5. プロジェクト固有の依存
   - Python 依存は [.devcontainer/setup.sh](.devcontainer/setup.sh) が自動で pip インストールします（参照: [`requirements.txt`](requirements.txt)）。
   - Playwright ブラウザは初回セットアップでインストールされます（setup.sh 内の npx playwright インストール）。

6. 確認用コマンド（ホスト/コンテナ双方で確認可能）
   - Docker の動作確認: docker --version
   - Docker Desktop が起動しているかを GUI で確認（Windows/macOS）
   - VS Code でリポジトリを開き、「Reopen in Container」を実行するか、Remote-Containers 機能で devcontainer を起動してください。

7. セキュリティ・API キー等の取り扱い
   - 本リポジトリでは検索等に環境変数を使います（例: Google API）。API キーは `.env` 等で安全に管理してください（リポジトリに平文で置かないこと）。
   - 本プロジェクトでは Google Cloud の「Custom Search（Programmable Search Engine）」とその API（Custom Search JSON API）を利用しており、以下の手順でセットアップします。

     1. Google Cloud Console で Custom Search API を有効化  
        - API ライブラリ（Custom Search API）を有効にする:  
          https://console.cloud.google.com/apis/library/customsearch.googleapis.com

     2. API キーの取得  
        - Google Cloud の「認証情報 (Credentials)」から API キーを作成してください。作成した API キーは安全に管理し、`.env` などでコンテナ内に渡す運用にしてください。

     3. カスタム検索エンジン（CSE）の作成（cx の取得）  
        - Programmable Search Engine 管理画面で検索エンジンを作成し、検索対象やサイトを設定します。作成後に得られる「Search engine ID（cx）」を控えてください。  
          Programmable Search Engine: https://programmablesearchengine.google.com/about/
        - Custom Search API の利用方法（概要）: https://developers.google.com/custom-search/v1/overview

     4. 環境変数の設定（本リポジトリでの配置例）  
        - 本リポジトリの開発用サンプルでは [.github/.env](.github/.env) を参照するようにしており、`GOOGLE_API_KEY` と `GOOGLE_CSE_ID` を設定してください（実運用ではリポジトリに平文で置かないこと）。参照実装: [.github/.env](.github/.env)

     5. 実装の参照と注意点  
        - このリポジトリ内の検索ラッパー実装は [`tools.GoogleSearch.getSearchResponse`](tools/GoogleSearch.py) にあります。関数は `GOOGLE_API_KEY` と `GOOGLE_CSE_ID` を使って検索を実行し、結果の URL リストを返します（実装: [tools/GoogleSearch.py](tools/GoogleSearch.py)）。  
        - API 利用にはクォータと課金の可能性があるため、利用量と課金設定を Google Cloud Console で確認してください。

   - なお、ローカルや CI に API キーを渡す場合は、`.env`／環境変数やシークレットマネージャ等を使って安全に取り扱ってください。
   - 参考: Custom Search のチュートリアルとドキュメント  
     - https://developers.google.com/custom-search/docs/tutorial/introduction  
     - https://developers.google.com/custom-search/v1/overview

参考:
- リポジトリのトップ README: [README.md](README.md)
- devcontainer 設定: [.devcontainer/devcontainer.json](.devcontainer/devcontainer.json)
- 初期セットアップスクリプト: [.devcontainer/setup.sh](.devcontainer/setup.sh)
- Python 依存リスト: [requirements.txt](requirements.txt)
