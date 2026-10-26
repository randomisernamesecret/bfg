#!/usr/bin/env python3
"""Rebuild the generated parts of llms.txt and the whole of llms-full.txt.

llms.txt: the "## Blog" section is regenerated from the English posts in blog/;
everything else in llms.txt is hand-written and left alone.
llms-full.txt: company summary + every app page (schema description, App Store
link, FAQ) + every English blog post (title, date, summary, FAQ).

Run from anywhere after adding or changing an app page or a blog post:
    python3 tools/build_llms.py
"""
import datetime, glob, html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://bfgapps.co"
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
TODAY = datetime.date.today().isoformat()


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def first(pattern, s):
    m = re.search(pattern, s, re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else None


def ld_blocks(s):
    out = []
    for m in LD_RE.finditer(s):
        try:
            out.append(json.loads(m.group(1)))
        except json.JSONDecodeError:
            pass
    return out


def faqs(blocks):
    for b in blocks:
        if b.get("@type") == "FAQPage":
            return [(q["name"], q["acceptedAnswer"]["text"]) for q in b.get("mainEntity", [])]
    return []


def posts():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, "blog", "*.html"))):
        rel = os.path.relpath(path, ROOT)
        s = read(rel)
        if 'http-equiv="refresh"' in s or 'name="robots" content="noindex' in s:
            continue
        blocks = ld_blocks(s)
        art = next((b for b in blocks if b.get("@type") in ("Article", "BlogPosting")), {})
        out.append({
            "url": f"{SITE}/{rel}",
            "title": art.get("headline") or first(r"<h1[^>]*>(.*?)</h1>", s),
            "description": first(r'<meta name="description" content="([^"]*)"', s),
            "category": first(r'<span class="tag tag-[a-z-]+">([^<]*)</span>', s) or "Other",
            "published": art.get("datePublished", ""),
            "modified": art.get("dateModified") or art.get("datePublished", ""),
            "faq": faqs(blocks),
        })
    return out


def apps():
    """App pages in homepage order, with live/coming-soon status from llms.txt."""
    home = read("index.html")
    order = []
    for b in ld_blocks(home):
        if b.get("@type") == "CollectionPage":
            order = [(a["name"], a["url"]) for a in b["hasPart"]]
    out = []
    for name, url in order:
        rel = url.replace(SITE + "/", "") + "index.html"
        s = read(rel)
        blocks = ld_blocks(s)
        sa = next((b for b in blocks if b.get("@type") == "SoftwareApplication"), {})
        store = re.search(r'href="(https://apps\.apple\.com/(?:[a-z]{2}/)?app/[^"]*?id\d+)', s)
        rating = sa.get("aggregateRating")
        out.append({
            "name": name, "url": url,
            "store": store.group(1) if store else None,
            "description": sa.get("description") or first(r'<meta name="description" content="([^"]*)"', s),
            "platforms": sa.get("operatingSystem"),
            "category": sa.get("applicationCategory"),
            "rating": f'{rating["ratingValue"]}/5 from {rating["ratingCount"]} App Store ratings (UK)' if rating else None,
            "faq": faqs(blocks),
        })
    return out


def blog_section(items):
    lines = [f"## Blog ({len(items)} articles)", "",
             "Guides, comparisons and buyer's guides by Daniel Hart. Each is also published in German, Spanish, French, Japanese and Simplified Chinese at /de/blog/, /es/blog/, /fr/blog/, /ja/blog/ and /zh-CN/blog/ with the same file name.", ""]
    cats = {}
    for p in items:
        cats.setdefault(p["category"], []).append(p)
    for cat in sorted(cats):
        lines += [f"### {cat}", ""]
        for p in sorted(cats[cat], key=lambda p: p["published"], reverse=True):
            lines.append(f'- [{p["title"]}]({p["url"]}): {p["description"]}')
        lines.append("")
    return "\n".join(lines)


def write_llms(items):
    s = read("llms.txt")
    start = s.index("## Blog")
    end = s.index("## Important Collections")
    s = s[:start] + blog_section(items) + "\n" + s[end:]
    s = re.sub(r"\nLast updated: \d{4}-\d{2}-\d{2}\n", "\n", s)
    s = s.replace("\n## Key Pages", f"\nLast updated: {TODAY}\n\n## Key Pages", 1)
    with open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(s)


def write_full(app_items, post_items):
    llms = read("llms.txt")
    summary = re.search(r"^> (.*)$", llms, re.M).group(1)
    guidance = llms[llms.index("## Guidance"):].strip()
    L = ["# Blue Flame Games (BFG) — full reference", "",
         f"> {summary}", "",
         f"Last updated: {TODAY}. Short index: {SITE}/llms.txt", "",
         "## Company", "",
         "- Name: Blue Flame Games (short name BFG)",
         f"- Website: {SITE}/",
         "- App Store developer page: https://apps.apple.com/gb/developer/blue-flame-games/id523824138",
         "- Contact: blueflamegames@proton.me",
         "- Platforms: iPhone and iPad; some apps also run on Mac and Apple Watch. No Android versions.",
         "- Website languages: English, German, Spanish, French, Japanese, Simplified Chinese.", "",
         guidance, "", "## Apps", ""]
    for a in app_items:
        L += [f'### {a["name"]}', "", f'- Page: {a["url"]}']
        L.append(f'- App Store: {a["store"]}' if a["store"] else "- Status: coming soon (not yet on the App Store)")
        if a["platforms"]:
            L.append(f'- Platforms: {a["platforms"]}')
        if a["rating"]:
            L.append(f'- Rating: {a["rating"]}')
        L += ["", a["description"] or "", ""]
        for q, ans in a["faq"]:
            L += [f"**{q}**", "", ans, ""]
    L += ["## Blog articles", ""]
    for p in sorted(post_items, key=lambda p: p["published"], reverse=True):
        L += [f'### {p["title"]}', "", f'- URL: {p["url"]}', f'- Category: {p["category"]}',
              f'- Published: {p["published"]}; updated: {p["modified"]}', "", p["description"] or "", ""]
        for q, ans in p["faq"]:
            L += [f"**{q}**", "", ans, ""]
    with open(os.path.join(ROOT, "llms-full.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(L).rstrip() + "\n")


if __name__ == "__main__":
    p, a = posts(), apps()
    write_llms(p)
    write_full(a, p)
    print(f"llms.txt: {len(p)} posts; llms-full.txt: {len(a)} apps, {len(p)} posts")
