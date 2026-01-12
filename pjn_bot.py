import os
import datetime
import feedparser
import requests
import json
import time

# --- 設定 ---
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# あなたの環境で確実に動作するモデル名
MODEL_NAME = "gemini-2.0-flash"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"

POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

# ニュースソース（ペナンとマレーシア全国）
RSS_URLS = [
    "https://www.thestar.com.my/rss/news/nation",
    "https://www.thestar.com.my/rss/metro/community"
]

def ask_ai(title, summary, link):
    print(f"AI翻訳中: {title}")
    
    # 子育て世帯や母子留学生を意識した翻訳指示
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

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        data = response.json()
        
        if response.status_code == 200:
            translated_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # ジャンルを特定（簡易的）
            category = "生活"
            if "school" in title.lower() or "education" in title.lower():
                category = "教育"
            elif "important" in title.lower() or "alert" in title.lower():
                category = "重要"

            # 最終的なMarkdownを組み立て
            return f"""---
title: "{title}"
date: "{datetime.date.today()}"
category: "{category}"
---
<div class="genre-label">ジャンル：{category}</div>
<h3>【内容（全文翻訳）】</h3>

{translated_text}

<a href="{link}" class="source-link">🔗 参照元記事を確認する</a>
"""
        else:
            print(f"❌ APIエラー: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return None

# --- メイン処理 ---
print(f"PJN Bot 起動中... 使用モデル: {MODEL_NAME}")

for url in RSS_URLS:
    feed = feedparser.parse(url)
    print(f"ニュース取得: {url} (記事数: {len(feed.entries)})")
    
    count = 0
    for entry in feed.entries:
        if count >= 5: break # 1ソースにつき最大5件
        
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
            time.sleep(2) # API制限を考慮

print("本日の更新作業がすべて完了しました。")
