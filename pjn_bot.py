import os
import datetime
import feedparser
import requests
import json
import time

# --- 設定 ---
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"

POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

# ブラウザになりすますためのヘッダー（ブロック対策）
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# ニュースソース（複数を予備として持つ）
RSS_URLS = [
    "https://www.thestar.com.my/rss/news/nation",
    "https://www.thestar.com.my/rss/metro/community",
    "https://www.bernama.com/en/rss/news.php?cat=ge"
]

def ask_ai(title, summary, link):
    print(f"AI翻訳中: {title}")
    prompt = f"以下の英語ニュースを、ペナン在住日本人向けに読みやすい日本語で翻訳・整形して。1行目は「ジャンル：〇〇」として（グルメ、重要、暮らし、おでかけ、教育、エンタメ、お得 のいずれか）。タイトル: {title}, 内容: {summary}"
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        # 無料枠制限を避けるための10秒待機
        time.sleep(10)
        response = requests.post(API_URL, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            lines = content.strip().split('\n')
            
            # ジャンルの抽出
            genre = "暮らし"
            if "ジャンル：" in lines[0]:
                genre = lines[0].replace("ジャンル：", "").strip()
                body = "\n".join(lines[1:])
            else:
                body = content

            return f"""---
title: "{title}"
date: "{datetime.date.today()}"
category: "{genre}"
---
<div class="genre-label">ジャンル：{genre}</div>
<h3>【内容】</h3>

{body}

<a href="{link}" target="_blank" rel="noopener noreferrer" class="source-link">🔗 参照元記事を確認する</a>
"""
        else:
            print(f"❌ AIエラー (Code {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ 通信エラー: {e}")
        return None

# --- メイン実行 ---
print(f"PJN Bot 起動 (モデル: {MODEL_NAME})")
count = 0

for url in RSS_URLS:
    if count >= 3: break # 1日に合計3記事まで
    
    try:
        print(f"ニュース取得中: {url}")
        # 直接 feedparser を使わず、requests で取得してから解析する（ブロック対策）
        response = requests.get(url, headers=HEADERS, timeout=20)
        feed = feedparser.parse(response.content)
        
        print(f"取得成功: {len(feed.entries)}件のニュースを発見")
        
        for entry in feed.entries:
            if count >= 3: break
            
            safe_title = "".join([c for c in entry.title if c.isalnum() or c==' '])[:30].strip().replace(" ", "_")
            filename = os.path.join(POSTS_DIR, f"{datetime.date.today()}-{safe_title}.md")
            
            if os.path.exists(filename): continue

            result = ask_ai(entry.title, entry.summary, entry.link)
            if result:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(result)
                print(f"✅ 保存完了: {filename}")
                count += 1
                time.sleep(60) # 1分待機
                
    except Exception as e:
        print(f"❌ 取得エラー ({url}): {e}")

print(f"本日の自動更新完了。作成記事数: {count}")
