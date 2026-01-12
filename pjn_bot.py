import os
import datetime
import feedparser
import google.generativeai as genai

# 設定
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 収集するソース（ニュースRSS）
# ※学校サイトの自動巡回はデザイン変更に弱いため、まずは信頼性の高いニュースRSSから開始します
RSS_URLS = [
    "https://www.thestar.com.my/rss/metro/community", # ペナン現地のコミュニティニュース
]

def ask_ai(title, summary, link):
    prompt = f"""
    あなたはペナン在住日本人向けのニュース編集長です。
    以下の英語ニュースを、子育て世帯や母子留学生が読みやすい日本語に全文翻訳・整形してください。

    【ニュース内容】
    タイトル: {title}
    内容: {summary}

    【出力ルール】
    1. 冒頭に「ジャンル：〇〇」を明記（教育、生活、交通など）
    2. タイトルは「【ジャンル】タイトル」の形式に。
    3. 本文は3-4行ごとに改行を入れ、読みやすく。
    4. 最後に「🔗 参照元記事を確認する」というリンクをつける。
    5. 出力は以下のMarkdown形式の「中身」だけを出力してください。

    ---
    title: "【ジャンル】タイトル"
    date: "{datetime.date.today()}"
    category: "ジャンル名"
    ---
    <div class="genre-label">ジャンル：〇〇</div>
    <h3>【内容（全文翻訳）】</h3>
    （ここに翻訳された本文）
    
    <a href="{link}" class="source-link">🔗 参照元記事を確認する</a>
    """
    response = model.generate_content(prompt)
    return response.text

# 実行
feed = feedparser.parse(RSS_URLS[0])
for entry in feed.entries[:3]: # 最新3件を取得
    article_md = ask_ai(entry.title, entry.summary, entry.link)
    filename = f"src/pages/posts/{datetime.date.today()}-{entry.title[:20]}.md".replace(" ", "_")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(article_md)
