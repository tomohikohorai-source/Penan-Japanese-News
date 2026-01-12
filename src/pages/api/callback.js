export const prerender = false;

export async function GET({ url }) {
  const code = url.searchParams.get('code');
  const clientID = process.env.GITHUB_CLIENT_ID;
  const clientSecret = process.env.GITHUB_CLIENT_SECRET;

  try {
    const res = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ client_id: clientID, client_secret: clientSecret, code })
    });

    const data = await res.json();
    const token = data.access_token;

    if (!token) return new Response("Token error", { status: 500 });

    const html = `
      <!DOCTYPE html>
      <html>
      <head><meta charset="utf-8"></head>
      <body>
        <p>認証完了。画面を切り替えています...</p>
        <script>
          (function() {
            const token = "${token}";
            const userStr = JSON.stringify({ token: token, provider: "github" });
            
            // 1. 親ウィンドウに合図を送る（標準的な方法）
            if (window.opener) {
              window.opener.postMessage("authorization:github:success:" + userStr, "*");
            }
            
            // 2. 万が一のためにブラウザの共通領域にも鍵を保存する
            localStorage.setItem('decap-cms-user', userStr);
            
            // 3. 1秒後にウィンドウを閉じる
            setTimeout(() => {
              window.close();
            }, 1000);
          })();
        </script>
      </body>
      </html>
    `;

    return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
  } catch (e) {
    return new Response(e.message, { status: 500 });
  }
}
