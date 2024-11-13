from bs4 import BeautifulSoup
import requests
import pandas as pd
from fake_useragent import UserAgent
from pprint import pprint
ua = UserAgent()
url = 'https://www.gb.ru'

headers = {'User-Agent': ua.random}
params = {'page': 1}
session = requests.Session()

# print(len(posts))
all_posts = []
while True:
    response = session.get(url+"/posts", headers=headers, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')
    posts = soup.find_all('div', class_='post-item').findChildren('span')
    if not posts:
        break
    # else:
    #     params['page'] +=1
    for post in posts:
        post_info = {}
        try: 
            name_info = post.find('a', class_='post-item__title')
            post_info['name'] = name_info.getText()
        except:
            post_info['name'] = 'None'
        try:
            post_info['url'] = url + name_info.get('href')
        except:
            post_info['url'] = 'None'
        try:
            add_info = post.find('div',class_='text-muted').findChildren('span')
            post_info['views'] = int(add_info[0].getText())
        except:
            post_info['views'] = -1
        try:
            post_info['comments'] = int(add_info[1].getText())
        except:
            post_info['comments'] = -1
        all_posts.append(post_info)
    print(f"Обработана {params['page']} страница", end='\r')
    params['page'] +=1

pprint(all_posts)
pprint(len(all_posts))
# Создание pandas dataframe
df = pd.DataFrame(all_posts)
print(df)
df.to_csv('gb_posts.csv')