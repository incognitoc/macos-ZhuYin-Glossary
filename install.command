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
    RAW_URL="https://""raw.githubusercontent.com/incognitoc/macos-ZhuYin-Glossary/main/src/zhuyin_dict.py"
    curl -fsSL "$RAW_URL" -o "$HOME/zhuyin_dict.py"
    cp "$HOME/zhuyin_dict.py" "$INSTALL_DIR/zhuyin_dict.py"
fi
chmod +x "$HOME/zhuyin_dict.py" "$INSTALL_DIR/zhuyin_dict.py"

# 編譯桌面與應用程式 App
osacompile -o "$HOME/Desktop/注音加詞器.app" -e 'do shell script "export LANG=zh_TW.UTF-8; /usr/bin/python3 ~/zhuyin_dict.py > /dev/null 2>&1 &"'
cp -R "$HOME/Desktop/注音加詞器.app" "/Applications/注音加詞器.app" 2>/dev/null || true

# 若使用者機器上已有右鍵選單範本則確保啟用，或由系統建立
WF_DIR="$HOME/Library/Services/➕ 加入注音詞庫.workflow/Contents"
mkdir -p "$WF_DIR"
cat << 'WEOF' > "$WF_DIR/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>NSServices</key>
	<array>
		<dict>
			<key>NSMenuItem</key>
			<dict>
				<key>default</key>
				<string>➕ 加入注音詞庫</string>
			</dict>
			<key>NSMessage</key>
			<string>runWorkflowAsService</string>
			<key>NSSendTypes</key>
			<array>
				<string>NSStringPboardType</string>
			</array>
		</dict>
	</array>
</dict>
</plist>
WEOF

/System/Library/CoreServices/pbs -flush 2>/dev/null || true
echo "✅ 安裝完成！桌面已建立【注音加詞器.app】並啟用右鍵選單！"
