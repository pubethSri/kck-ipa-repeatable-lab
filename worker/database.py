import os
import time
from datetime import datetime, timezone

from pymongo import MongoClient

MONGO_USER = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASSWORD = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
MONGO_LOCATION = os.environ.get("MONGO_LOCATION")
mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_LOCATION}:27017/"
db_name = os.environ.get("DB_NAME")


def insert_interface_status(data):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    interface_status = db["interface_status"]

    ts = time.time()
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    data["timestamp"] = dt

    interface_status.insert_one(data)
    router_ip = data.get("router_ip")

    print(f"Stored interface status for {router_ip}")


def insert_motd_message(data):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    motd_messages = db["motd_messages"]

    router_ip = data.get("router_ip")
    message = data.get("message")

    # Get the latest MOTD for this router
    existing_motd = motd_messages.find_one(
        {"router_ip": router_ip}, sort=[("timestamp", -1)]
    )

    ts = time.time()
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    data["timestamp"] = dt

    if existing_motd and existing_motd.get("message") == message:
        # Update timestamp if message is the same
        motd_messages.update_one(
            {"_id": existing_motd["_id"]}, {"$set": {"timestamp": dt}}
        )
        print(f"Updated timestamp for existing MOTD on router {router_ip}")
    else:
        # Insert new message if different
        motd_messages.insert_one(data)
        print(f"Stored new MOTD message for router {router_ip}")
