#!/usr/bin/env bash
set -euo pipefail

# ====== PrinceXML の導入（Debian 12 / amd64）======
export DEBIAN_FRONTEND=noninteractive
apt-get update

# 文字化け対策で日本語フォントも入れておく（必要に応じて調整）
apt-get install -y --no-install-recommends \
  ca-certificates curl fontconfig \
  fonts-noto fonts-noto-cjk \
  # Prince の依存は .deb 側で解決されるが、fontconfig/CA だけ先に入れておく
  && rm -rf /var/lib/apt/lists/*

# Prince 16.1 の Debian 12 パッケージを取得してインストール
PRINCE_VER=16.1-1
PRINCE_DEB="/tmp/prince_${PRINCE_VER}_debian12_amd64.deb"
curl -fsSL -o "${PRINCE_DEB}" \
  "https://www.princexml.com/download/16/prince_${PRINCE_VER}_debian12_amd64.deb"
apt-get update
apt-get install -y "${PRINCE_DEB}" && rm -f "${PRINCE_DEB}"
# 動作確認（失敗時は set -e で止まる）
prince --version

# ====== (既存) Python パッケージ（PDFまわり）======
python -m pip install --upgrade pip
pip install -r requirements.txt

# ====== (既存) Playwright のブラウザ（MCP が内部で利用）======
npx --yes playwright install --with-deps
