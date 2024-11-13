# Импорт необходимых библиотек
from bs4 import BeautifulSoup
import requests
import pandas as pd
from fake_useragent import UserAgent
from pprint import pprint
ua = UserAgent()
# print(ua.safari)
# url = 'https://www.boxofficemojo.com/intl/?ref_=bo_nb_hm_tab'
url = 'https://www.boxofficemojo.com'
headers = {'User-Agent': ua.random}
params = {'ref_':'bo_nb_hm_tab'}
session = requests.Session()
response = session.get(url+"/intl", headers=headers, params=params)
print(response.status_code)
soup = BeautifulSoup(response.text, 'html.parser')
test_link = soup.find(name = "a", attrs = {'class':'a-link-normal'})
# print(test_link)
rows = soup.find_all('tr')
# print(rows)
films = []
for row in rows[1:]:
    film = {}
    # area_info = row.find('a', {'class', 'a-link-normal'})
    # area_info = row.find('td', {'class', 'mojo-field-type-area_id'})
    # if area_info:
    #     area_info = area_info.find('a')
    area_info = row.find('td', {'class', 'mojo-field-type-area_id'})
    if area_info:
        area_info = area_info.findChildren()[0]
    film['area'] = ''
    # print(area_info)
    if area_info:
        film['area'] = [area_info.getText(), url + area_info.get('href')]
    # print(film['area'])
    
    weekend_info = row.find('td', {'class', 'mojo-field-type-date_interval'})
    if weekend_info:
        weekend_info = weekend_info.findChildren()[0]
    film['weekend'] = ''
    if weekend_info:
        film['weekend'] = [weekend_info.getText(), url + weekend_info.get('href')]
    # print(film['weekend'])
    realeses_info = row.find('td', {'class', 'mojo-field-type-positive_integer'})
    film['realeses'] = ''
    if realeses_info:
        try:
            film['realeses'] = int(realeses_info.getText())
        except:
            film['realeses'] = ['-']
    # print(film['realeses'])
    
    frealeses_info = row.find('td', {'class', 'mojo-cell-wide'})
    film['frealeses'] = ''
    if frealeses_info:
        try:
            frealeses_info = frealeses_info.findChildren()[0]
            film['frealeses'] = [frealeses_info.getText(), url + frealeses_info.get('href')]
        except:
            film['frealeses'] = ['None']
    # print(film['frealeses'])
    
    distributor_info = row.find('td', {'class', 'mojo-field-type-studio'})
    film['distributor'] = ''
    if distributor_info:
        try:
            distributor_info = distributor_info.findChildren()[0]
            film['distributor'] = [distributor_info.getText(), url + distributor_info.get('href')]
        except:
            film['distributor'] = ['None']
    # print(film['distributor'])
    
    gross_info = row.find('td', {'class', 'mojo-field-type-money'})
    # print(gross_info)
    film['gross'] = ''
    if gross_info:
        try:
            film['gross'] = gross_info.getText()
        except:
            film['gross'] = ['None']
    # print(film['gross'])    

    # print('---------------------')
    films.append(film)
pprint(films)
session.close()