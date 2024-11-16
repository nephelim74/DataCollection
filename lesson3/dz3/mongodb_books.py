from bs4 import BeautifulSoup
import requests
import pandas as pd
from fake_useragent import UserAgent
from pprint import pprint
import re
import json
import pymongo
from pymongo import MongoClient
from pymongo.errors import *
import time

def insert_bd(doc):
    try:
        result = collection.insert_one(doc)
        # print(f"Документ {doc} вставлен с ID: {result.inserted_id}")
        for id in collection.find(
                {'UPC': doc['UPC'] }):
            print(f'В БД добавлен документ с ID: {id["_id"]}', end='\r')
            # time.sleep(1)
    except pymongo.errors.DuplicateKeyError as e:
        print(f"Ошибка: Дубликат ключа для документа {doc['title']}")
    except pymongo.errors.BulkWriteError as e:
        print(f"Ошибка при массовой вставке: {e}")
def sort_rating():
    pipeline = [
        {
            "$group": {
                "_id": "$rating",  # Группируем по полю rating
                "count": {"$sum": 1}  # Подсчитываем количество книг с данным рейтингом
            }
        },
        {
            "$sort": {
                "_id": 1  # Сортируем по полю rating (по возрастанию)
            }
        }
    ]
    result = collection.aggregate(pipeline)
    for doc in result:
        print(f"С рейтингом: {doc['_id']}, количество книг: {doc['count']}")
# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/") # Замените на ваши параметры подключения
db = client["mydatabasebook"]
collection = db["books"]
collection.drop()
select_menu = input('Хотите загрузить новые данные по книгам? (y/n): ')
if select_menu in ['да', 'yes', 'y', 'Да', 'Yes', 'Y']:
    
    # Создаем уникальный индекс (если его еще нет) по полю 'title'
    try:
        collection.create_index([("UPC", pymongo.ASCENDING)], unique=True)
        print("Уникальный индекс создан.")
    except pymongo.errors.OperationFailure as e:
        if "already exists with the same name" in str(e):
            print("Уникальный индекс уже существует.")
        else:
            print(f"Ошибка при создании индекса: {e}")
    ua = UserAgent()
    url = 'https://books.toscrape.com/catalogue/'
    headers = {'User-Agent': ua.random}
    session = requests.Session()
    all_books = []
    page = "page-1.html"
    while True:
        response = session.get(url + page, headers=headers)
        print(f"Обрабатывается  страница {page}", end='\r')
        # time.sleep(1)
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
                try:
                    UPC =  soup.find('table', {'class': 'table table-striped'})
                    page_books['UPC'] = UPC.find('td').text
                    # print(page_books['UPC'])
                except:
                    page_books['UPC'] = 'None'
                    # print(page_books['UPC'])
                

                all_books.append(page_books)
                insert_bd(page_books)
                

                
    # print(all_books)
    session.close()
    # sort_rating()

    
print('------------------------------\n')
keys = input('Вывести статистику по книгам?  (y/n):')
if keys in ['да', 'yes', 'y', 'Да', 'Yes', 'Y']:
    sort_rating()
    while True:
        print('------------------------------\n')
        search_criteria = input("Введите 'title' (1) для поиска по названию книги  \n или 'rating' (2) для поиска по рейтингу \n или q (0) выход:").strip().lower()
        if search_criteria in ['1', 'title']: search_criteria = 'title'
        elif search_criteria in ['2', 'rating']: search_criteria = 'rating'
        elif search_criteria in ['q', '0', 'exit', 'quit']: break
        else: search_criteria = 'title'
        if search_criteria == 'title':
            search_title = input("Введите название книги для поиска: ")
            results = collection.find({
                "title": {"$regex": search_title, "$options": "i"}  # Регистронезависимый поиск
            })
        elif search_criteria == 'rating':
            search_rating = input("Введите рейтинг для поиска: ").strip().lower()
            if search_rating in ['1', 'one']: search_rating = 'Оne'
            elif search_rating in ['2', 'two']: search_rating = 'Two'
            elif search_rating in ['3', 'three']: search_rating = 'Three'
            elif search_rating in ['4', 'four']: search_rating = 'Four'
            elif search_rating in ['5', 'five']: search_rating = 'Five'
            else: print('некорректный ввод')
            results = collection.find({
                "rating": search_rating  # Поиск по рейтингу
            })
        else:
            print('-----------------------------------\n')
            print("Неверный ввод. Пожалуйста, введите 'title' или 'rating'.")
            results = []

        # Вывод результатов
        # Вывод результатов
        for doc in results:
            print(f"Title: {doc['title']}, Rating: {doc['rating']}, In Stock: {doc['in_stok']}, Price: {doc['price_info']}")
    client.close()
else:
    client.close()
    exit()
# with open('books_info.json', 'w', encoding='utf-8') as f:
#     json.dump(all_books, f, indent=4)

# client = MongoClient('mongodb://localhost:27017/')
# db = client['crashes']
# info = db.info