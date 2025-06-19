# modules/news_fetcher.py
import feedparser

# Основні RSS-джерела англійською
REUTERS_RSS = "https://feeds.reuters.com/reuters/topNews"
CNN_RSS = "http://rss.cnn.com/rss/edition.rss"

def fetch_news(language="en", limit=6):
    news_items = []

    try:
        # Підтримка лише англійської (можна додати інші мови пізніше)
        if language == "en":
            
            feed_reuters = feedparser.parse(REUTERS_RSS)
            feed_cnn = feedparser.parse(CNN_RSS)
            combined_entries = feed_cnn.entries[:limit//6] + feed_reuters.entries[:limit//5] + feed_cnn.entries[:limit//5]
        else:
            return [f"⚠️ News for language '{language}' is not supported in this version."]

        for entry in combined_entries[:limit]:
            title = entry.get("title", "(no title)")
            link = entry.get("link", "")
            news_items.append(f"• {title}\n{link}")

        return news_items

    except Exception as e:
        return [f"⚠️ Failed to fetch news: {e}"]

# Для тесту
if __name__ == "__main__":
    print("\n".join(fetch_news("en")))
