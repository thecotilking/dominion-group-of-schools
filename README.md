# Dominion Group of Schools — Website (Source)

**Important change:** this repo now holds the *source* for the site, not the
final HTML. Vercel builds the real site automatically on every push by
running `python3 build.py`, which reads everything (including news posts)
and produces the final site in `output/`.

You should no longer copy files from a Claude-generated `output/` folder
into this repo. Just edit the source files below and push — Vercel does
the rest.

## What's in here

- `build.py` — generates the whole site. Run `python3 build.py` locally to
  preview changes.
- `content/news/*.md` — one file per news post. This is what the staff CMS
  edits directly on GitHub — no need to touch `build.py` to add news.
- `assets/styles.css`, `assets/photos/` — styling and images.
- `admin/` — the staff Content Manager (Decap CMS). Lives at
  `dominiongroupofschools.com/admin`.
- `api/auth.js`, `api/callback.js` — the login bridge that lets the CMS
  securely authenticate staff through GitHub. Requires environment
  variables set in Vercel (see setup steps below).
- `vercel.json` — tells Vercel to run `python3 build.py` and serve
  `output/` as the live site.

## One-time setup still required

1. **Create a GitHub OAuth App** at
   github.com/settings/developers → OAuth Apps → New OAuth App
   - Application name: `Dominion Site CMS`
   - Homepage URL: `https://dominiongroupofschools.com`
   - Authorization callback URL: `https://dominiongroupofschools.com/api/callback`
   - Generate a Client Secret and copy both the Client ID and Client Secret.

2. **Add environment variables in Vercel**
   Project → Settings → Environment Variables:
   - `GITHUB_OAUTH_CLIENT_ID`
   - `GITHUB_OAUTH_CLIENT_SECRET`
   Apply to Production, then redeploy.

3. **Give the staff member GitHub access**
   They need a free GitHub account. Add them as a Collaborator on this repo
   (Settings → Collaborators) so they can log into the CMS and publish.

4. **Staff logs in at** `dominiongroupofschools.com/admin` — click
   "Login with GitHub", authorize once, and they'll see a simple dashboard
   to add/edit "News & Events" posts with a title, date, photo and summary.
   Every publish automatically updates the live site within about a minute.

## Local preview

```bash
python3 build.py
```
Then open `output/index.html` in a browser, or serve the folder locally.
