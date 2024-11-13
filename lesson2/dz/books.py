from bs4 import BeautifulSoup
import requests
import pandas as pd
from fake_useragent import UserAgent
from pprint import pprint
import re
import json

ua = UserAgent()
url = 'https://books.toscrape.com/catalogue/'
headers = {'User-Agent': ua.random}
session = requests.Session()
all_books = []
page = "page-1.html"
while True:
    response = session.get(url + page, headers=headers)
    print(f"Обрабатывается  страница {page}", end='\r')
    # soup = BeautifulSoup(response.text, 'html.parser')
    # print(response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    books = soup.find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3')
    try:
        page = soup.find('li', class_='next').find('a')['href']
    except:
        break
    # print(len(books))
    # books
    for book_id in books:
        page_books = {}
        books_info = book_id.find('a')
        href_result = books_info.get('href')
        # print(href_result)
        response = session.get(url + href_result, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        book = soup.find_all('div', class_='col-sm-6 product_main')

        for book_id2 in book:
            try:
                page_books['title'] = book_id2.find('h1').text
            except:
                page_books['title'] = 'None'
            
            # page_books['stok_info'] = book_id2.find('p', class_='instock availability').find(string=re.compile('In stock ')).get_text(strip=True)
            try:
                in_stock = book_id2.find('p', class_='instock availability').find(string=re.compile('In stock ')).get_text(strip=True)
                match = re.findall(r'\d+', in_stock)
                # Проверяем, найдено ли число, и преобразуем его в int
                if match:
                    page_books['in_stok'] = int(match[0])
                else:
                    page_books['in_stok'] = 0
            except:
                page_books['in_stok'] = 0
            try:
                page_books['price_info'] = book_id2.find('p', class_='price_color').text
            except:
                page_books['price_info'] = 'None'
            try:
                rating_element = book_id2.find('p', {'class': 'star-rating'})
                if rating_element:
                    page_books['rating']=rating_element.get('class')[1]
                else:
                    page_books['rating']='None'
            except:
                    page_books['rating']='None'
            try:
                product_page = soup.find('article', {'class': 'product_page'})                                                       
                paragraph_box =  product_page.find_all('p', {'class': None})
                page_books['description'] = " ".join(paragraph.text.strip() for paragraph in paragraph_box)
            except:
                page_books['description'] = 'None'

            all_books.append(page_books)
            
# print(all_books)
session.close()
with open('books_info.json', 'w', encoding='utf-8') as f:
    json.dump(all_books, f, indent=4)