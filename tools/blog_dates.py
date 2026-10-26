#!/usr/bin/env python3
"""Blog meta line: show the last-updated date (relative, via /reldate.js).

For every post in blog/ and <locale>/blog/: makes sure the Article JSON-LD has
dateModified (falls back to datePublished), and rewrites the first part of
<p class="meta"> to <time class="rel-date" datetime=... data-kind=...> with the
full localized date as static text. Idempotent; run after adding a post or
changing a post's dateModified:
    python3 tools/blog_dates.py
"""
import glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONTHS = {
    "en": "January February March April May June July August September October November December".split(),
    "de": "Januar Februar März April Mai Juni Juli August September Oktober November Dezember".split(),
    "es": "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split(),
    "fr": "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split(),
}
LABEL = {
    "en": ("Updated {d}", "Published {d}"), "de": ("Aktualisiert am {d}", "Veröffentlicht am {d}"),
    "es": ("Actualizado el {d}", "Publicado el {d}"), "fr": ("Mis à jour le {d}", "Publié le {d}"),
    "ja": ("{d}に更新", "{d}に公開"), "zh": ("{d}更新", "{d}发布"),
}


def fmt(iso, lang):
    y, m, d = (int(x) for x in iso.split("-"))
    if lang in ("ja", "zh"):
        return f"{y}年{m}月{d}日"
    if lang == "en":
        return f"{d} {MONTHS['en'][m - 1]} {y}"
    if lang == "de":
        return f"{d}. {MONTHS['de'][m - 1]} {y}"
    if lang == "es":
        return f"{d} de {MONTHS['es'][m - 1]} de {y}"
    return f"{d} {MONTHS['fr'][m - 1]} {y}"


def process(path, lang):
    s = open(path, encoding="utf-8").read()
    if 'http-equiv="refresh"' in s:
        return False
    orig = s
    m = re.search(r'("datePublished":\s*"(\d{4}-\d{2}-\d{2})")(,?\s*"dateModified":\s*"(\d{4}-\d{2}-\d{2})")?', s)
    if not m:
        print("no datePublished:", path)
        return False
    published, modified = m.group(2), m.group(4)
    if not modified:
        modified = published
        sep = ",\n    " if "\n" in s[m.start() - 40:m.start()] else ","
        s = s[:m.end(1)] + f'{sep}"dateModified": "{modified}"' + s[m.end(1):]
    kind = "updated" if modified > published else "published"
    label = LABEL[lang][0 if kind == "updated" else 1].format(d=fmt(modified, lang))
    stamp = f'<time class="rel-date" datetime="{modified}" data-kind="{kind}">{label}</time>'
    s = re.sub(r'(<p class="meta">)(?:<time class="rel-date"[^>]*>[^<]*</time>|[^·<]*?)(\s*·)',
               lambda mm: mm.group(1) + stamp + mm.group(2), s, count=1)
    if "/reldate.js" not in s:
        s = s.replace('  <script src="/nav.js"></script>', '  <script src="/nav.js"></script>\n  <script src="/reldate.js" defer></script>', 1)
    if s != orig:
        open(path, "w", encoding="utf-8").write(s)
        return True
    return False


n = 0
for loc, lang in [("", "en"), ("de/", "de"), ("es/", "es"), ("fr/", "fr"), ("ja/", "ja"), ("zh-CN/", "zh")]:
    for f in sorted(glob.glob(os.path.join(ROOT, loc + "blog", "*.html"))):
        n += process(f, lang)
print("updated", n, "posts")
