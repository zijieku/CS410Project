import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
# from bs4.element import Comment
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# define API keys here
STOCKNEWSAPI_KEY = 'h369abgt0vvwxlsqbediutienyp7raeskw5xpvhj'
STOCKNEWSAPI_URL = 'https://stocknewsapi.com/api/v1'


INCLUDE_SRC = {
    'Seeking Alpha'
    #, 
    # 'Forbes'
    # 'Benzinga', 'Business Insider', 'Fox Business',
    # 'Investors Business Daily', 'The Motley Fool', 'Reuters',
    # 'New York Times', 'Yahoo Finance', 'Zacks Investment Research',
    # 'The Street', 'Market Watch'
}

target_url = [
    'https://seekingalpha.com/article/4311754-apple-3-biggest-current-risks',
    'https://seekingalpha.com/article/4297018-apple-changes-strategy-one-cheap-iphone-rule'
]

def get_stock_news (stocks, today=False):
    news = dict()
    for s in stocks:
        news.update(get_single_stock_news(s, today))
    return news


def get_single_stock_news (ticker, today=False):
    '''
    Get last 30 days news for all of the tickers
    '''
    start_date = datetime.strftime(datetime.now() - timedelta(63), '%m%d%Y')
    end_date = datetime.strftime(datetime.now() - timedelta(3), '%m%d%Y')
    PARAMS = {
        'date': 'today' if today else start_date + '-' + end_date,
        'token': STOCKNEWSAPI_KEY, 'items': 50,
        'tickers': ticker, 'source': ','.join(INCLUDE_SRC), 
        'type':'article'
    }
    r = requests.get(url=STOCKNEWSAPI_URL, params=PARAMS)
    # print(r.url)
    if r.status_code != 200:
        raise Exception('invalid STOCKNEWS API request to get stock news')
    news = dict()
    sentiment = {'Positive': 0, 'Neutral':1, 'Negative': 2}
    for s in r.json()['data']:
        data = {
            'source_name': s['source_name'],
            'news_url': s['news_url'],
            'title': s['title'],
            'sentiment': sentiment[s['sentiment']]
        }
        if ticker not in news:
            news[ticker] = [data]
        else:
            news[ticker].append(data)
    return news

def scrape_page_forbs(url):
    USER_AGENT = 'Mozilla/5.0'
    r = requests.get(url, headers={'User-Agent': USER_AGENT})
    count = 0
    while r.status_code == 403:
        print('encounter throttler, try again in 10 seconds')
        time.sleep(10)
        r = requests.get(url, headers={'User-Agent': USER_AGENT})
        if count > 12:
            raise Exception('Please investigate url: [{}]'.format(url))
        count += 1
    soup = BeautifulSoup(r.text, 'html.parser')
    body = soup.find_all('div', class_='body-container')
    content = []
    for index, el in enumerate(body):
        content.append(el.text)
    return ' '.join(content).strip().replace('\r', ' ').replace('\n', ' ') 

def scrape_page_seeking_alpha(url):
    USER_AGENT = 'Mozilla/5.0'
    r = requests.get(url, headers={'User-Agent': USER_AGENT})
    count = 0
    while r.status_code == 403:
        print('encounter throttler, try again in 10 seconds')
        time.sleep(10)
        r = requests.get(url, headers={'User-Agent': USER_AGENT})
        if count > 12:
            raise Exception('Please investigate url: [{}]'.format(url))
        count += 1
    soup = BeautifulSoup(r.text, 'html.parser')
    article = soup.find_all('article')
    content = []
    for index, el in enumerate(article):
        content.append(el.text)
    return ' '.join(content).strip().replace('\r', ' ').replace('\n', ' ').replace('  ', '')


if __name__ == "__main__":
    top_stocks = ['GOOGL', 'FB', 'UBER', 'MSFT', 'NVDA', 'INTC', 'T', 'CRM', 'AMD', 'AAPL']
    # stock_news = get_stock_news(top_stocks)
    # stock_news_content = dict()
    # for sn in stock_news.items():
    #     ticker = sn[0]
    #     print('{} has {} news'.format(sn[0], len(sn[1])))
    #     for news in sn[1]:
    #         url = news['news_url']
    #         print('\t>> url: {}'.format(url))
    print(scrape_page_seeking_alpha(target_url[0])[0:100])