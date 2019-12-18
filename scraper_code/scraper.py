# Team Member:
# * Coordinator: Zijie Ku (zijieku2)
# * Member: Yanbin Zhang (zhang50)

import requests
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# define API keys here
STOCKNEWSAPI_KEY = 'h369abgt0vvwxlsqbediutienyp7raeskw5xpvhj'
STOCKNEWSAPI_URL = 'https://stocknewsapi.com/api/v1'

IEXAPI_KEY = 'pk_c9e4c01aba164dcd8970fa1b79038ca1'

NEWS_SRC = {
    '24/7 Wall Street': '24/7+Wall+Street',
    'Benzinga': 'Benzinga',
    'Bloomberg Markets & Finance': 'Bloomberg+Markets+and+Finance', 
    'Bloomberg Technology': 'Bloomberg+Technology',
    'Business Insider': 'Business+Insider',
    'CNBC': 'CNBC',
    'CNBC International TV': 'CNBC+International+TV',
    'CNBC Television': 'CNBC+Television',
    'CNET': 'CNET',
    'CNN': 'CNN',
    'CNN Business': 'CNN+Business',
    'Digital Trends': 'Digital+Trends',
    'Deadline': 'Deadline',
    'Engadget': 'Engadget',
    'ETF Trends': 'ETF+Trends',
    'Fast Company': 'Fast+Company',
    'Forbes': 'Forbes',
    'Fox Business': 'Fox+Business',
    'GeekWire': 'GeekWire',
    'Globe News Wire': 'GlobeNewsWire',
    'GuruFocus': 'GuruFocus',
    'Huffington Post': 'Huffington+Post',
    'Investopedia': 'Investopedia',
    'Investors Business Daily': 'Investors+Business+Daily',
    'Investor Place': 'InvestorPlace',
    'Iris': 'Iris',
    'Market Watch': 'Market+Watch',
    'New York Post': 'New+Yor+Post',
    'New York Times': 'NYTimes',
    'Reuters': 'Reuters',
    'See It Market': 'See+It+Market',
    'Seeking Alpha': 'Seeking+Alpha',
    'TechCrunch': 'TechCrunch',
    'The Motley Fool': 'The+Motley+Fool',
    'The Street': 'The+Street',
    'Wall Street Journal': 'Wall+Street+Journal',
    'Yahoo Finance': 'Yahoo+Finance',
    'Zacks Investment Research': 'Zacks+Investment+Research'
}

# Blacklist
EXCLUDE_SRC = {
    # Bloomberg Markets & Finance is pure YouTube content
    # Irrelevant to text data analysis
    # Perhaps one day, we can do a speech recognition project
    'Bloomberg Markets & Finance'
}

# Whitelist
# For the purpose of CS 410: 
# Choose 'Free' news source
INCLUDE_SRC = {
    'Benzinga', 'Business Insider', 'Forbes', 'Fox Business',
    'Investors Business Daily', 'The Motley Fool', 'Reuters',
    'New York Times', 'Yahoo Finance', 'Zacks Investment Research',
    'Seeking Alpha', 'The Street', 'Market Watch'
}

class scraper:
    """Create an scraper object
    """
    def __init__(self, browser, url=''):
        self.browser = browser
        self.url = url
        self.blacklist = set()

    def __repr__(self):
        """Return string representation of the scraper object
        """
        return 'scraping url: [' + self.url + ']'

    def is_reponse_200(self):
        try:
            headers = {'User-Agent': ''}
            return 200 == requests.get(self.url, headers=headers).status_code
        except:
            print("### Cloud not get response from [{}]".format(self.url))

    def add_to_blacklist(self, bl):
        """Add set of url to the scraper blacklist

        """
        input_type = type(bl)
        if set == input_type:
            self.blacklist.union(bl)
        elif list == input_type:
            self.backlist.union(set(bl))
        elif str == input_type:
            self.blacklist.add(bl)
        else:
            print('### Could not add {} to scraper\'s blacklist'.format(input_type))


def get_top_mentioned_stocks_last30days (sector='All'):
    '''
    Get top mentioned stock ticker for the past 30 days
    '''
    sectors = {
        'Basic Materials', 'Conglomerates', 'Consumer Goods', 'Financial',
        'Healthcare', 'Industrial Goods', 'Services', 'Technology', 'Utilities'
    }
    if sector != 'All' and sector not in sectors:
        raise Exception ('invalid sector')

    url = STOCKNEWSAPI_URL + '/top-mention'
    PARAMS = {'date': 'last30days','token': STOCKNEWSAPI_KEY, 'items': 50}
    if sector != 'All':
        PARAMS['sector'] = sector.replace(' ', '+')
    r = requests.get(url=url, params=PARAMS)
    if r.status_code != 200:
        raise Exception('invalid STOCKNEWS API request to get top mentioned stocks')
    top_stocks = []
    for s in r.json()['data']['all']:
        top_stocks.append(s['ticker'])
    return top_stocks


def get_stock_news (stocks):
    news = dict()
    for s in stocks:
        news.update(get_single_stock_news(s))
    return news


def get_single_stock_news (ticker, today=False):
    '''
    Get last 30 days news for all of the tickers
    '''
    start_date = datetime.strftime(datetime.now() - timedelta(33), '%m%d%Y')
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

if __name__ == "__main__":

    # create a chrome browser object
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # browser = webdriver.Chrome('./chromedriver', options=chrome_options)
    # browser.quit()

    # url = STOCKNEWSAPI_URL + '/category?section=general'
    # print(url)
    # PARAMS = {'token': STOCKNEWSAPI_KEY, 'items': 50}
    # r = requests.get(url=url, params=PARAMS)

    # if r.status_code != 200:
    #     raise Exception('invalid STOCKNEWS API request')

    top_stocks = get_top_mentioned_stocks_last30days(sector = 'Technology')
    print('top stocks: {}'.format(top_stocks))
    stock_news = get_stock_news(top_stocks)
    for sn in stock_news.items():
        print('{} has {} news'.format(sn[0], sn[1]))
    # print(r.json())
    # print(r.status_code)
