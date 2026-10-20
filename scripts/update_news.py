import json, re, requests
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

SOURCES = [
    ("پرسپولیس نیوز", "https://perspolisnews.ir"),
    ("ارتش سرخ", "https://arteshesorkh.com"),
    ("طرفداری", "https://www.tarafdari.com"),
    ("قطره", "https://www.ghatreh.com"),
    ("باشگاه پرسپولیس", "https://fc-perspolis.com"),
]

PERSPOLIS = re.compile(r"پرسپولیس|پرسپوليسي|پیروزی|ارتش سرخ|سرخپوشان|سرخ پوشان|قرمزپوشان|قرمز پوشان", re.I)
SPORT = re.compile(
    r"پرسپولیس|پرسپوليسي|ارتش سرخ|فوتبال|لیگ|بازیکن|مربی|دروازه.?بان|"
    r"استقلال|تراکتور|سپاهان|ملوان|تیم ملی|جام حذفی|قهرمانی|"
    r"نقل.?انتقال|مسابقه|دیدار|بازی|گلزنی|گل|جدول|امتیاز|"
    r"رئال مادرید|بارسلونا|منچست|لیورپول|بایرن|یوونتوس|"
    r"champions league|football|soccer|perspolis",
    re.I
)
BLOCK = re.compile(
    r"سیاست|انتخابات|مجلس|دولت|وزیر|رئیس.?جمهور|جنگ|"
    r"قیمت دلار|قیمت طلا|زلزله|آب.?وهوا|بورس|"
    r"ورود|ثبت.?نام|تبلیغات|استخدام|آشپزی",
    re.I
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 11) AppleWebKit/537.36 Chrome/130 Mobile Safari/537.36"
}

all_news, failed = [], []

for source, base in SOURCES:
    found, seen = [], set()
    try:
        response = requests.get(base, headers=HEADERS, timeout=25)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding
        soup = BeautifulSoup(response.text, "html.parser")
        host = (urlparse(base).hostname or "").lower()

        for a in soup.select("article a[href], h1 a[href], h2 a[href], h3 a[href], a[href]"):
            title = " ".join(a.get_text(" ", strip=True).split())
            if not title and a.find("img"):
                title = a.find("img").get("alt", "").strip()

            url = urljoin(base, a.get("href", ""))
            parsed = urlparse(url)
            linkhost = (parsed.hostname or "").lower()

            if len(title) < 12 or len(title) > 220:
                continue
            if parsed.scheme not in ("http", "https"):
                continue
            if linkhost != host and not linkhost.endswith("." + host):
                continue
            if url.rstrip("/") == base.rstrip("/"):
                continue
            if re.search(r"login|register|search|contact|category|tag|author|javascript:|mailto:", url, re.I):
                continue
            if not PERSPOLIS.search(title) or BLOCK.search(title):
                continue

            key = re.sub(r"\W+", "", title).lower()
            if key in seen:
                continue
            seen.add(key)
            found.append({
                "title": title,
                "url": url,
                "source": source
            })
            if len(found) >= 15:
                break

        print(f"{source}: {len(found)} خبر مرتبط")
        all_news.extend(found)

    except Exception as e:
        failed.append(source)
        print(f"{source}: دریافت نشد ({e})")

unique, seen_titles = [], set()
for item in all_news:
    key = re.sub(r"\W+", "", item["title"]).lower()
    if key and key not in seen_titles:
        seen_titles.add(key)
        unique.append(item)

if not unique:
    raise SystemExit("خبر فوتبالی پیدا نشد؛ فایل قبلی دست‌نخورده باقی ماند.")

data = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "sources": len(SOURCES),
    "failed_sources": failed,
    "news": unique[:60]
}
with open("news.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nتمام شد: {len(unique[:60])} خبر مرتبط ذخیره شد.")
print("منابع ناموفق:", ", ".join(failed) if failed else "هیچ‌کدام")
