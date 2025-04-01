import feedparser

# RSS-ленты новостных сайтов
RSS_FEEDS = "https://lenta.ru/rss"

# Файлы
SITES_FILE = "sites.txt"

# Получаем ссылки из RSS
all_links = set()

feed = feedparser.parse(RSS_FEEDS)
for entry in feed.entries:
    if len(all_links) >= 120:
        break
    all_links.add(entry.link)

# Сохраняем ссылки в файл
with open(SITES_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(list(all_links)))
