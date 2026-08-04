export default function handler(req, res) {
  const clientId = process.env.GITHUB_OAUTH_CLIENT_ID;
  const host = req.headers.host;
  const redirectUri = `https://${host}/api/callback`;

  if (!clientId) {
    res.status(500).send("Missing GITHUB_OAUTH_CLIENT_ID environment variable.");
    return;
  }

  const authUrl =
    `https://github.com/login/oauth/authorize` +
    `?client_id=${encodeURIComponent(clientId)}` +
    `&redirect_uri=${encodeURIComponent(redirectUri)}` +
    `&scope=repo,user`;

  res.writeHead(302, { Location: authUrl });
  res.end();
}
