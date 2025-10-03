#!/usr/bin/env bash
set -euo pipefail

# Python パッケージ（PDFまわり）
python -m pip install --upgrade pip
pip install -r requirements.txt


# Playwright のブラウザ（MCP が内部で利用）
npx --yes playwright install --with-deps
