import time
import requests
from bs4 import BeautifulSoup
# from bs4.element import Comment
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

target_url = [
    'https://www.forbes.com/sites/greatspeculations/2019/12/04/verizons-cash-flow-increases-the-safety-of-its-dividend-yield/',
    'https://www.forbes.com/sites/adamsarhan/2019/12/02/earnings-preview-what-to-expect-from-salesforcecom-on-tuesday/'
]

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
    # create a webdriver object and set options for headless browsing
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # browser = webdriver.Chrome('./chromedriver', options=chrome_options)
    content = scrape_page_forbs(target_url[0])
    print(content)
    # browser.quit()
