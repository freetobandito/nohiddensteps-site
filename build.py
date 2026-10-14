#!/usr/bin/env python3
"""Build the No Hidden Steps video site from videos.json into _site/.

Every video gets its own page at /<slug>/ so the QR code in the book can point to
https://nohiddensteps.com/<slug> forever. The YouTube ID only lives in videos.json:
re-shoot a video or switch hosts, change one line, and every printed QR code still works.
"""
import html, json, os, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "_site")
DATA = json.load(open(os.path.join(ROOT, "videos.json"), encoding="utf-8"))
SITE = DATA["site"]
VIDEOS = sorted(DATA["videos"], key=lambda v: v["title"].lower())
E = html.escape

HEAD = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#f5ede2">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,600;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}static/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='15' fill='%23b8462a'/%3E%3Ctext x='16' y='21.5' font-size='16' font-family='Arial' font-weight='700' fill='%23f5ede2' text-anchor='middle'%3E1%3C/text%3E%3C/svg%3E">
</head><body>
<header class="top"><div class="wrap"><a class="brand" href="{root}">No Hidden Steps</a><a class="toplink" href="{book}">Get the book</a></div></header>
<main>
"""

def foot(root):
    return f"""</main>
<footer class="foot">
  <p><a href="{root}">All technique videos</a> · <a href="{book_href(root)}">Get the book</a></p>
  <p class="small">No Hidden Steps: A Cookbook for People Who Say They Can't Cook · Aaron McNeal</p>
</footer>
</body></html>"""

def book_href(root):
    """Where every "Get the book" button goes.
    Only a Lulu link set -> straight to Lulu. Both Lulu and Amazon -> the /book/ page with both buttons.
    No links yet -> the /book/ page, which says the book is in testing."""
    links = SITE.get("book_links", {})
    if links.get("lulu") and not links.get("amazon"):
        return E(links["lulu"])
    return f"{root}book/"

def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(text)

def video_page(v):
    root = "../"
    vid = v.get("youtube_id", "").strip()
    if vid:
        player = f"""<div class="player"><iframe src="https://www.youtube-nocookie.com/embed/{E(vid)}?rel=0&amp;playsinline=1"
  title="{E(v['title'])}" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>
<p class="yt"><a href="https://www.youtube.com/watch?v={E(vid)}">Video not playing? Watch it on YouTube</a></p>"""
    else:
        player = """<div class="player soon"><div><span class="badge">Video coming soon</span>
<p>The quick recap below has the key points, and the book has every step.</p></div></div>"""
    recap = ""
    if v.get("recap"):
        items = "".join(f"<li>{E(r)}</li>" for r in v["recap"])
        recap = f'<section class="recap"><h2>Quick recap</h2><ol>{items}</ol></section>'
    used = ", ".join(E(u) for u in v.get("used_in", []))
    body = f"""<article class="video">
<p class="kicker">Technique video</p>
<h1>{E(v['title'])}</h1>
{player}
{recap}
<p class="used">In the book: {used}</p>
<aside class="book-cta"><p>Every recipe, every step, nothing assumed.</p><a class="btn" href="{book_href(root)}">Get the book</a></aside>
</article>"""
    head = HEAD.format(title=E(f"{v['title']} · No Hidden Steps"), desc=E(f"Short technique video: {v['title']}."), root=root, book=book_href(root))
    write(os.path.join(OUT, v["slug"], "index.html"), head + body + foot(root))

def index_page():
    parts = SITE.get("parts", {})
    groups = ""
    for num in sorted({v.get("part", 9) for v in VIDEOS}):
        vs = [v for v in VIDEOS if v.get("part", 9) == num]
        items = "".join(
            f'<li data-q="{E((v["title"] + " " + " ".join(v.get("used_in", []))).lower())}"><a href="{E(v["slug"])}/">'
            f'<span class="t">{E(v["title"])}</span>'
            + ('<span class="tag ok">video</span>' if v.get("youtube_id") else '<span class="tag">recap</span>')
            + "</a></li>" for v in vs)
        groups += f'<section class="group"><h3>Part {num} · {E(parts.get(str(num), ""))}</h3><ul class="videos">{items}</ul></section>'
    body = f"""<section class="hero">
<p class="kicker">The cookbook for people who say they can't cook</p>
<h1>No Hidden Steps</h1>
<p class="lede">Most recipes leave out the steps experienced cooks don't think about. This book doesn't.
These short videos show the techniques that are easier to see than to read.</p>
<a class="btn" href="{book_href("")}">Get the book</a>
</section>
<section class="list"><h2>Technique videos</h2>
<p class="small">Scanned a QR code in the book? It brought you straight to the right one. Here's the full list, in book order.</p>
<input id="q" class="search" type="search" placeholder="Search techniques or recipes" aria-label="Search techniques or recipes" autocomplete="off">
<div id="groups">{groups}</div>
<p id="none" class="small" hidden>Nothing matches that. Try a recipe name, like "roux" or "pancakes".</p>
</section>
<script>
(function(){{var q=document.getElementById('q'),none=document.getElementById('none');
q.addEventListener('input',function(){{var t=q.value.trim().toLowerCase(),any=false;
document.querySelectorAll('.group').forEach(function(g){{var shown=0;
g.querySelectorAll('li').forEach(function(li){{var m=!t||li.dataset.q.indexOf(t)>-1;li.hidden=!m;if(m)shown++;}});
g.hidden=shown===0;if(shown)any=true;}});none.hidden=any;}});}})();
</script>"""
    write(os.path.join(OUT, "index.html"), HEAD.format(title="No Hidden Steps", desc="Technique videos for No Hidden Steps, a cookbook for people who say they can't cook.", root="", book=book_href("")) + body + foot(""))

def book_page():
    links = SITE.get("book_links", {})
    buttons = ""
    if links.get("lulu"):
        buttons += (f'<div class="edition"><h3>Kitchen Edition</h3><p>Coil-bound so it lies flat on the counter. Full color.</p>'
                    f'<a class="btn" href="{E(links["lulu"])}">Buy on Lulu</a></div>')
    if links.get("amazon"):
        buttons += (f'<div class="edition"><h3>Hardcover</h3><p>A sturdy keepsake edition for the shelf. Full color.</p>'
                    f'<a class="btn ghost" href="{E(links["amazon"])}">Buy on Amazon</a></div>')
    if not buttons:
        buttons = '<p class="soonnote">The book is in testing now. Check back soon.</p>'
    body = f"""<section class="hero">
<p class="kicker">Book 1 · Foundations</p>
<h1>No Hidden Steps</h1>
<p class="sub">A Cookbook for People Who Say They Can't Cook</p>
<p class="lede">Every recipe on one two-page spread: get everything ready on the left, cook on the right.
What "done" looks, smells and sounds like at every step. From pancakes to a full Sunday dinner.</p>
<div class="editions">{buttons}</div>
</section>"""
    write(os.path.join(OUT, "book", "index.html"), HEAD.format(title="Get the book · No Hidden Steps", desc="Get No Hidden Steps.", root="../", book=book_href("../")) + body + foot("../"))

def not_found():
    body = """<section class="hero"><h1>Page not found</h1>
<p class="lede">That link may have changed. Every technique video is listed on the home page.</p>
<a class="btn" href="/">See all videos</a></section>"""
    write(os.path.join(OUT, "404.html"), HEAD.format(title="Not found · No Hidden Steps", desc="", root="/", book=book_href("/")) + body + foot("/"))

if __name__ == "__main__":
    shutil.rmtree(OUT, ignore_errors=True)
    shutil.copytree(os.path.join(ROOT, "static"), os.path.join(OUT, "static"))
    for v in VIDEOS:
        video_page(v)
    index_page(); book_page(); not_found()
    if SITE.get("domain_live"):
        write(os.path.join(OUT, "CNAME"), SITE["domain"] + "\n")
    print(f"Built {len(VIDEOS)} video pages into _site/")
