import requests
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgent
import threading
import pandas as pd

headers = {'User-Agent': FakeUserAgent().random}
data = []
lock = threading.Lock()


def deal_with_othe_nam(other_name: str):  # delete first "/" and space
    other_name = other_name.split('/')
    other_name = '/'.join([s.strip() for s in other_name[1:]])
    return other_name


def scrape_web(page: int):
    global data
    url = f'https://movie.douban.com/top250?start={(page - 1) * 25}&filter='
    response = requests.get(url, headers=headers)
    html = BeautifulSoup(response.text, 'lxml')
    # deal with name, href, rating
    names = html.find_all('div', class_='info')
    for name in names:
        title = name.find_all('span', class_='title')
        cn_name = title[0].text.strip()
        en_name = title[1].text.strip()[1:] if len(title) == 2 else None
        other_name = name.find('span', class_='other')
        other_name = deal_with_othe_nam(other_name.text) if other_name else None
        rating = name.find('span', class_='rating_num').text
        href = name.find('div', class_='hd').a['href']
        with lock:
            data.append([cn_name, en_name, other_name, rating, href])
    print(f'page{page} is done')


threads = []
# use thread to fast the process
for i in range(1, 11):
    thread = threading.Thread(target=scrape_web, args=[i])
    threads.append(thread)
    thread.start()  # start every thread

for t in threads:
    t.join()  # wait every thread to end otherwise some of them not finished

df = pd.DataFrame(data, columns=['CN_TITLE', 'EN_TITLE', 'OTHER_TITLE', 'RATING', 'HREF'])
df.to_excel('movie.xlsx', index=False, encoding='utf-8')
