#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

# デバッグ出力：アーキテクチャ確認
echo "Container architecture: $(uname -m)"

sudo rm -rf /var/lib/apt/lists/*
sudo mkdir -p /var/lib/apt/lists/partial

sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  ca-certificates curl fontconfig \
  fonts-noto fonts-noto-cjk \

# -------- generic tar.gz 方式で Prince インストール --------

# バージョンとアーキを指定
PRINCE_VER=16.1
ARCH="$(uname -m)"
# x86_64 環境なら以下、arm 系なら aarch64 に切り替え（必要なら調整）
if [ "$ARCH" = "x86_64" ]; then
  PR_ARCH="x86_64"
elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
  PR_ARCH="aarch64"
else
  echo "Unsupported architecture: $ARCH"
  exit 1
fi

TGZ_NAME="prince-${PRINCE_VER}-linux-generic-${PR_ARCH}.tar.gz"
TGZ_URL="https://www.princexml.com/download/${TGZ_NAME}"

# ダウンロード
echo "Downloading: $TGZ_URL"
curl -fsSL -o "/tmp/${TGZ_NAME}" "${TGZ_URL}"

# 解凍、インストール
cd /tmp
tar xzf "${TGZ_NAME}"
cd "prince-${PRINCE_VER}-linux-generic-${PR_ARCH}"

sudo ./install.sh <<EOF
/usr/local
EOF

# install.sh によって /usr/bin/prince や /usr/lib/prince 以下が構成されるはず

# クリーンアップ
cd /
rm -rf /tmp/prince-${PRINCE_VER}-linux-generic-${PR_ARCH} /tmp/${TGZ_NAME}

# 動作確認
prince --version

# -------- 既存の残り処理 --------

python -m pip install --upgrade pip
pip install -r /workspaces/PaperInterpreter/requirements.txt

npx --yes playwright install --with-deps
