#!/bin/bash
set -e
echo "🍎 正在安裝 macOS 原生注音加詞器 (ZhuYin Glossary)..."

INSTALL_DIR="$HOME/.macos_zhuyin_glossary"
mkdir -p "$INSTALL_DIR"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/src/zhuyin_dict.py" ]; then
    cp "$SCRIPT_DIR/src/zhuyin_dict.py" "$INSTALL_DIR/zhuyin_dict.py"
    cp "$SCRIPT_DIR/src/zhuyin_dict.py" "$HOME/zhuyin_dict.py"
else
    curl -fsSL "https://raw.githubusercontent.com/incognitoc/macos-ZhuYin-Glossary/main/src/zhuyin_dict.py" -o "$HOME/zhuyin_dict.py"
    cp "$HOME/zhuyin_dict.py" "$INSTALL_DIR/zhuyin_dict.py"
fi
chmod +x "$HOME/zhuyin_dict.py" "$INSTALL_DIR/zhuyin_dict.py"

osacompile -o "$HOME/Desktop/注音加詞器.app" -e 'do shell script "export LANG=zh_TW.UTF-8; /usr/bin/python3 ~/zhuyin_dict.py > /dev/null 2>&1 &"'
cp -R "$HOME/Desktop/注音加詞器.app" "/Applications/注音加詞器.app" 2>/dev/null || true

echo "✅ 安裝完成！桌面與應用程式資料夾已建立【注音加詞器.app】"
