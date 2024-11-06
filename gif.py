# from passwords import api_key
import os
import requests
from dotenv import  load_dotenv
import json
from pprint import pprint

# https://api.giphy.com/v1/gifs/search
# ?
# api_key=XveF0PK31CO2iK349KBWdnHFKC7G4fgZ &
# q=programming &
# limit=7 &
# offset=0 &
# rating=g &
# lang=ru &
# bundle=messaging_non_clips
dotenv_path = os.path.join(os.path.dirname(__file__),'env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
# print(os.getenv("API_KEY"))
url =  "https://api.giphy.com/v1/gifs/search"
params = {
    "api_key": os.getenv("API_KEY"),
    "q": "programming",
    "limit": 7,
    "offset": 0,
    "rating": "g",
    "lang": "ru",
    "bundle": "messaging_non_clips"
}
headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 YaBrowser/24.10.0.0 Safari/537.36", 
         "Accept":"*/*"
         }
response = requests.get(url=url, params=params, headers=headers)
j_data = response.json()

with open('gifs.json','w') as f:
    json.dump(obj=j_data, fp=f)
    
for gif in j_data.get("data"):
    print(gif.get('images').get('original').get('url'))
pprint(j_data)