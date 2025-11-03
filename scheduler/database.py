import os

from pymongo import MongoClient


def get_router_info():
    mongo_uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("DB_NAME")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    routers = db["routers"]

    router_data = routers.find()
    # for data in router_data:
    #     print(data)
    return router_data


if __name__ == "__main__":
    get_router_info()
