import os, datetime, feedparser, requests, json, time

# --- 設定 ---
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"
POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

def ask_ai(title, summary, link):
    prompt = f"""
    あなたはペナン在住日本人向けのニュース編集長です。
    以下の英語ニュースを、子育て世帯や母子留学生が読みやすい日本語に翻訳・整形してください。

    【ニュース】
    タイトル: {title}
    内容: {summary}

    【出力ルール】
    1. 1行目は必ず「ジャンル：〇〇」とする（教育、重要、グルメ、おでかけ、暮らし、エンタメ、お得 のいずれか）
    2. 本文は読みやすく改行を入れる。
    3. Markdown形式で出力する。
    """
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(API_URL, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=20)
        if response.status_code == 200:
            content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            lines = content.strip().split('\n')
            genre = "暮らし"
            if "ジャンル：" in lines[0]:
                genre = lines[0].replace("ジャンル：", "").strip()
                body = "\n".join(lines[1:])
            else:
                body = content
            return genre, body
        return None, None
    except:
        return None, None

print("🚀 PJN 自動更新システム稼働中...")
feed = feedparser.parse("https://news.google.com/rss/search?q=Penang+when:24h&hl=en-MY&gl=MY&ceid=MY:en")
count = 0

for entry in feed.entries[:3]:
    safe_title = "".join([c for c in entry.title if c.isalnum() or c==' '])[:30].strip().replace(" ", "_")
    filename = os.path.join(POSTS_DIR, f"{datetime.date.today()}-{safe_title}.md")
    if os.path.exists(filename): continue

    genre, body = ask_ai(entry.title, entry.summary, entry.link)
    
    if genre and body:
        # AI翻訳成功パターン
        print(f"✅ AI翻訳成功: {entry.title[:20]}...")
        final_title = entry.title
        final_content = f"<div class='genre-label'>ジャンル：{genre}</div>\n<h3>【内容】</h3>\n\n{body}"
        final_category = genre
    else:
        # AI制限中のバックアップパターン
        print(f"⚠️ AI制限中のため原文で作成します: {entry.title[:20]}...")
        final_title = f"【速報】{entry.title}"
        final_content = f"（現在AI翻訳制限中のため、原文を表示しています）\n\n{entry.summary}"
        final_category = "重要"

    # ファイル書き出し
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: \"{final_title}\"\ndate: \"{datetime.date.today()}\"\ncategory: \"{final_category}\"\n---\n{final_content}\n\n<a href='{entry.link}' target='_blank' rel='noopener noreferrer' class='source-link'>🔗 参照元（英語）を確認する</a>")
    
    count += 1
    time.sleep(60) # 1分休み（Googleの無料枠を大切に使うため）

print(f"🏁 業務終了。本日の公開記事数: {count}")
