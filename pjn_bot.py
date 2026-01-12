import os
import datetime
import feedparser
import requests
import json
import time

# --- 設定 ---
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MODEL_NAME = "gemini-2.0-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"

POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

# ニュースソース（まずは1つに絞って確実に動かします）
RSS_URLS = ["https://www.thestar.com.my/rss/news/nation"]

def ask_ai(title, summary, link):
    print(f"AI翻訳中: {title}")
    
    prompt = f"""
    あなたはペナン在住日本人向けのニュース編集長です。
    以下の英語ニュースを、子育て世帯や母子留学生が読みやすい日本語に全文翻訳してください。
    
    【ルール】
    ・タイトルは「【ジャンル】タイトル」の形式にする。
    ・内容は原文に忠実に、かつ読みやすく改行を入れる。
    ・Markdown形式で出力する。

    タイトル: {title}
    内容: {summary}
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            data = response.json()
            translated_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return f"""---
title: "{title}"
date: "{datetime.date.today()}"
category: "ニュース"
---
<div class="genre-label">ジャンル：ニュース</div>
<h3>【内容（全文翻訳）】</h3>

{translated_text}

<a href="{link}" class="source-link">🔗 参照元記事を確認する</a>
"""
        elif response.status_code == 429:
            print("❌ 速度制限(429)がかかりました。少し待ち時間を増やしてください。")
            return None
        else:
            print(f"❌ APIエラー: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return None

# --- メイン処理 ---
print(f"PJN Bot 起動中... 使用モデル: {MODEL_NAME}")

feed = feedparser.parse(RSS_URLS[0])
print(f"ニュース取得: {len(feed.entries)}件見つかりました。")

count = 0
for entry in feed.entries:
    if count >= 3: # まずは3記事で確実に成功させます
        break
    
    # 安全なファイル名の作成
    safe_title = "".join([c for c in entry.title if c.isalnum() or c==' '])[:30].strip().replace(" ", "_")
    filename = os.path.join(POSTS_DIR, f"{datetime.date.today()}-{safe_title}.md")
    
    if os.path.exists(filename):
        continue

    result = ask_ai(entry.title, entry.summary, entry.link)
    
    if result:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"✅ 保存完了: {filename}")
        count += 1
        print("制限回避のため、35秒間待機します...")
        time.sleep(35) # 35秒待機（ここが重要です）

print(f"本日の更新作業完了。{count}件の記事を作成しました。")
