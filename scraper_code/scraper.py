# Team Member:
# * Coordinator: Zijie Ku (zijieku2)
# * Member: Yanbin Zhang (zhang50)

import time
import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# define API keys here
STOCKNEWSAPI_KEY = 'h369abgt0vvwxlsqbediutienyp7raeskw5xpvhj'
STOCKNEWSAPI_URL = 'https://stocknewsapi.com/api/v1'

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
    # 'Seeking Alpha'
    #, 
    'Forbes'
    # 'Benzinga', 'Business Insider', 'Fox Business',
    # 'Investors Business Daily', 'The Motley Fool', 'Reuters',
    # 'New York Times', 'Yahoo Finance', 'Zacks Investment Research',
    # 'The Street', 'Market Watch'
}

def scrape_page_seeking_alpha(url):
    USER_AGENT = 'Mozilla/5.0'
    r = requests.get(url, headers={'User-Agent': USER_AGENT})
    count = 0
    while r.status_code == 403:
        print('\t>> encounter throttler, try again in 10 seconds')
        time.sleep(30)
        r = requests.get(url, headers={'User-Agent': USER_AGENT})
        if count > 12:
            raise Exception('Please investigate url: [{}]'.format(url))
        count += 1
    soup = BeautifulSoup(r.text, 'html.parser')
    r.cookies.clear()
    r.close()
    article = soup.find_all('article')
    content = []
    for index, el in enumerate(article):
        content.append(el.text)
    return ' '.join(content).strip().replace('\r', ' ').replace('\n', ' ').replace('  ', '')

def scrape_page_forbs(url):
    ## include user agent as some website does not allow the default 'User-Agent'
    ## another go around is to use a web proxy
    ## Unfortunately, it's not available in certain regions
    USER_AGENT = 'Mozilla/5.0'
    r = requests.get(url, headers={'User-Agent': USER_AGENT})
    count = 0

    ## exponential backoff for throttler 
    while r.status_code == 403:
        print('encounter throttler, try again in 10 seconds')
        time.sleep(10)
        r = requests.get(url, headers={'User-Agent': USER_AGENT})
        if count > 12:
            raise Exception('Please investigate url: [{}]'.format(url))
        count += 1
        # clears request cookie
        request.cookies.clear()
        request.close()
    soup = BeautifulSoup(r.text, 'html.parser')
    body = soup.find_all('div', class_='body-container')
    content = []
    for index, el in enumerate(body):
        content.append(el.text)
    return process_bio(' '.join(content).strip().replace('\r', ' ').replace('\n', ' ')) 

def process_bio(bio):
    ## remove white spaces in the contents
    bio = bio.encode('ascii', errors='ignore').decode('utf-8')
    bio = re.sub('\s+', ' ', bio)
    return bio

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

def write_file (file, data):
    with open(file, 'a+') as f:
        f.write(data)
        f.write('\n\n')


def get_browser():
    ''' 
    create an browser object
    remember to close the browser object to prevent leakage and overflow
    browser.quit()
    '''
    ## create a chrome browser object
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    browser = webdriver.Chrome('./chromedriver', options=chrome_options)
    return browser


def scrape(stock_news):
    ## creates label based on Forbs news
    dir_0 = './0'
    dir_1 = './1'
    dir_2 = './2'

    ## process labels and news contents
    stock_news_content = dict()
    for sn in stock_news.items():
        ticker = sn[0]
        print('{} has {} news'.format(sn[0], len(sn[1])))
        for news in sn[1]:
            url = news['news_url']
            # print('\t>> url: {}'.format(url))
            news_content = scrape_page_forbs(url)
            data = {
                'content': news_content,
                'sentiment': news['sentiment']
            }
            if ticker not in stock_news_content:
                stock_news_content[ticker] = [data]
            else:
                stock_news_content[ticker].append(data)
        print('\tcompleted scapping for {}'.format(ticker))
            # print('\t>> news is: {}'.format(news_content[0:100]))

    count_0 = count_1 = count_2 = 0
    for snc in stock_news_content.items():
        ticker = snc[0]
        for content in snc[1]:
            # print(content)
            file_name = ''
            if content['sentiment'] == 0:
                file_name = dir_0 + '/sample' + str(count_0) + '.txt'
                count_0 += 1
            elif content['sentiment'] == 1:
                file_name = dir_1 + '/sample' + str(count_1) + '.txt'
                count_1 += 1
            else:
                file_name = dir_2 + '/sample' + str(count_2) + '.txt'
                count_2 += 1
            write_file(file_name, content['content'])


if __name__ == "__main__":

    ## top stocks changes as time progresses
    ## to make it consistent with trained model hard-code it with the top mentioned stock listed at 01:34 AM UTC
    # top_stocks = get_top_mentioned_stocks_last30days(sector = 'Technology')
    top_stocks = ['GOOGL', 'FB', 'UBER', 'MSFT', 'NVDA', 'INTC', 'T', 'CRM', 'AMD', 'AAPL']
    print('top stocks: {}'.format(top_stocks))
    
    
    ## Done scrapping
    # stock_news = get_stock_news(top_stocks)
    # scrape(stock_news)

    stock_news = get_stock_news(top_stocks, today=True)
    test_dir = './test'
    ## process labels and news contents
    stock_news_content = dict()
    for sn in stock_news.items():
        ticker = sn[0]
        print('{} has {} news'.format(sn[0], len(sn[1])))
        for news in sn[1]:
            url = news['news_url']
            print('\t>> url: {}'.format(url))
            news_content = scrape_page_forbs(url)
            data = {
                'content': news_content,
                'sentiment': news['sentiment']
            }
            if ticker not in stock_news_content:
                stock_news_content[ticker] = [data]
            else:
                stock_news_content[ticker].append(data)
        print('\tcompleted scapping for {}'.format(ticker))

    count_0 = count_1 = count_2 = 0
    for snc in stock_news_content.items():
        ticker = snc[0]
        for content in snc[1]:
            # print(content)
            file_name = ''
            if content['sentiment'] == 0:
                file_name = test_dir + '/sample' + str(count_0) + '.txt'
                count_0 += 1
            elif content['sentiment'] == 1:
                file_name = test_dir + '/sample' + str(count_1) + '.txt'
                count_1 += 1
            else:
                file_name = test_dir + '/sample' + str(count_2) + '.txt'
                count_2 += 1
            write_file(file_name, content['content'])
    
    # for sn in stock_news_content.items():
    #     print('{}'.format(sn))
    # for sn in stock_news.items():
    #     print('{} has {} news'.format(sn[0], sn[1]))
