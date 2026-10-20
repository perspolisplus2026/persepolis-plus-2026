import json, os, re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

SOURCES = [
    ("پرسپولیس نیوز", "https://perspolisnews.ir"),
    ("ارتش سرخ", "https://arteshesorkh.com"),
    ("طرفداری", "https://www.tarafdari.com"),
    ("قطره", "https://www.ghatreh.com"),
    ("باشگاه پرسپولیس", "https://fc-perspolis.com"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"
}
BLOCK = re.compile(
    r"login|register|signup|search|contact|about|privacy|"
    r"category|tag|author|wp-content|javascript:|mailto:|"
    r"telegram|instagram|facebook|twitter",
    re.I,
)

def collect(name, base):
    response = requests.get(base, headers=HEADERS, timeout=25)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or response.encoding
    soup = BeautifulSoup(response.text, "html.parser")
    host = urlparse(base).hostname
    found, seen = [], set()

    for a in soup.select("article a[href], h1 a[href], h2 a[href], h3 a[href], a[href]"):
        title = " ".join(a.get_text(" ", strip=True).split())
        href = urljoin(base, a.get("href", ""))
        parsed = urlparse(href)

        if not title and a.find("img"):
            title = a.find("img").get("alt", "").strip()

        if len(title) < 18 or len(title) > 220:
            continue
        if not parsed.hostname or parsed.scheme not in ("http", "https"):
            continue
        if parsed.hostname != host and not parsed.hostname.endswith("." + host):
            continue
        if href.rstrip("/") == base.rstrip("/"):
            continue
        if BLOCK.search(parsed.path + " " + parsed.query):
            continue
        if href in seen:
            continue

        seen.add(href)
        found.append({
            "title": title,
            "url": href,
            "source": name
        })
        if len(found) >= 10:
            break

    print(f"{name}: {len(found)} خبر")
    return found

all_news, failed = [], []

for name, url in SOURCES:
    try:
        all_news.extend(collect(name, url))
    except Exception as exc:
        failed.append(name)
        print(f"خطا در {name}: {exc}")

# اگر همه منابع شکست خوردند، خبرهای قبلی را حفظ کن.
if not all_news:
    raise SystemExit("هیچ خبری دریافت نشد؛ فایل قبلی حفظ شد.")

seen_titles, unique = set(), []
for item in all_news:
    key = re.sub(r"\W+", "", item["title"]).lower()
    if key and key not in seen_titles:
        seen_titles.add(key)
        unique.append(item)

data = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "sources": len(SOURCES),
    "failed_sources": failed,
    "news": unique[:40]
}

with open("news.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"ذخیره شد: {len(data['news'])} خبر؛ منابع ناموفق: {len(failed)}")
