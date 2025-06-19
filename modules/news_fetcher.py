# modules/news_fetcher.py

import feedparser

# Основні RSS-джерела англійською мовою
REUTERS_RSS = "https://feeds.reuters.com/reuters/topNews"
CNN_RSS = "http://rss.cnn.com/rss/edition.rss"

def fetch_news(language="en", limit=6):
    news_items = []

    try:
        if language != "en":
            return [f"⚠️ News for language '{language}' is not supported yet."]

        # Завантаження фідів
        feed_reuters = feedparser.parse(REUTERS_RSS)
        feed_cnn = feedparser.parse(CNN_RSS)

        # Обʼєднання фідів без дублів (за заголовками)
        combined_entries = feed_reuters.entries + feed_cnn.entries
        seen_titles = set()

        for entry in combined_entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()

            if not title or title in seen_titles:
                continue

            seen_titles.add(title)
            news_items.append(f"• {title}\n{link}")

            if len(news_items) >= limit:
                break

        if not news_items:
            return ["⚠️ No news found at the moment. Try again later."]

        return news_items

    except Exception as e:
        return [f"⚠️ Failed to fetch news: {e}"]

# Тестування локально
if __name__ == "__main__":
    print("\n\n".join(fetch_news("en")))
