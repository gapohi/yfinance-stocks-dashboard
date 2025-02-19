from pymongo import MongoClient

# Función para obtener los datos desde MongoDB
def fetch_data_from_mongodb():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["yfinance"]
    collection = db["prices"]
    data = list(collection.find({}))
    return list(data)

data = fetch_data_from_mongodb()

for i in data:
    print(i['ticker'])
    print("\n")
    print(i['price'])
    print("\n")
    print(i['volume'])
    print("\n")
    print("--------------------")
    print("\n")