# Dominion Group of Schools — Website

Plain HTML/CSS static site. No build step, no npm needed — works on any static host.

## Deploy to Vercel (free)
1. Create a GitHub repo, push this folder's contents to it.
2. Go to vercel.com → New Project → import the repo.
3. Framework preset: "Other". Build command: leave blank. Output directory: leave blank (root).
4. Deploy. Vercel gives you a `*.vercel.app` URL immediately.
5. In Vercel: Project → Settings → Domains → add `dominiongroupofschools.com`.
6. In GoDaddy DNS settings for the domain, add the records Vercel shows you
   (usually an A record to 76.76.21.21 and a CNAME for `www`).
7. Propagation takes anywhere from a few minutes to a few hours.

Netlify works the same way (drag-and-drop the folder at app.netlify.com/drop
also works for a quick preview, no git needed).

## What to replace before launch
- `assets/` — swap the placeholder `.placeholder-img` divs in about.html,
  news.html for real `<img src="assets/photos/...">` once you have photos.
- Contact details (phone, address, email) — currently placeholders in
  every page's footer and contact.html.
- Leadership names/bios in about.html.
- News posts in news.html — currently sample content.
- The two forms (admissions.html, contact.html) currently just show an
  alert on submit. Wire them to a real service (e.g. Formspree, Netlify
  Forms, or a simple backend) so submissions actually reach an inbox.

## Structure
- `index.html` — Home
- `about.html` — About/mission/leadership
- `academics.html` — Nursery/Primary/Secondary curriculum
- `admissions.html` — Admissions process + enquiry form
- `news.html` — News/events
- `contact.html` — Contact form + details
- `assets/styles.css` — all styling, one shared file
