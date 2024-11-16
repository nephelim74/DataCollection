from pymongo import MongoClient
from pprint import pprint
from pymongo.errors import *
import json
client = MongoClient('mongodb://localhost:27017/')
db = client['users']
persons = db.persons

# doc = { '_id': 'sxhywy6t3gx5',
#     'autor':'Peter',
#     'text':'is cool! Wilberry',
#     'date':'2020-01-01',
#     'likes': 0,
#     'tags':['cool','hot','ice'],
#     'comments':['good']
# }

with open('books.json', 'r') as file:
    docs = json.load(file)

# for doc in docs:
#     try:
#         # persons.insert_one(doc)
#         persons.insert_many(docs)
#     except DuplicateKeyError as e:
#         print(e)

# for doc in persons.find({'title':{'$regex':'^Vampire.'}}, {'title':1,'rating':1, '_id':0}).sort('in_stok'):
#     print(doc)

persons.update_many({'title':{'$regex':'^Lost(.*)'}},{'$set':{'title':'Lost2'}})

for doc in persons.find({},{'title':1,'rating':1, '_id':0}):
    print(doc)
    