#!/usr/bin/env python3
"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver; Bing feeds ChatGPT
search and Copilot) which pages changed, so they re-crawl in hours, not weeks.

The key is the hex-named .txt file at the site root; it must be live before pinging.
Run after a push has deployed:
    python3 tools/indexnow.py                # URLs of files changed in the last commit
    python3 tools/indexnow.py HEAD~5         # URLs changed since that commit
    python3 tools/indexnow.py --all          # every URL in sitemap.xml
"""
import glob, json, os, re, subprocess, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "bfgapps.co"
KEY_FILE = next(f for f in glob.glob(os.path.join(ROOT, "*.txt")) if re.fullmatch(r"[0-9a-f]{32}\.txt", os.path.basename(f)))
KEY = open(KEY_FILE).read().strip()


def sitemap_urls():
    return re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(ROOT, "sitemap.xml")).read())


def changed_urls(since):
    names = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", since, "HEAD"],
                           capture_output=True, text=True, check=True).stdout.split()
    live = set(sitemap_urls())
    urls = []
    for n in names:
        url = f"https://{HOST}/" + re.sub(r"(^|/)index\.html$", r"\1", n)
        if url in live:
            urls.append(url)
    return urls


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "HEAD~1"
    urls = sitemap_urls() if arg == "--all" else changed_urls(arg)
    if not urls:
        print("No sitemap URLs changed.")
        return
    for i in range(0, len(urls), 10000):
        body = json.dumps({"host": HOST, "key": KEY, "keyLocation": f"https://{HOST}/{KEY}.txt",
                           "urlList": urls[i:i + 10000]}).encode()
        req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                     headers={"Content-Type": "application/json; charset=utf-8",
                                              "User-Agent": "bfgapps-indexnow/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow: {r.status} for {len(urls[i:i + 10000])} URLs")


if __name__ == "__main__":
    main()
