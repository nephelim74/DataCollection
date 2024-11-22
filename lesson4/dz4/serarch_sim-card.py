import requests
from fake_useragent import UserAgent
from lxml import html
import csv
import re
import logging

# Настройка логирования для отслеживания ошибок
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ua = UserAgent()
url = 'https://megasimka.ru/product-category/sim-cards/'
headers = {'User-Agent': ua.random}
session = requests.Session()

def extract_data(tree_loc):
    """Извлекает данные из страницы товара."""
    data = {}
    try:
        sim_attrs = tree_loc.xpath('.//div[@class="col-inner"]//h1')
        if sim_attrs:
            data['name'] = sim_attrs[0].text_content().strip()
        else:
            logging.warning("Не найдено название SIM-карты.")
            return None

        prices = tree_loc.xpath('.//p[@class="price product-page-price price-on-sale"]/span')
        if prices and len(prices) >= 2:
            price_tmp0 = prices[0].text_content().strip()
            price_tmp1 = prices[1].text_content().strip()
            match_past = re.search(r'Первоначальная цена составляла\s*(.*)₽\.', price_tmp0)
            data['past_price'] = float(re.sub(r'[,]', '', match_past.group(1).strip())) if match_past else 0
            match_last = re.search(r'Текущая цена:\s*(.*)₽\.', price_tmp1)
            data['last_price'] = float(re.sub(r'[,]', '', match_last.group(1).strip())) if match_last else 0
        else:
            logging.warning("Не найдены цены.")
            return None

        raiting = tree_loc.xpath('//div[@class="woocommerce-product-rating"]//span/strong/text()')
        data['raiting'] = float(raiting[0]) if raiting else 0

        description_paragraphs = tree_loc.xpath('//div[@class="product-short-description"]/p')
        description_text = " ".join([p.text_content().strip() for p in description_paragraphs if p.text_content()]) 

        data['subscription_fee'] = re.search(r'Абонентская плата:\s*(\d+\s*₽\s*в месяц)', description_text)
        data['subscription_fee'] = data['subscription_fee'].group(1) if data['subscription_fee'] else 'null'

        data['call_local'] = re.search(r'Исходящие звонки внутри сети:\s*(.+)', description_text)
        data['call_local'] = data['call_local'].group(1) if data['call_local'] else 'null'

        data['call_all'] = re.search(r'Исходящие звонки на любые номера по всей РФ:\s*(.+)', description_text) 
        data['call_all'] = data['call_all'].group(1) if data['call_all'] else 'null'

        data['share_smartphone'] = re.search(r'Раздача со смартфона:\s*(.+)', description_text) 
        data['share_smartphone'] = data['share_smartphone'].group(1) if data['share_smartphone'] else 'null'

        data['sms_mms'] = re.search(r'SMS/MMS:\s*(.+)', description_text) 
        data['sms_mms'] = data['sms_mms'].group(1) if data['sms_mms'] else 'null'

        data['traffic'] = re.search(r'Трафик:\s*(.+)', description_text)
        data['traffic'] = data['traffic'].group(1) if data['traffic'] else 'null'

        data['speed'] = re.search(r'Скорость:\s*(.+)', description_text)
        data['speed'] = data['speed'].group(1) if data['speed'] else 'null'


        return data
    except (AttributeError, IndexError) as e:
        logging.error(f"Ошибка при обработке данных: {e}")
        return None
    except Exception as e:
        logging.exception(f"Непредвиденная ошибка: {e}")
        return None


try:
    response = session.get(url, headers=headers)
    response.raise_for_status()
    tree = html.fromstring(response.content)
    sims = tree.xpath('//div[contains(@class,"product-small")]//a[contains(@aria-label,"SIM")]')
    all_sim_cards = []
    for i, sim_items in enumerate(sims):
        sim_fref = sim_items.get('href')
        print(f'Обработано {i+1} из {len(sims)}', end='\r') 
        try:
            response = session.get(sim_fref, headers=headers)
            response.raise_for_status()
            tree_loc = html.fromstring(response.content)
            sim_data = extract_data(tree_loc)
            if sim_data:
                all_sim_cards.append(sim_data)
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка при запросе к {sim_fref}: {e}")
        except Exception as e:
            logging.exception(f"Непредвиденная ошибка при обработке страницы {sim_fref}: {e}")


    # Сохранение данных в CSV (добавлена обработка ошибок)
    try:
        with open('sim_cards.csv', 'w', newline='', encoding='utf-8') as csvfile:
            if all_sim_cards: # Проверка на пустоту
                fieldnames = all_sim_cards[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                writer.writerows(all_sim_cards)
            else:
                logging.warning("Список SIM-карт пуст. Файл CSV не создан.")
        logging.info("Данные успешно сохранены в sim_cards.csv")
    except (IOError, IndexError) as e:
        logging.error(f"Ошибка при сохранении данных в CSV: {e}")

except requests.exceptions.RequestException as e:
    logging.error(f"Ошибка при запросе к {url}: {e}")
except Exception as e:
    logging.exception(f"Непредвиденная ошибка: {e}")
