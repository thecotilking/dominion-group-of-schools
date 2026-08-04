export default async function handler(req, res) {
  const clientId = process.env.GITHUB_OAUTH_CLIENT_ID;
  const clientSecret = process.env.GITHUB_OAUTH_CLIENT_SECRET;
  const code = req.query.code;

  if (!clientId || !clientSecret) {
    res.status(500).send("Missing GitHub OAuth environment variables.");
    return;
  }
  if (!code) {
    res.status(400).send("Missing authorization code.");
    return;
  }

  try {
    const tokenRes = await fetch("https://github.com/login/oauth/access_token", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        client_id: clientId,
        client_secret: clientSecret,
        code: code,
      }),
    });

    const tokenData = await tokenRes.json();

    if (tokenData.error) {
      res.status(400).send(`GitHub OAuth error: ${tokenData.error_description || tokenData.error}`);
      return;
    }

    const payload = JSON.stringify({ token: tokenData.access_token, provider: "github" });
    const message = "authorization:github:success:" + payload;

    const html = `<!DOCTYPE html>
<html><body>
<script>
(function() {
  function receiveMessage(e) {
    window.opener.postMessage(${JSON.stringify(message)}, e.origin);
    window.removeEventListener("message", receiveMessage, false);
  }
  window.addEventListener("message", receiveMessage, false);
  window.opener.postMessage("authorizing:github", "*");
})();
</script>
<p>Authenticated. You can close this window if it does not close automatically.</p>
</body></html>`;

    res.setHeader("Content-Type", "text/html");
    res.status(200).send(html);
  } catch (err) {
    res.status(500).send("Authentication failed: " + err.message);
  }
}
