import requests
import json

# Ваши учетные данные API
client_id = "_________" # Замените на ваш ID
client_secret = "____________" # Замените на ваш секретный ключ

# Конечная точка API
endpoint = "https://api.foursquare.com/v3/places/search"

# Запрос категории
category = input("Введите интересующую вас категорию (например, кофейни, музеи, парки): ")

# Определение параметров для запроса API
city = input("Введите название города: ")
params = {
    "client_id": client_id,
    "client_secret": client_secret,
    "near": city,
    "query": category
    # "rating": "10"
}

headers = {
    "Accept": "application/json",
    "Authorization": "fsq3S4QbATMZblPviOe3grYFMQxepSf291wa6B/Boa24gTU="
}

# Отправка запроса API и получение ответа
response = requests.get(endpoint, params=params, headers=headers)

# Проверка успешности запроса API
if response.status_code == 200:
    print(f'Вы искали {category} в городе {city}')
    print('\n')

    data = json.loads(response.text)
    venues = data["results"]
    for venue in venues:
        name = venue["name"]
        address = venue["location"]["formatted_address"]
        latitude =  venue["location"]
        latitude = venue["geocodes"]["main"]["latitude"]
        longitude = venue["geocodes"]["main"]["longitude"]
        # rating = venue.get("rating", "Рейтинг недоступен") # Получение рейтинга, если он есть

        print(f"Название: {name}")
        print(f"Адрес: {address}")
        print(f"Широта: {latitude}")
        print(f"Долгота: {longitude}")
        # print(f"Рейтинг: {rating}")
        print("\n")

else:
    print("Запрос API завершился неудачей с кодом состояния:", response.status_code)
    print(response.text)
