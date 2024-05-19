import finnhub
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()
finnhub_token = os.getenv("FINNHUB_TOKEN")
finnhub_client = finnhub.Client(api_key=finnhub_token)

def get_news(ticker):
    try:
        today_date = datetime.today().strftime('%Y-%m-%d')
        one_week_ago = datetime.today() - timedelta(days=7)
        one_week_ago_date = one_week_ago.strftime('%Y-%m-%d')
        news_data = finnhub_client.company_news(ticker, _from=one_week_ago_date, to=today_date)

        articles = []
        for i, article in enumerate(news_data):
            if i >= 2:
                break

            headline = article['headline']
            summary = article['summary']
            url = article['url']

            articles.append(f" {headline}\n\n {summary}\n\n {url}\n")

        return "\n\n".join(articles)

    except Exception as e:
        return f"Error fetching news: {e}"

def get_market_news():
    try:
        news_data = finnhub_client.general_news('general', min_id=0)

        articles = []
        for i, article in enumerate(news_data):
            if i >= 10:
                break

            headline = article['headline']
            summary = article['summary']
            url = article['url']

            if "cnbc.com" not in url.lower():
                articles.append(f" {headline}\n\n {summary}\n\nURL: {url}\n\n")


        return "\n\n".join(articles)

    except Exception as e:
        return f"Error fetching news: {e}"
