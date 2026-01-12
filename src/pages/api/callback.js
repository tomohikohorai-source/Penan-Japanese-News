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

    const responseHtml = `
      <!DOCTYPE html>
      <html>
      <body>
        <script>
          const token = "${token}";
          const message = "authorization:github:success:" + JSON.stringify({token: token, provider: "github"});
          
          // 親ウィンドウにトークンを送信
          if (window.opener) {
            window.opener.postMessage(message, window.location.origin);
            setTimeout(() => window.close(), 500);
          } else {
            document.body.innerHTML = "ログイン成功。画面を閉じて管理画面を更新してください。";
          }
        </script>
        認証に成功しました。
      </body>
      </html>
    `;

    return new Response(responseHtml, { headers: { 'Content-Type': 'text/html' } });
  } catch (e) {
    return new Response(e.message, { status: 500 });
  }
}
