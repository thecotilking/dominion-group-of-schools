export default async function handler(req, res) {
  res.setHeader("Cross-Origin-Opener-Policy", "unsafe-none");
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

    // Verify this specific user actually has write access to the repo
    // before ever handing control to the CMS. Public repo visibility does
    // not imply write access, but without this check anyone with a GitHub
    // account could reach the editor UI (even though they couldn't
    // ultimately save anything, since GitHub itself blocks that server-side).
    const repoRes = await fetch(
      "https://api.github.com/repos/thecotilking/dominion-group-of-schools",
      {
        headers: {
          Authorization: `token ${tokenData.access_token}`,
          Accept: "application/vnd.github+json",
        },
      }
    );
    const repoData = await repoRes.json();
    const canWrite = !!(repoData.permissions && (repoData.permissions.push || repoData.permissions.admin));

    if (!canWrite) {
      res.status(403).setHeader("Content-Type", "text/html");
      res.send(`<!DOCTYPE html>
<html><body style="font-family: sans-serif; padding: 48px; text-align:center;">
<h2>Access Denied</h2>
<p>You're signed in to GitHub, but this account doesn't have permission to edit the Dominion Group of Schools website.</p>
<p>If you believe this is a mistake, contact the site administrator to be added as a collaborator on the repository.</p>
</body></html>`);
      return;
    }

    const payload = JSON.stringify({ token: tokenData.access_token, provider: "github" });
    const message = "authorization:github:success:" + payload;

    const html = `<!DOCTYPE html>
<html><body style="font-family: sans-serif; padding: 24px;">
<p id="status">Connecting back to the CMS...</p>
<script>
(function() {
  var statusEl = document.getElementById('status');
  var message = ${JSON.stringify(message)};

  if (!window.opener) {
    statusEl.textContent = "No opener window found. This tab was likely opened without a proper popup link (or a popup blocker interfered). Please close this tab, disable any popup blocker for this site, and click 'Login with GitHub' again.";
    return;
  }

  function send(targetOrigin) {
    try {
      window.opener.postMessage(message, targetOrigin);
    } catch (err) {
      statusEl.textContent = "Error sending message to opener: " + err.message;
    }
  }

  function receiveMessage(e) {
    send(e.origin);
    statusEl.textContent = "Authenticated. Closing this window...";
    window.removeEventListener("message", receiveMessage, false);
    setTimeout(function() { window.close(); }, 800);
  }

  window.addEventListener("message", receiveMessage, false);
  window.opener.postMessage("authorizing:github", "*");

  // Fallback: if opener never replies within 2s, send directly to any origin
  // so the CMS can still pick it up even if the handshake ping is missed.
  setTimeout(function() {
    send("*");
    statusEl.textContent = "Authenticated. If this tab does not close automatically, you can close it and return to the CMS tab.";
  }, 2000);
})();
</script>
</body></html>`;

    res.setHeader("Content-Type", "text/html");
    res.status(200).send(html);
  } catch (err) {
    res.status(500).send("Authentication failed: " + err.message);
  }
}
