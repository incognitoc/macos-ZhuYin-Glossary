# 🍎 macOS-ZhuYin-Glossary（macOS 原生注音加詞器）

解決 macOS 內建繁體中文「注音輸入法 (Zhuyin - Traditional)」經常**失憶、記不住常用選字與專有名詞**的痛點！

本工具能直接將常用詞彙寫入 macOS 原生注音底層的 `UserDictionary` (CoreData SQLite) 並賦予最高詞頻權重，同時提供**桌面圖形化 App** 與**滑鼠右鍵「反白即加」快速動作**。

## ✨ 功能特色
1. **🖱️ 隨處反白，右鍵秒加詞庫**：在任何軟體打完字後，直接反白選取文字 ➔ 按滑鼠右鍵 ➔ 點選 **「➕ 加入注音詞庫」** 即可一鍵鎖定。
2. **🔤 自動轉換注音 + 防破音字校正**：呼叫 macOS 原生 API 自動算出注音符號，遇到破音字可手動微調。
3. **📦 桌面獨立 `.app` 隨點隨用**：可常駐於 Dock 或透過 Spotlight 快速呼叫。
4. **💾 自動本地備份**：所有新增過的詞彙皆會自動備份於桌面 (`~/Desktop/Zhuyin_Custom_Words.txt`)。
5. **🗑️ 內建一鍵乾淨解除安裝 (Uninstall)**：App 視窗內建「🗑️ 解除安裝」按鈕，不留任何系統垃圾。

## 🚀 快速安裝方式

### 方式 A：終端機一行指令安裝
打開 macOS **終端機 (Terminal)**，貼上以下指令並按 Enter：

```bash
curl -fsSL https://raw.githubusercontent.com/incognitoc/macos-ZhuYin-Glossary/main/install.command | bash
```

### 方式 B：下載 ZIP 雙擊安裝
1. 點擊本頁面右上角的綠色 **Code** 按鈕 ➔ **Download ZIP** 並解壓縮。
2. 點兩下執行資料夾內的 **`install.command`** 即可自動完成安裝。

## 📄 License
MIT License
