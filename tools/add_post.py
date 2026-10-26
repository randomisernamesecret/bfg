#!/usr/bin/env python3
"""Wire a new blog post (already written in blog/ and all five locale blog/ dirs)
into the site: top of each homepage's blog list, sitemap.xml, feed.xml, the
relative "Updated" date line, and llms.txt / llms-full.txt.

    python3 tools/add_post.py <file-name.html> [<category data-cat>]

Category defaults to the post's breadcrumb tag (tag-games -> games). Idempotent.
"""
import datetime, html, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://bfgapps.co"
LOCALES = ["", "de/", "es/", "fr/", "ja/", "zh-CN/"]


def read(p):
    return open(os.path.join(ROOT, p), encoding="utf-8").read()


def write(p, s):
    open(os.path.join(ROOT, p), "w", encoding="utf-8").write(s)


def main(name, cat=None):
    en = read("blog/" + name)
    cat = cat or re.search(r'class="tag tag-([a-z-]+)"', en).group(1)
    art = next(json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', en, re.S)
               if '"Article"' in m)
    date = art["datePublished"]

    for loc in LOCALES:
        post = read(f"{loc}blog/{name}")
        title = html.unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", post, re.S).group(1))).strip()
        home = read(f"{loc}index.html")
        if f'href="blog/{name}"' not in home:
            label = re.search(rf'<li data-cat="{cat}">.*?<span class="meta">([^<]*)</span>', home).group(1)
            li = f'        <li data-cat="{cat}"><a href="blog/{name}">{html.escape(title, quote=False)}</a><span class="meta">{label}</span></li>\n'
            home = re.sub(r'(<ul class="blog-list">\n)', lambda m: m.group(1) + li, home, count=1)
            write(f"{loc}index.html", home)

    sm = read("sitemap.xml")
    for loc in LOCALES:
        url = f"{SITE}/{loc}blog/{name}"
        if f"<loc>{url}</loc>" in sm:
            continue
        line = f'  <url><loc>{url}</loc><lastmod>{date}</lastmod><changefreq>monthly</changefreq><priority>{"0.8" if not loc else "0.7"}</priority></url>\n'
        first = re.search(rf"  <url><loc>{re.escape(SITE)}/{re.escape(loc)}blog/[^<]+</loc>", sm)
        sm = sm[:first.start()] + line + sm[first.start():] if first else sm.replace("</urlset>", line + "</urlset>")
    write("sitemap.xml", sm)

    feed = read("feed.xml")
    if f"<link>{SITE}/blog/{name}</link>" not in feed:
        desc = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', en).group(1))
        when = datetime.datetime.strptime(date, "%Y-%m-%d").replace(hour=9).strftime("%a, %d %b %Y %H:%M:%S GMT")
        item = (f"    <item>\n      <title><![CDATA[{art['headline']}]]></title>\n"
                f"      <link>{SITE}/blog/{name}</link>\n      <guid>{SITE}/blog/{name}</guid>\n"
                f"      <description><![CDATA[{desc}]]></description>\n      <pubDate>{when}</pubDate>\n    </item>\n")
        feed = re.sub(r"(<atom:link [^>]*/>\n)", lambda m: m.group(1) + item, feed, count=1)
        feed = re.sub(r"<lastBuildDate>[^<]*</lastBuildDate>", f"<lastBuildDate>{when}</lastBuildDate>", feed, count=1)
        write("feed.xml", feed)

    for tool in ("blog_dates.py", "build_llms.py"):
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", tool)], check=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
