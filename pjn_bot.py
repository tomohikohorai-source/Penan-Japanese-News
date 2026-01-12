import os
import datetime
import feedparser
import requests
import json
import time

# --- 設定 ---
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
# あなたの環境で確実に動作する最新モデル
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"

POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

# ニュースソース
RSS_URLS = ["https://www.thestar.com.my/rss/news/nation"]

def ask_ai(title, summary, link):
    prompt = f"以下の英語ニュースを、ペナン在住日本人向けに読みやすい日本語で翻訳・整形して。1行目は「ジャンル：〇〇」として。タイトル: {title}, 内容: {summary}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        # 無料枠を労わるため、実行前に少し待機
        time.sleep(10)
        response = requests.post(API_URL, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        
        if response.status_code == 200:
            content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            lines = content.strip().split('\n')
            genre = "暮らし" # デフォルト
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

<a href="{link}" target="_blank" rel="noopener noreferrer" class="source-link">🔗 参照元記事（英語）を確認する</a>
"""
        return None
    except:
        return None

# --- メイン実行 ---
print(f"PJN Bot 起動 (使用モデル: {MODEL_NAME})")

feed = feedparser.parse(RSS_URLS[0])
count = 0

for entry in feed.entries[:3]: # 毎朝3記事ずつ更新
    safe_title = "".join([c for c in entry.title if c.isalnum() or c==' '])[:30].strip().replace(" ", "_")
    filename = os.path.join(POSTS_DIR, f"{datetime.date.today()}-{safe_title}.md")
    
    if os.path.exists(filename): continue

    result = ask_ai(entry.title, entry.summary, entry.link)
    if result:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"✅ 保存完了: {filename}")
        count += 1
        # 連続リクエストを避けるため、1分間しっかり休む
        time.sleep(60)

print(f"本日の自動更新完了。作成記事数: {count}")
