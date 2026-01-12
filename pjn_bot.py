import os
import datetime
import feedparser
import google.generativeai as genai
import time

# --- AI設定 ---
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 試行するモデルのリスト（動くものを自動で探します）
MODELS_TO_TRY = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro"]

POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

RSS_URLS = [
    "https://www.thestar.com.my/rss/news/nation",
    "https://www.thestar.com.my/rss/metro/community"
]

def ask_ai(title, summary, link):
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
    5. 出力は以下のMarkdown形式の「中身」だけを出力。
    ---
    title: "{title}"
    date: "{datetime.date.today()}"
    category: "ニュース"
    ---
    <div class="genre-label">ジャンル：ニュース</div>
    <h3>【内容（全文翻訳）】</h3>
    """

    for model_name in MODELS_TO_TRY:
        try:
            print(f"モデル {model_name} で試行中...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt + "\n\n(翻訳された本文をここに)\n\n<a href='" + link + "' class='source-link'>🔗 参照元記事を確認する</a>")
            
            if response.text:
                return response.text
        except Exception as e:
            print(f"モデル {model_name} でエラー: {e}")
            continue # 次のモデルを試す
            
    return None

# --- メイン処理 ---
print("ニュース取得開始...")
articles_count = 0

for url in RSS_URLS:
    feed = feedparser.parse(url)
    print(f"ソース取得: {url} (記事数: {len(feed.entries)})")
    
    for entry in feed.entries[:5]: 
        if articles_count >= 10: break
        
        # ファイル名作成
        clean_title = "".join([c for c in entry.title if c.isalnum() or c==' '])[:30].strip().replace(" ", "_")
        filename = os.path.join(POSTS_DIR, f"{datetime.date.today()}-{clean_title}.md")
        
        if os.path.exists(filename): continue

        article_md = ask_ai(entry.title, entry.summary, entry.link)
        
        if article_md:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(article_md)
            print(f"保存完了: {filename}")
            articles_count += 1
        
        time.sleep(2) # API制限回避のための待機

print(f"本日の業務終了。作成記事数: {articles_count}")
