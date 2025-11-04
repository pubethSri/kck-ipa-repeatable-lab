"""Database"""

import os

from pymongo import MongoClient


def get_router_info():
    """Get router info from DB"""
    MONGO_USER = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
    MONGO_PASSWORD = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
    MONGO_LOCATION = os.environ.get("MONGO_LOCATION")
    mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_LOCATION}:27017/"
    db_name = os.environ.get("DB_NAME")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    routers = db["routers"]

    router_data = routers.find()
    return router_data


if __name__ == "__main__":
    get_router_info()
