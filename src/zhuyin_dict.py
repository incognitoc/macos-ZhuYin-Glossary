#!/usr/bin/env python3
import os
import sys
import sqlite3
import glob
import shutil
import subprocess
from datetime import datetime

SEARCH_PATHS = [
    os.path.expanduser("~/Library/Dictionaries/CoreDataUbiquitySupport/**/UserDictionary*.db"),
    os.path.expanduser("~/Library/Dictionaries/**/UserDictionary*.db"),
    os.path.expanduser("~/Library/Application Support/com.apple.inputmethod.TCIM/**/UserDictionary*.db"),
    os.path.expanduser("~/Library/Containers/com.apple.inputmethod.TCIM*/Data/Library/**/*.sqlite*")
]

LOCAL_BACKUP = os.path.expanduser("~/Desktop/Zhuyin_Custom_Words.txt")
SERVICE_WORKFLOW = os.path.expanduser("~/Library/Services/➕ 加入注音詞庫.workflow")

def get_bopomofo_spaced(text):
    jxa_code = f"""
    ObjC.import('Foundation');
    var str = $.NSMutableString.stringWithString({repr(text)});
    $.CFStringTransform(str, null, $.kCFStringTransformMandarinLatin, false);
    $.CFStringTransform(str, null, $.kCFStringTransformLatinBopomofo, false);
    str.js;
    """
    try:
        res = subprocess.run(["osascript", "-l", "JavaScript", "-e", jxa_code], capture_output=True, text=True, timeout=3)
        return " ".join(res.stdout.strip().split())
    except Exception:
        return ""

def find_tcim_db():
    found = []
    for pattern in SEARCH_PATHS:
        found.extend(glob.glob(pattern, recursive=True))
    found = [f for f in found if os.path.isfile(f)]
    found.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return found[0] if found else None

def inject_into_tcim_db(db_path, phrase, reading):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'Z%ENTRY%';")
        row = cur.fetchone()
        if not row:
            conn.close()
            return False, "找不到標準 CoreData 詞庫資料表"
        
        table = row[0]
        cur.execute(f"PRAGMA table_info({table});")
        cols = [c[1] for c in cur.fetchall()]
        apple_ts = datetime.now().timestamp() - 978307200
        
        if "ZPHRASE" in cols and "ZREADING" in cols:
            cur.execute(f"SELECT Z_PK FROM {table} WHERE ZPHRASE = ? AND ZREADING = ?", (phrase, reading))
            if cur.fetchone():
                conn.close()
                return True, "詞庫中已存在此詞彙（已確保權重）"
            
            cur.execute(f"SELECT MAX(Z_PK) FROM {table}")
            max_pk = cur.fetchone()[0] or 0
            new_pk = max_pk + 1
            
            insert_cols = ["Z_PK", "Z_ENT", "Z_OPT", "ZPHRASE", "ZREADING"]
            insert_vals = [new_pk, 1, 1, phrase, reading]
            if "ZTIMESTAMP" in cols:
                insert_cols.append("ZTIMESTAMP")
                insert_vals.append(apple_ts)
            if "ZFREQUENCY" in cols:
                insert_cols.append("ZFREQUENCY")
                insert_vals.append(999)
                
            placeholders = ",".join(["?"] * len(insert_cols))
            col_names = ",".join(insert_cols)
            cur.execute(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})", insert_vals)
            cur.execute("UPDATE Z_PRIMARYKEY SET Z_MAX = ? WHERE Z_ENT = 1", (new_pk,))
            conn.commit()
            conn.close()
            return True, f"已直接寫入原生注音底層詞庫 ({os.path.basename(db_path)})"
        conn.close()
        return False, "資料庫結構不同"
    except Exception as e:
        return False, str(e)

def gui_alert(title, message):
    script = f'Tell application "System Events" to display alert "{title}" message "{message}" as informational'
    subprocess.run(["osascript", "-e", script])

def run_uninstall():
    """執行自我解除安裝程序（包含右鍵選單服務）"""
    script = (
        'Tell application "System Events" to display dialog '
        '"確定要解除安裝「注音加詞器」與「右鍵選單服務」嗎？\\n\\n這將會移除：\\n• 右鍵選單：➕ 加入注音詞庫.workflow\\n• 桌面與應用程式中的 注音加詞器.app\\n• 家目錄下的背景腳本 (zhuyin_dict.py / mac_vocab.py)\\n\\n（註：已經寫入 macOS 系統底層的字詞記憶不會受影響）" '
        'with title "🗑️ 解除安裝確認" buttons {"取消", "保留桌面備份並移除", "全部徹底刪除"} default button "取消"'
    )
    res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if res.returncode != 0 or "取消" in res.stdout:
        sys.exit(0)
        
    delete_backups = "全部徹底刪除" in res.stdout
    
    targets = [
        SERVICE_WORKFLOW,
        os.path.expanduser("~/Desktop/注音加詞器.app"),
        "/Applications/注音加詞器.app",
        os.path.expanduser("~/Applications/注音加詞器.app"),
        os.path.expanduser("~/zhuyin_dict.py"),
        os.path.expanduser("~/mac_vocab.py")
    ]
    
    if delete_backups:
        targets.extend([
            LOCAL_BACKUP,
            os.path.expanduser("~/Desktop/MyCustomTextSubstitutions.plist"),
            os.path.expanduser("~/.custom_mac_vocab_backup.txt")
        ])
        
    removed = []
    for path in targets:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                removed.append(os.path.basename(path))
            except Exception:
                pass
                
    # 重新整理 macOS 右鍵服務快取
    subprocess.run(["/System/Library/CoreServices/pbs", "-flush"], stderr=subprocess.DEVNULL)
    
    summary = "\\n• ".join(removed) if removed else "無殘留檔案"
    gui_alert("✅ 解除安裝完成", f"已成功從您的 Mac 清除以下項目：\\n• {summary}")
    sys.exit(0)

def main():
    # 判斷是否從「右鍵選單反白文字」直接傳入參數
    selected_text = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else ""
    
    if selected_text:
        phrase = selected_text
    else:
        script = (
            'Tell application "System Events" to display dialog '
            '"請輸入你想讓 Mac 永遠記住的詞彙（或直接在任何地方反白文字按右鍵呼叫）：" '
            'default answer "" with title "➕ 新增 macOS 原生注音詞彙" '
            'buttons {"🗑️ 解除安裝", "取消", "下一步"} default button "下一步" cancel button "取消"'
        )
        res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if res.returncode != 0:
            sys.exit(0)
            
        out = res.stdout.strip()
        if "button returned:🗑️ 解除安裝" in out:
            run_uninstall()
            return
            
        phrase = out.split("text returned:")[1].strip() if "text returned:" in out else ""
        if not phrase:
            return
        
    # 直接跳出注音確認框（防破音字）
    auto_reading = get_bopomofo_spaced(phrase)
    script2 = (
        f'Tell application "System Events" to display dialog '
        f'"已擷取詞彙：【{phrase}】\\n系統自動轉換注音如下（若有破音字可直接修改，字與字之間請留一個空白）：" '
        f'default answer "{auto_reading}" with title "🔤 確認注音讀音（防破音字）" '
        f'buttons {{"🗑️ 解除安裝", "取消", "確認新增"}} default button "確認新增" cancel button "取消"'
    )
    res2 = subprocess.run(["osascript", "-e", script2], capture_output=True, text=True)
    if res2.returncode != 0:
        sys.exit(0)
        
    out2 = res2.stdout.strip()
    if "button returned:🗑️ 解除安裝" in out2:
        run_uninstall()
        return
        
    reading = out2.split("text returned:")[1].strip() if "text returned:" in out2 else ""
    if not reading:
        return

    db_path = find_tcim_db()
    db_status = "未偵測到初始 DB（請先在打字時用 Shift+左鍵 技巧建立第一個詞以初始化資料庫）"
    if db_path:
        ok, msg = inject_into_tcim_db(db_path, phrase, reading)
        db_status = msg

    with open(LOCAL_BACKUP, "a", encoding="utf-8") as f:
        f.write(f"{phrase}\t{reading}\n")

    subprocess.run(["killall", "TCIM_Extension", "ChineseIM", "cfprefsd"], stderr=subprocess.DEVNULL)
    gui_alert("✅ 詞庫更新完成！", f"詞彙：{phrase}\\n注音：{reading}\\n\\n狀態：{db_status}\\n備份已存於桌面：Zhuyin_Custom_Words.txt")

if __name__ == "__main__":
    main()
