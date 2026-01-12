import os
import datetime
import feedparser
import requests
import json
import time

# --- 設定 ---
API_KEY = os.environ["GEMINI_API_KEY"]
# 確実に存在するモデル名とAPIバージョンを指定
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

RSS_URLS = [
    "https://www.thestar.com.my/rss/news/nation",
    "https://www.thestar.com.my/rss/metro/community"
]

def ask_ai(title, summary, link):
    print(f"AI翻訳中: {title}")
    
    prompt = f"""
    あなたはペナン在住日本人向けのニュース編集長です。
    以下の英語ニュースを、子育て世帯や母子留学生が読みやすい日本語に全文翻訳・整形してください。

    タイトル: {title}
    内容: {summary}

    【出力ルール】
    1. 冒頭に「ジャンル：〇〇」を明記
    2. タイトルは「【ジャンル】タイトル」の形式に。
    3. 本文は3-4行ごとに改行を入れ、読みやすく。
    4. 最後に「🔗 参照元記事を確認する」というリンクをつける。
    5. 出力は以下のMarkdown形式で。
    ---
    title: "【ジャンル】タイトル"
    date: "{datetime.date.today()}"
    category: "ニュース"
    ---
    <div class="genre-label">ジャンル：ニュース</div>
    <h3>【内容（全文翻訳）】</h3>
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
        
        # エラーチェック
        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"APIエラー: {data}")
            return None
    except Exception as e:
        print(f"接続エラー: {e}")
        return None

# --- メイン処理 ---
print("ニュース取得開始...")
articles_count = 0

for url in RSS_URLS:
    feed = feedparser.parse(url)
    print(f"ソース取得: {url} (記事数: {len(feed.entries)})")
    
    for entry in feed.entries[:5]: 
        if articles_count >= 10: break
        
        clean_title = "".join([c for c in entry.title if c.isalnum() or c==' '])[:30].strip().replace(" ", "_")
        filename = os.path.join(POSTS_DIR, f"{datetime.date.today()}-{clean_title}.md")
        
        if os.path.exists(filename): continue

        article_md = ask_ai(entry.title, entry.summary, entry.link)
        
        if article_md:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(article_md)
            print(f"保存完了: {filename}")
            articles_count += 1
        
        time.sleep(2)

print(f"本日の業務終了。作成記事数: {articles_count}")
