import os
import datetime
import feedparser
import requests
import json
import time

# --- 設定 ---
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# 複数のモデルを順番に試す（1.5-flash が一番制限が緩いので、404覚悟でもう一度試します）
MODELS = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"]

POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

RSS_URL = "https://www.thestar.com.my/rss/news/nation"

def ask_ai(title, summary, link):
    print(f"AI翻訳を開始します: {title}")
    
    prompt = f"以下の英語ニュースを日本語で翻訳して。タイトル: {title}, 内容: {summary}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for model_name in MODELS:
        print(f"モデル {model_name} で接続テスト中...")
        url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={API_KEY}"
        
        try:
            # 実行前に20秒待機（バースト防止）
            time.sleep(20)
            response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
            
            if response.status_code == 200:
                data = response.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"✅ {model_name} で翻訳成功！")
                return content
            else:
                print(f"   -> {model_name} は失敗 (Code: {response.status_code})")
                continue
        except Exception as e:
            print(f"   -> 接続エラー: {e}")
            continue
    return None

# --- メイン実行 ---
print("--- PJN 復旧モード起動 ---")

feed = feedparser.parse(RSS_URL)
if len(feed.entries) > 0:
    entry = feed.entries[0] # 【重要】まずは「1件だけ」試します
    
    result_text = ask_ai(entry.title, entry.summary, entry.link)
    
    if result_text:
        filename = os.path.join(POSTS_DIR, f"{datetime.date.today()}-news.md")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"""---
title: "{entry.title}"
date: "{datetime.date.today()}"
category: "重要"
---
<div class="genre-label">ジャンル：重要</div>
<h3>【内容（全文翻訳）】</h3>

{result_text}

<a href="{entry.link}" target="_blank" rel="noopener noreferrer" class="source-link">🔗 参照元記事を確認する</a>
""")
        print(f"✅ 記事を保存しました: {filename}")
    else:
        print("❌ すべてのモデルで制限がかかっています。数時間あける必要があります。")

print("--- 処理終了 ---")
