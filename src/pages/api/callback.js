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

    // もしトークンが取れなかった場合のエラー表示
    if (!token) {
      return new Response("GitHubからのトークン取得に失敗しました。設定を確認してください。", { status: 500 });
    }

    // デカップCMSが受け取れる「最も標準的で強力な」メッセージ送信コード
    const responseHtml = `
      <!DOCTYPE html>
      <html>
      <head><title>認証成功</title></head>
      <body>
        <p>認証に成功しました。まもなく管理画面へ戻ります...</p>
        <script>
          (function() {
            const token = "${token}";
            const content = JSON.stringify({ token: token, provider: "github" });
            const message = "authorization:github:success:" + content;
            
            // 親ウィンドウにメッセージを送信（ターゲットを明示的に指定せず広く送る）
            window.opener.postMessage(message, "*");
            
            console.log("Token sent to opener.");
            
            // 1秒待ってから閉じる
            setTimeout(function() {
              window.close();
            }, 1000);
          })();
        </script>
      </body>
      </html>
    `;

    return new Response(responseHtml, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  } catch (e) {
    return new Response("接続エラー: " + e.message, { status: 500 });
  }
}
