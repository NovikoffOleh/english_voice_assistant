from datetime import datetime, timedelta
import time
import feedparser

REUTERS_RSS = "https://feeds.reuters.com/reuters/topNews"
BBC_RSS = "http://feeds.bbci.co.uk/news/rss.xml"
CNN_RSS = "http://rss.cnn.com/rss/edition.rss"

def fetch_news(language="en", limit=6, max_age_hours=12):
    news_items = []
    try:
        if language != "en":
            return [f"⚠️ News for language '{language}' is not supported yet."]

        feeds = [
            feedparser.parse(REUTERS_RSS),
            feedparser.parse(CNN_RSS),
            feedparser.parse(BBC_RSS)
        ]

        now = datetime.utcnow()
        threshold = now - timedelta(hours=max_age_hours)
        seen_titles = set()

        for feed in feeds:
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                published = entry.get("published_parsed")

                if not title or title in seen_titles or not published:
                    continue

                entry_time = datetime.fromtimestamp(time.mktime(published))
                if entry_time < threshold:
                    continue  # старі новини

                seen_titles.add(title)
                news_items.append(f"• {title}\n{link}")

                if len(news_items) >= limit:
                    return news_items

        return news_items if news_items else ["⚠️ No fresh news found."]
    except Exception as e:
        return [f"⚠️ Failed to fetch news: {e}"]

# Test local run
if __name__ == "__main__":
    print("\n\n".join(fetch_news("en")))
