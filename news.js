
const SOURCES = [
  { name: "پرسپولیس نیوز", url: "https://perspolisnews.ir" },
  { name: "ارتش سرخ", url: "https://arteshesorkh.com" },
  { name: "طرفداری", url: "https://www.tarafdari.com" },
  { name: "قطره", url: "https://www.ghatreh.com" },
  { name: "باشگاه پرسپولیس", url: "https://fc-perspolis.com" }
];

async function loadNews() {
  const container = document.querySelector("#news .news-list");
  if (!container) return;

  container.innerHTML = "<p>در حال دریافت اخبار...</p>";

  const results = await Promise.allSettled(
    SOURCES.map(async source => {
      const api =
        "https://api.allorigins.win/raw?url=" +
        encodeURIComponent(source.url);

      const response = await fetch(api);
      if (!response.ok) throw new Error("دریافت ناموفق");

      const html = await response.text();
      const doc = new DOMParser().parseFromString(html, "text/html");

      const links = [...doc.querySelectorAll("a[href]")]
        .filter(a => a.querySelector("img") === null)
        .map(a => ({
          title: a.textContent.trim().replace(/\s+/g, " "),
          url: a.href
        }))
        .filter(a => a.title.length > 20 && /^https?:/.test(a.url))
        .slice(0, 5);

      return { source, links };
    })
  );

  const items = [];

  results.forEach(result => {
    if (result.status !== "fulfilled") return;

    result.value.links.forEach(item => {
      items.push({
        ...item,
        source: result.value.source.name
      });
    });
  });

  if (!items.length) {
    container.innerHTML =
      "<p>فعلاً دریافت اخبار ممکن نیست. اتصال منابع را بعداً بررسی می‌کنیم.</p>";
    return;
  }

  container.innerHTML = "";

  items.slice(0, 20).forEach(item => {
    const article = document.createElement("p");
    const link = document.createElement("a");

    link.textContent = item.title;
    link.href = item.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";

    const source = document.createElement("small");
    source.textContent = " — " + item.source;

    article.append(link, source);
    container.appendChild(article);
  });
}

loadNews();
setInterval(loadNews, 15 * 60 * 1000);

