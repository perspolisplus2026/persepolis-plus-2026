(async function () {
  const targets = [
    document.querySelector("#news .news-list"),
    document.querySelector("#ppx-news-list")
  ].filter(Boolean);

  if (!targets.length) return;

  function render(items, updatedAt) {
    targets.forEach(container => {
      container.replaceChildren();

      if (!items.length) {
        container.textContent = "فعلاً خبری دریافت نشده است.";
        return;
      }

      items.forEach(item => {
        const card = document.createElement("article");
        card.style.cssText =
          "padding:12px;margin:8px 0;border-radius:12px;" +
          "border:1px solid rgba(180,20,45,.22);";

        const link = document.createElement("a");
        link.textContent = item.title;
        link.href = item.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.style.cssText =
          "display:block;color:inherit;text-decoration:none;font-weight:700;";

        const source = document.createElement("small");
        source.textContent = "منبع: " + item.source;
        source.style.cssText = "display:block;margin-top:8px;opacity:.7;";

        card.append(link, source);
        container.appendChild(card);
      });

      const stamp = document.createElement("small");
      stamp.textContent = "آخرین به‌روزرسانی: " +
        new Date(updatedAt).toLocaleString("fa-IR");
      stamp.style.cssText = "display:block;margin:12px 0;opacity:.7;";
      container.appendChild(stamp);
    });
  }

  async function loadNews() {
    try {
      const response = await fetch("./news.json?v=" + Date.now(), {
        cache: "no-store"
      });
      if (!response.ok) throw new Error("فایل اخبار هنوز آماده نیست");
      const data = await response.json();
      render(data.news || [], data.updated_at || new Date().toISOString());
    } catch (error) {
      targets.forEach(container => {
        if (!container.children.length) {
          container.textContent =
            "در حال آماده‌سازی اخبار خودکار؛ کمی بعد دوباره امتحان کن.";
        }
      });
      console.error(error);
    }
  }

  await loadNews();
  setInterval(loadNews, 5 * 60 * 1000);
})();
