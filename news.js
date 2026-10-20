const SOURCES = [
  { name: "پرسپولیس نیوز", url: "https://perspolisnews.ir" },
  { name: "ارتش سرخ", url: "https://arteshesorkh.com" },
  { name: "پرسپولیس نیوز", url: "https://www.perspolisnews.ir" },
  { name: "باشگاه پرسپولیس", url: "https://fc-perspolis.com" },
  { name: "قطره", url: "https://www.ghatreh.com" },
  { name: "طرفداری", url: "https://www.tarafdari.com" }
];

async function getNews() {
  return Promise.all(
    SOURCES.map(async (source) => {
      try {
        const response = await fetch(
          `https://api.allorigins.win/raw?url=${encodeURIComponent(source.url)}`,
          { cache: "no-store" }
        );

        if (!response.ok) throw new Error("خطا در دریافت");

        const html = await response.text();
        const doc = new DOMParser().parseFromString(html, "text/html");

        return {
          source: source.name,
          title: doc.querySelector("h1")?.textContent?.trim() || "صفحه خبر",
          url: source.url,
          status: "connected"
        };
      } catch {
        return {
          source: source.name,
          url: source.url,
          status: "error"
        };
      }
    })
  );
}

if (typeof window !== "undefined") {
  window.getPerspolisNewsSources = getNews;
}
