import os
import re
import shutil
from datetime import date, datetime

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@400;500;600;700&family=Work+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">'

LOGO_SVG = '''<img src="/assets/photos/logo.jpg" alt="Dominion Group of Schools crest" class="brand-mark" style="border-radius:50%; object-fit:cover;">'''

SITE_URL = "https://dominiongroupofschools.com"

# ---------------- Markdown frontmatter parsing (no external deps) ----------------

def parse_markdown(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    frontmatter_raw, body = parts[1], parts[2]
    data = {}
    lines = frontmatter_raw.strip("\n").split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or ":" not in line:
            i += 1
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value:
            data[key] = value
            i += 1
        else:
            # Possible list: look ahead for "  - " lines
            items = []
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("-"):
                item_line = lines[j].strip()[1:].strip()
                if ":" in item_line:
                    # dict-style list item, e.g. "image: path.jpg" -> take the value
                    _, _, item_val = item_line.partition(":")
                    items.append(item_val.strip())
                elif item_line:
                    items.append(item_line)
                j += 1
            data[key] = items
            i = j
    data["body"] = body.strip()
    return data

def load_news():
    news_dir = "content/news"
    items = []
    if os.path.isdir(news_dir):
        for fname in os.listdir(news_dir):
            if fname.endswith(".md"):
                item = parse_markdown(os.path.join(news_dir, fname))
                if item and item.get("title"):
                    item["slug"] = fname[:-3]
                    items.append(item)
    def sort_key(item):
        try:
            return datetime.strptime(item.get("date", "1970-01-01")[:10], "%Y-%m-%d")
        except ValueError:
            return datetime(1970, 1, 1)
    items.sort(key=sort_key, reverse=True)
    return items

# ---------------- Shared page chrome ----------------

def header(active):
    links = [
        ("/index.html", "Home"),
        ("/about.html", "About"),
        ("/academics.html", "Academics"),
        ("/admissions.html", "Admissions"),
        ("/news.html", "News"),
        ("/contact.html", "Contact"),
    ]
    nav_items = ""
    for href, label in links:
        current = ' aria-current="page"' if href.lstrip("/") == active.lstrip("/") else ""
        nav_items += f'<a href="{href}"{current}>{label}</a>'
    return f'''<header class="site-header">
  <div class="nav-row">
    <a href="/index.html" class="brand">
      {LOGO_SVG}
      <span class="brand-name">Dominion Group<small>of Schools</small></span>
    </a>
    <button class="nav-toggle" aria-label="Toggle menu" onclick="document.querySelector('.main-nav').classList.toggle('open')">☰</button>
    <nav class="main-nav">
      {nav_items}
      <a href="/admissions.html" class="btn btn-gold" style="padding:10px 20px;">Apply Now</a>
    </nav>
  </div>
</header>'''

def footer():
    return '''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h4>Dominion Group of Schools</h4>
        <p style="color:rgba(251,243,231,0.7); max-width:36ch;">Knowledge, Wisdom, Fear of God. Nurturing every child from Creche to Secondary, under one roof.</p>
      </div>
      <div>
        <h4>Explore</h4>
        <ul>
          <li><a href="/about.html">About Us</a></li>
          <li><a href="/academics.html">Academics</a></li>
          <li><a href="/admissions.html">Admissions</a></li>
          <li><a href="/news.html">News &amp; Events</a></li>
        </ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li>1 Dominion School Road, off Hospital Road, Ugboma Layout, Asaba, Delta State</li>
          <li>0705 574 2394</li>
          <li>dominiongroupofschools777@gmail.com</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; 2026 Dominion Group of Schools. All rights reserved.</span>
      <span>Built with care for our school community.</span>
    </div>
  </div>
</footer>'''

def page(title, description, active, body, extra_class="bg-aurora"):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Dominion Group of Schools</title>
<meta name="description" content="{description}">
<meta name="google-site-verification" content="dE47g7njdAgwHCtTECg4YXOA3cOfoKFzB0KvC_WPCpc" />
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "School",
  "name": "Dominion Group of Schools",
  "alternateName": "Dominion Nursery/Primary School and Dominion College",
  "url": "https://dominiongroupofschools.com",
  "logo": "https://dominiongroupofschools.com/assets/photos/logo.jpg",
  "image": "https://dominiongroupofschools.com/assets/photos/campus-exterior-1.jpg",
  "description": "Dominion Group of Schools offers Nursery, Primary and Secondary education in Asaba, Delta State, Nigeria, guided by the motto Knowledge, Wisdom, Fear of God.",
  "telephone": "+2347055742394",
  "email": "dominiongroupofschools777@gmail.com",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "1 Dominion School Road, off Hospital Road, Ugboma Layout",
    "addressLocality": "Asaba",
    "addressRegion": "Delta State",
    "addressCountry": "NG"
  }},
  "sameAs": []
}}
</script>
{FONTS}
<link rel="stylesheet" href="/assets/styles.css">
</head>
<body class="{extra_class}">
<div class="site-notice"><div class="marquee-track"><span class="marquee-item">🎓 Admissions for 2026 are now open!<a href="/admissions.html">Apply or Enquire</a></span><span class="marquee-item">🎓 Admissions for 2026 are now open!<a href="/admissions.html">Apply or Enquire</a></span></div></div>
{header(active)}
{body}
{footer()}
<div class="lightbox-overlay" id="lightbox-overlay" onclick="closeLightbox()">
  <button class="modal-close" onclick="closeLightbox()" aria-label="Close" style="position:fixed; top:20px; right:20px;">&times;</button>
  <img id="lightbox-img" src="" alt="">
</div>
<script>
(function() {{
  var reducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function startArcSun() {{
    if (reducedMotion) return;
    var motion = document.getElementById('arcSunMotion');
    if (motion && motion.beginElement) {{
      try {{ motion.beginElement(); }} catch (e) {{}}
    }}
  }}
  var arc = document.querySelector('.arc-wrap');
  if (arc && 'IntersectionObserver' in window) {{
    var io = new IntersectionObserver(function(entries) {{
      entries.forEach(function(entry) {{
        if (entry.isIntersecting) {{
          arc.classList.add('in-view');
          startArcSun();
          io.disconnect();
        }}
      }});
    }}, {{ threshold: 0.3 }});
    io.observe(arc);
  }} else if (arc) {{
    arc.classList.add('in-view');
    startArcSun();
  }}

  var revealEls = document.querySelectorAll('.reveal');
  if (revealEls.length && 'IntersectionObserver' in window) {{
    var rio = new IntersectionObserver(function(entries) {{
      entries.forEach(function(entry) {{
        if (entry.isIntersecting) {{
          entry.target.classList.add('in-view');
          rio.unobserve(entry.target);
        }}
      }});
    }}, {{ threshold: 0.15 }});
    revealEls.forEach(function(el) {{ rio.observe(el); }});
  }} else {{
    revealEls.forEach(function(el) {{ el.classList.add('in-view'); }});
  }}
  document.querySelectorAll('.main-nav a').forEach(function(link) {{
    link.addEventListener('click', function() {{
      document.querySelector('.main-nav').classList.remove('open');
    }});
  }});
  var spotlightIndex = 0;
  var spotlightTimer = null;
  function showSpotlight(idx) {{
    var slides = document.querySelectorAll('.spotlight-banner');
    var dots = document.querySelectorAll('.spotlight-dot');
    if (!slides.length) return;
    spotlightIndex = (idx + slides.length) % slides.length;
    slides.forEach(function(s, i) {{ s.classList.toggle('active', i === spotlightIndex); }});
    dots.forEach(function(d, i) {{ d.classList.toggle('active', i === spotlightIndex); }});
  }}
  function restartSpotlightTimer() {{
    if (spotlightTimer) clearInterval(spotlightTimer);
    var slides = document.querySelectorAll('.spotlight-banner');
    if (slides.length > 1) {{
      spotlightTimer = setInterval(function() {{ showSpotlight(spotlightIndex + 1); }}, 6000);
    }}
  }}
  window.shiftSpotlight = function(dir) {{ showSpotlight(spotlightIndex + dir); restartSpotlightTimer(); }};
  window.goToSpotlight = function(idx) {{ showSpotlight(idx); restartSpotlightTimer(); }};
  restartSpotlightTimer();

  window.openLightbox = function(src) {{
    var overlay = document.getElementById('lightbox-overlay');
    var img = document.getElementById('lightbox-img');
    if (overlay && img) {{
      img.src = src;
      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
    }}
  }};
  window.closeLightbox = function() {{
    var overlay = document.getElementById('lightbox-overlay');
    if (overlay) {{ overlay.classList.remove('open'); document.body.style.overflow = ''; }}
  }};
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') {{ window.closeLightbox(); }}
  }});
}})();
</script>
</body>
</html>'''

# ---------------- Build ----------------

if os.path.exists("output"):
    shutil.rmtree("output")
os.makedirs("output", exist_ok=True)

# ---------------- News data + Spotlight (needed by HOME too) ----------------
# ---------------- NEWS (dynamic, read from content/news/*.md) ----------------
news_items = load_news()
spotlight_items = [item for item in news_items if str(item.get("spotlight", "")).strip().lower() == "true"]

def get_images(item):
    images = [img for img in (item.get("images") or []) if img]
    if not images and item.get("image"):
        images = [item["image"]]
    return [img if img.startswith("/") else "/" + img for img in images]

def build_spotlight_section(compact=False):
    if not spotlight_items:
        return ""
    slides = ""
    for idx, item in enumerate(spotlight_items):
        images = get_images(item)
        cover = images[0] if images else ""
        date_display = item.get("date", "")[:10]
        title = item.get("title", "")
        excerpt = item.get("body", "")
        active_class = " active" if idx == 0 else ""
        img_html = f'<img src="{cover}" alt="{title}">' if cover else '<div class="placeholder-img" style="aspect-ratio:16/7;">No photo</div>'
        excerpt_html = "" if compact else f'<p class="news-excerpt">{excerpt}</p>'
        slides += f'''
    <a href="/news/{item['slug']}.html" class="spotlight-banner{active_class}" data-index="{idx}">
      {img_html}
      <div class="spotlight-banner-content">
        <span class="spotlight-date">{date_display}</span>
        <h2>{title}</h2>
        {excerpt_html}
        <span class="btn btn-primary" style="margin-top:12px;">Read Full Story</span>
      </div>
    </a>'''

    dots = ""
    if len(spotlight_items) > 1:
        for idx in range(len(spotlight_items)):
            active = " active" if idx == 0 else ""
            dots += f'<button class="spotlight-dot{active}" onclick="goToSpotlight({idx})" aria-label="Go to slide {idx+1}"></button>'

    arrows = ""
    if len(spotlight_items) > 1:
        arrows = '''
      <button class="spotlight-arrow spotlight-arrow-left" onclick="shiftSpotlight(-1)" aria-label="Previous">&#8592;</button>
      <button class="spotlight-arrow spotlight-arrow-right" onclick="shiftSpotlight(1)" aria-label="Next">&#8594;</button>'''

    wrap_class = "spotlight-banner-wrap spotlight-compact reveal" if compact else "spotlight-banner-wrap reveal"
    eyebrow = "Latest Highlight" if compact else "Spotlight"

    return f'''
<section style="padding-top:0;">
  <div class="wrap">
    <span class="eyebrow">{eyebrow}</span>
    <div class="{wrap_class}">
      {slides}
      {arrows}
    </div>
    <div class="spotlight-dots">{dots}</div>
  </div>
</section>'''

home_spotlight_section = build_spotlight_section(compact=True)
news_spotlight_section = build_spotlight_section(compact=False)

# ---------------- HOME ----------------
home_body = f'''
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <span class="eyebrow">Knowledge &middot; Wisdom &middot; Fear of God</span>
      <h1>Every stage of childhood, carried with the same care.</h1>
      <p class="lead">Dominion Group of Schools walks with your child from their very first day of nursery to their final secondary exam &mdash; one community, one standard of excellence, all the way through.</p>
      <div class="hero-actions">
        <a href="/admissions.html" class="btn btn-primary">Start Admissions</a>
        <a href="/about.html" class="btn btn-outline">Our Story</a>
      </div>
      <div class="pill-row">
        <span class="pill-label">Explore:</span>
        <a href="#nursery" class="pill-link">Nursery</a>
        <a href="#primary" class="pill-link">Primary</a>
        <a href="#secondary" class="pill-link">Secondary</a>
      </div>
    </div>
    <div class="arc-wrap">
      <svg viewBox="0 0 400 220" width="100%" style="overflow:visible;">
        <defs>
          <filter id="arcGlow" x="-100%" y="-100%" width="300%" height="300%">
            <feGaussianBlur stdDeviation="6" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        <path id="arcPath" class="arc-path" d="M20 190 C 90 60, 310 60, 380 190" stroke="#6E1E2E" stroke-width="3" fill="none" stroke-linecap="round"/>
        <a href="#nursery"><circle class="arc-dot" cx="20" cy="190" r="9" fill="#8A6C4E"/></a>
        <a href="#primary"><circle class="arc-dot" cx="200" cy="72" r="9" fill="#D9A73B"/></a>
        <a href="#secondary"><circle class="arc-dot" cx="380" cy="190" r="9" fill="#6E1E2E"/></a>
        <circle class="arc-sun" r="6" fill="#D9A73B" filter="url(#arcGlow)">
          <animateMotion id="arcSunMotion" dur="6s" begin="indefinite" repeatCount="indefinite" keyPoints="0;1;0" keyTimes="0;0.5;1" calcMode="linear">
            <mpath href="#arcPath"/>
          </animateMotion>
        </circle>
      </svg>
      <div class="arc-caption">
        <a href="#nursery">Nursery<small>Ages 2&ndash;5</small></a>
        <a href="#primary">Primary<small>Ages 6&ndash;11</small></a>
        <a href="#secondary">Secondary<small>Ages 12&ndash;17</small></a>
      </div>
    </div>
  </div>
</section>
{home_spotlight_section}
<section class="overview">
  <div class="wrap overview-split">
    <div class="overview-label">
      <strong>Overview</strong>
      Our Promise
    </div>
    <div>
      <p class="overview-statement">Dominion is built to carry a child from their very first day of nursery to their final secondary exam &mdash; <span class="accent">one campus, one community, one standard, all the way through.</span></p>
      <a href="/about.html" class="overview-link">Read our story &rarr;</a>
    </div>
  </div>
</section>
<section class="stages">
  <div class="wrap">
    <span class="eyebrow" style="color:var(--gold);">The Dominion Journey</span>
    <h2>Three stages. One continuous path.</h2>
    <p class="section-intro">We built Dominion around a simple idea: a child shouldn't have to change schools, cultures or standards just to grow up. Each stage hands off to the next with the same values intact.</p>
    <div class="stage-list">
      <div class="stage-card reveal" id="nursery" style="transition-delay:0s;">
        <span class="stage-num">01</span>
        <h3>Nursery</h3>
        <p>Play-driven early learning that builds curiosity, language and confidence before formal schooling begins.</p>
      </div>
      <div class="stage-card reveal" id="primary" style="transition-delay:0.1s;">
        <span class="stage-num">02</span>
        <h3>Primary</h3>
        <p>A structured, well-rounded curriculum in literacy, numeracy, science and character, taught by dedicated form teachers.</p>
      </div>
      <div class="stage-card reveal" id="secondary" style="transition-delay:0.2s;">
        <span class="stage-num">03</span>
        <h3>Secondary</h3>
        <p>Rigorous preparation for WAEC/NECO and beyond, with sciences, arts, commercial subjects and strong pastoral care.</p>
      </div>
    </div>
  </div>
</section>
<div class="motto-band">
  <p>
    <span>Knowledge</span>
    <span class="motto-divider" aria-hidden="true"></span>
    <span>Wisdom</span>
    <span class="motto-divider" aria-hidden="true"></span>
    <span>Fear of God</span>
  </p>
</div>

<section>
  <div class="wrap">
    <span class="eyebrow">Why Families Choose Us</span>
    <h2>A school built around the whole child</h2>
    <div class="card-grid">
      <div class="card reveal" style="transition-delay:0s;">
        <h3>Small Class Sizes</h3>
        <p>Every child is known by name, with teachers who track progress closely at every stage.</p>
      </div>
      <div class="card reveal" style="transition-delay:0.1s;">
        <h3>Qualified, Caring Staff</h3>
        <p>Experienced educators who bring warmth and high expectations into every classroom.</p>
      </div>
      <div class="card reveal" style="transition-delay:0.2s;">
        <h3>Safe, Modern Campus</h3>
        <p>A secure, well-maintained environment designed for learning, play and growth.</p>
      </div>
      <div class="card reveal" style="transition-delay:0.3s;">
        <h3>Consistent Values</h3>
        <p>The same standards of discipline, faith and character from nursery right through to graduation.</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <span class="eyebrow">Life at Dominion</span>
    <h2>A campus built for learning and growth</h2>
    <div class="card-grid">
      <div class="card reveal" style="padding:0; overflow:hidden; transition-delay:0s;">
        <img src="/assets/photos/campus-exterior-1.jpg" alt="Dominion Group of Schools campus building" style="border-radius:14px 14px 0 0;">
        <div style="padding:18px;"><h3>Our Campus</h3><p>Dominion College and Dominion Nursery/Primary School share one secure campus.</p></div>
      </div>
      <div class="card reveal" style="padding:0; overflow:hidden; transition-delay:0.1s;">
        <img src="/assets/photos/science-lab-1.jpg" alt="Student in the science laboratory" style="border-radius:14px 14px 0 0;">
        <div style="padding:18px;"><h3>Science Laboratory</h3><p>Hands-on practicals give secondary students real lab experience ahead of WAEC/NECO.</p></div>
      </div>
      <div class="card reveal" style="padding:0; overflow:hidden; transition-delay:0.2s;">
        <img src="/assets/photos/classroom-students.jpg" alt="Students in class and walking on campus" style="border-radius:14px 14px 0 0;">
        <div style="padding:18px;"><h3>Everyday Learning</h3><p>Attentive teachers and focused classrooms, day to day.</p></div>
      </div>
      <div class="card reveal" style="padding:0; overflow:hidden; transition-delay:0.3s;">
        <img src="/assets/photos/graduation.jpg" alt="Dominion primary school graduation ceremony" style="border-radius:14px 14px 0 0;">
        <div style="padding:18px;"><h3>Milestones</h3><p>Celebrating our pupils at every graduation and achievement.</p></div>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="cta-band">
      <div>
        <h2>Ready to visit us?</h2>
        <p>Book a school tour or start your child's application today.</p>
      </div>
      <div style="display:flex; gap:12px; flex-wrap:wrap;">
        <a href="/admissions.html" class="btn btn-primary">Apply Now</a>
        <a href="/contact.html" class="btn btn-outline">Book a Tour</a>
      </div>
    </div>
  </div>
</section>
'''
with open("output/index.html", "w") as f:
    f.write(page("Home", "Dominion Group of Schools — Nursery, Primary and Secondary education.", "index.html", home_body))

# ---------------- ABOUT ----------------
about_body = '''
<section class="page-hero">
  <div class="wrap">
    <h1>About Dominion</h1>
    <p>Our story, our values, and the people who make Dominion feel like home.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <span class="eyebrow">Our Story</span>
    <h2>Founded on care, built on consistency</h2>
    <p class="section-intro">Dominion Group of Schools was founded in September 2002 by Rev. Mrs. Esther Ebolum, who started the very first Dominion daycare from her father's boys' quarters. As the vision grew, a nursery and primary school was opened in Ogbeosowe Quarters, Asaba. In time, a permanent site of one and a half acres was acquired in Umudiake Land Extension, Ani-Ngene, where the secondary arm and a Nursery/Primary annex were established. Dominion is a purely Christian school, an affiliate of Dominion Christian Center, Asaba, founded by the Proprietress's husband, Bishop Ken Ebolum, who also serves as the school's Chairman.</p>
    <div class="card-grid">
      <div class="card">
        <h3>Our Mission</h3>
        <p>To provide a purely Christian education that builds confident, disciplined and knowledgeable young people, raised to become future leaders in their generation.</p>
      </div>
      <div class="card">
        <h3>Our Vision</h3>
        <p>To be a leading Christian group of schools known for academic excellence, godly character, and the raising up of tomorrow's leaders.</p>
      </div>
      <div class="card">
        <h3>Our Motto</h3>
        <p><strong>Nursery &amp; Primary:</strong> Knowledge, Wisdom, Fear of God.<br><strong>Secondary:</strong> Building Future Leaders.</p>
      </div>
    </div>
  </div>
</section>
<section>
  <div class="wrap">
    <span class="eyebrow">Our Campuses</span>
    <h2>Two campuses, one Dominion</h2>
    <div class="card-grid">
      <div class="card">
        <h3>Dominion College &amp; Nur/Pri Annex</h3>
        <p>1 Dominion School Road, off Hospital Road, Ugboma Layout, Asaba, Delta State</p>
      </div>
      <div class="card">
        <h3>Dominion Nursery/Primary School</h3>
        <p>7 Osowe Street, Ogbeosowe, Asaba, Delta State</p>
      </div>
    </div>
  </div>
</section>
<section>
  <div class="wrap">
    <span class="eyebrow">Leadership</span>
    <h2>Meet our team</h2>
    <div class="card-grid">
      <div class="card">
        <img src="/assets/photos/proprietress.jpg" alt="Rev. Mrs. Esther Ebolum, Founder and Proprietress" class="leader-photo">
        <h3 style="margin-top:14px;">Rev. Mrs. Esther Ebolum</h3>
        <p>Founder &amp; Proprietress</p>
      </div>
      <div class="card">
        <img src="/assets/photos/chairman.jpg" alt="Bishop Ken Ebolum, Chairman" class="leader-photo">
        <h3 style="margin-top:14px;">Bishop Ken Ebolum</h3>
        <p>Chairman &mdash; Founder, Dominion Christian Center</p>
      </div>
      <div class="card">
        <img src="/assets/photos/blessing-okonta.jpg" alt="Mrs. Blessing Okonta, Principal" class="leader-photo">
        <h3 style="margin-top:14px;">Mrs. Blessing Okonta</h3>
        <p>Principal</p>
      </div>
      <div class="card">
        <img src="/assets/photos/prosper-nwankwo.jpg" alt="Mr. Prosper Nwankwo, Vice Principal" class="leader-photo">
        <h3 style="margin-top:14px;">Mr. Prosper Nwankwo</h3>
        <p>Vice Principal</p>
      </div>
      <div class="card">
        <img src="/assets/photos/kenneth-nnabugwu.jpg" alt="Mr. Kenneth Nnabugwu, Assistant Administrator" class="leader-photo">
        <h3 style="margin-top:14px;">Mr. Kenneth Nnabugwu</h3>
        <p>Assistant Administrator</p>
      </div>
    </div>
  </div>
</section>
'''
with open("output/about.html", "w") as f:
    f.write(page("About", "Learn about Dominion Group of Schools — our story, mission and team.", "about.html", about_body))

# ---------------- ACADEMICS ----------------
academics_body = '''
<section class="page-hero">
  <div class="wrap">
    <h1>Academics</h1>
    <p>What your child learns at every stage of the Dominion journey.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="card-grid">
      <div class="card">
        <span class="stage-num" style="color:var(--sage); font-size:1.6rem;">01</span>
        <h3>Nursery</h3>
        <p>Play-based learning covering early literacy, numeracy, motor skills and social development, in a warm, secure setting.</p>
      </div>
      <div class="card">
        <span class="stage-num" style="color:var(--gold); font-size:1.6rem;">02</span>
        <h3>Primary</h3>
        <p>A full national curriculum &mdash; English, Mathematics, Basic Science, Social Studies, and Creative Arts &mdash; with continuous assessment.</p>
      </div>
      <div class="card">
        <span class="stage-num" style="color:var(--indigo); font-size:1.6rem;">03</span>
        <h3>Secondary</h3>
        <p>Junior and Senior Secondary programmes preparing students for BECE, WAEC and NECO, across Science, Arts and Commercial classes.</p>
      </div>
    </div>
  </div>
</section>
<section>
  <div class="wrap">
    <span class="eyebrow">In the Lab</span>
    <h2>Science, hands-on</h2>
    <div class="card-grid">
      <div class="card" style="padding:0; overflow:hidden;">
        <img src="/assets/photos/science-lab-1.jpg" alt="Secondary student conducting a chemistry experiment">
      </div>
      <div class="card" style="padding:0; overflow:hidden;">
        <img src="/assets/photos/science-lab-2.jpg" alt="Secondary student in the science laboratory">
      </div>
    </div>
  </div>
</section>
<section>
  <div class="wrap">
    <span class="eyebrow">Beyond the Classroom</span>
    <h2>Extracurricular life</h2>
    <p class="section-intro">A well-rounded Dominion education goes beyond the classroom.</p>
    <div class="card-grid">
      <div class="card"><h3>Sports &amp; Athletics</h3><p>Inter-house sports and athletics competitions each term.</p></div>
      <div class="card"><h3>Debate &amp; Quiz Club</h3><p>Building confidence, public speaking and quick thinking.</p></div>
      <div class="card"><h3>Choir &amp; Cultural Dance</h3><p>Music, cultural dance and creative performance.</p></div>
      <div class="card"><h3>Computer/ICT Club</h3><p>Practical computer skills alongside classroom learning.</p></div>
      <div class="card"><h3>Scripture Union</h3><p>Bible study and Christian fellowship for pupils and students.</p></div>
      <div class="card"><h3>Inter-House Sports</h3><p>An annual highlight bringing the whole school together.</p></div>
    </div>
  </div>
</section>
'''
with open("output/academics.html", "w") as f:
    f.write(page("Academics", "Explore the Dominion Group of Schools curriculum across Nursery, Primary and Secondary.", "academics.html", academics_body))

# ---------------- ADMISSIONS ----------------
admissions_body = '''
<section class="page-hero">
  <div class="wrap">
    <h1>Admissions</h1>
    <p>How to join the Dominion family, at any stage from Nursery to Secondary.</p>
  </div>
</section>
<section>
  <div class="wrap">
    <span class="eyebrow">How It Works</span>
    <h2>Four simple steps</h2>
    <div class="stage-list" style="color: var(--ink);">
      <div class="card"><span class="stage-num" style="font-size:1.6rem;">1</span><h3>Enquire</h3><p>Contact our admissions office or fill the form below.</p></div>
      <div class="card"><span class="stage-num" style="font-size:1.6rem;">2</span><h3>Tour &amp; Assess</h3><p>Visit the school and your child completes a simple entrance assessment.</p></div>
      <div class="card"><span class="stage-num" style="font-size:1.6rem;">3</span><h3>Register</h3><p>Submit documents and pay the registration fee.</p></div>
      <div class="card"><span class="stage-num" style="font-size:1.6rem;">4</span><h3>Resume</h3><p>Your child begins their Dominion journey on resumption day.</p></div>
    </div>
  </div>
</section>
<section>
  <div class="wrap">
    <span class="eyebrow">Get Started</span>
    <h2>Request admission information</h2>
    <form class="contact-form" action="https://formspree.io/f/xaqrankp" method="POST">
      <input type="hidden" name="_subject" value="New Admissions Enquiry - Dominion Group of Schools">
      <input type="hidden" name="_next" value="https://dominiongroupofschools.com/thank-you.html">
      <div>
        <label for="parent-name">Parent/Guardian Name</label>
        <input id="parent-name" name="parent_name" type="text" required>
      </div>
      <div>
        <label for="child-stage">Applying For</label>
        <select id="child-stage" name="applying_for">
          <option>Nursery</option>
          <option>Primary</option>
          <option>Secondary</option>
        </select>
      </div>
      <div>
        <label for="phone">Phone Number</label>
        <input id="phone" name="phone" type="tel" required>
      </div>
      <div>
        <label for="email">Email Address</label>
        <input id="email" name="email" type="email" required>
      </div>
      <button type="submit" class="btn btn-primary">Submit Enquiry</button>
    </form>
  </div>
</section>
'''
with open("output/admissions.html", "w") as f:
    f.write(page("Admissions", "Start the admissions process at Dominion Group of Schools.", "admissions.html", admissions_body))


# ---- Regular news grid (links to individual pages) ----
news_cards = ""
for item in news_items:
    images = get_images(item)
    body_text = item.get("body", "")
    title = item.get("title", "")
    cover = images[0] if images else ""
    url = f"/news/{item['slug']}.html"

    if cover:
        news_cards += f'''
      <a href="{url}" class="card news-card-trigger" style="padding:0; overflow:hidden; display:block; text-decoration:none;">
        <img src="{cover}" alt="{title}" style="border-radius:14px 14px 0 0;">
        <div style="padding:18px;"><h3>{title}</h3><p class="news-excerpt">{body_text}</p><span class="read-more-btn">Read More</span></div>
      </a>'''
    else:
        news_cards += f'''
      <a href="{url}" class="card news-card-trigger" style="display:block; text-decoration:none;">
        <div class="placeholder-img">Event photo</div>
        <h3 style="margin-top:14px;">{title}</h3>
        <p class="news-excerpt">{body_text}</p>
        <span class="read-more-btn">Read More</span>
      </a>'''

news_body = f'''
<section class="page-hero">
  <div class="wrap">
    <h1>News &amp; Events</h1>
    <p>What's happening across the Dominion community.</p>
  </div>
</section>
{news_spotlight_section}
<section>
  <div class="wrap">
    <div class="card-grid">
      {news_cards}
    </div>
  </div>
</section>
'''
with open("output/news.html", "w") as f:
    f.write(page("News", "Latest news and events from Dominion Group of Schools.", "news.html", news_body))

# ---- Individual event pages ----
os.makedirs("output/news", exist_ok=True)
for item in news_items:
    images = get_images(item)
    title = item.get("title", "")
    date_display = item.get("date", "")[:10]
    body_text = item.get("body", "")
    is_spotlight = item in spotlight_items

    gallery_html = ""
    if images:
        gallery_html = '<div class="event-gallery">' + "".join(
            f'<img src="{img}" alt="{title}" onclick="openLightbox(this.src)">' for img in images
        ) + "</div>"
    else:
        gallery_html = '<div class="placeholder-img" style="aspect-ratio:16/9;">No photo</div>'

    cta_html = '<a href="/admissions.html" class="btn btn-primary">Apply Now</a>' if is_spotlight else ""

    event_body = f'''
<section class="page-hero">
  <div class="wrap">
    <a href="/news.html" class="btn btn-outline" style="background:transparent; border-color:var(--paper); color:var(--paper); margin-bottom:18px; display:inline-flex;">&larr; Back to News</a>
    <div class="modal-date" style="color:var(--gold-soft);">{date_display}</div>
    <h1>{title}</h1>
  </div>
</section>
<section>
  <div class="wrap" style="max-width:820px;">
    {gallery_html}
    <p style="white-space: pre-wrap; font-size:1.05rem; margin-top:24px;">{body_text}</p>
    <div style="margin-top:24px; display:flex; gap:12px; flex-wrap:wrap;">
      {cta_html}
      <a href="/news.html" class="btn btn-outline">Back to News</a>
    </div>
  </div>
</section>
'''
    with open(f"output/news/{item['slug']}.html", "w") as f:
        f.write(page(title, body_text[:150], "news.html", event_body))



# ---------------- CONTACT ----------------
contact_body = '''
<section class="page-hero">
  <div class="wrap">
    <h1>Contact Us</h1>
    <p>We'd love to hear from you &mdash; reach out or book a campus tour.</p>
  </div>
</section>
<section>
  <div class="wrap hero-grid">
    <form class="contact-form" action="https://formspree.io/f/mqerwajg" method="POST">
      <input type="hidden" name="_subject" value="New Contact Message - Dominion Group of Schools">
      <input type="hidden" name="_next" value="https://dominiongroupofschools.com/thank-you.html">
      <div>
        <label for="c-name">Full Name</label>
        <input id="c-name" name="name" type="text" required>
      </div>
      <div>
        <label for="c-email">Email</label>
        <input id="c-email" name="email" type="email" required>
      </div>
      <div>
        <label for="c-message">Message</label>
        <textarea id="c-message" name="message" rows="5" required></textarea>
      </div>
      <button type="submit" class="btn btn-primary">Send Message</button>
    </form>
    <div class="card">
      <h3>Visit Us &mdash; College &amp; Nur/Pri Annex</h3>
      <p>1 Dominion School Road, off Hospital Road, Ugboma Layout, Asaba, Delta State</p>
      <h3>Visit Us &mdash; Nursery/Primary School</h3>
      <p>7 Osowe Street, Ogbeosowe, Asaba, Delta State</p>
      <h3>Call Us</h3>
      <p>0705 574 2394</p>
      <h3>Email Us</h3>
      <p>dominiongroupofschools777@gmail.com</p>
      <h3>Office Hours</h3>
      <p>Monday &ndash; Friday, 8:00am &ndash; 3:00pm</p>
    </div>
  </div>
</section>
'''
with open("output/contact.html", "w") as f:
    f.write(page("Contact", "Get in touch with Dominion Group of Schools.", "contact.html", contact_body))

# ---------------- THANK YOU ----------------
thankyou_body = '''
<section class="page-hero">
  <div class="wrap text-center">
    <h1>Thank You</h1>
    <p>We've received your message and will get back to you as soon as possible.</p>
  </div>
</section>
<section class="text-center">
  <div class="wrap">
    <a href="/index.html" class="btn btn-primary">Back to Home</a>
  </div>
</section>
'''
with open("output/thank-you.html", "w") as f:
    f.write(page("Thank You", "Thank you for contacting Dominion Group of Schools.", "", thankyou_body))

# ---------------- Copy static assets ----------------
shutil.copytree("assets", "output/assets", dirs_exist_ok=True)
os.makedirs("output/assets/photos/news-uploads", exist_ok=True)

if os.path.isdir("admin"):
    shutil.copytree("admin", "output/admin", dirs_exist_ok=True)

# ---------------- Sitemap & robots.txt ----------------
pages = [("", "1.0"), ("about.html", "0.8"), ("academics.html", "0.8"),
         ("admissions.html", "0.9"), ("news.html", "0.7"), ("contact.html", "0.7")]
today = date.today().isoformat()
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, priority in pages:
    url = f"{SITE_URL}/{path}" if path else f"{SITE_URL}/"
    lines += ["  <url>", f"    <loc>{url}</loc>", f"    <lastmod>{today}</lastmod>",
              f"    <priority>{priority}</priority>", "  </url>"]
lines.append("</urlset>")
with open("output/sitemap.xml", "w") as f:
    f.write("\n".join(lines))

with open("output/robots.txt", "w") as f:
    f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")

print(f"Build complete. {len(news_items)} news posts included.")
