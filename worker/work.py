import pika
import json
import os
import time
import pytz
from datetime import datetime
from pymongo import MongoClient
from connect import get_ip_interfaces

# Environment variables
RABBIT_HOST = os.getenv("RABBIT_HOST")
RABBIT_USER = os.getenv("RABBITMQ_DEFAULT_USER")
RABBIT_PASS = os.getenv("RABBITMQ_DEFAULT_PASS")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# MongoDB client
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
collection = db["router_status"]

# Connect RabbitMQ
credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
while True:
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_HOST, credentials=credentials)
        )
        break
    except pika.exceptions.AMQPConnectionError:
        print("RabbitMQ not ready, retrying in 5 seconds...")
        time.sleep(5)
channel = connection.channel()

# Declare queue (ต้องตรงกับ scheduler)
queue_name = "router_jobs"
channel.queue_declare(queue=queue_name, durable=True)

print(" Worker1 waiting for messages...")


def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        router_ip = message.get("router_ip")
        # username = message.get("username")
        # password = message.get("password")
        router_name = message.get("router_name", router_ip)

        print(f"Processing router ({router_ip})")

        # SSH + get interface info
        # แก้ BASE_PARAMS ผ่าน environment
        data = get_ip_interfaces(router_name, router_ip)

        # Add timestamp
        data["timestamp"] = datetime.now(pytz.timezone("Asia/Bangkok")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        print(data["timestamp"])
        print(type(data["timestamp"]))
        print(data.get("interfaces", []))
        # Save to MongoDB
        collection.insert_one(data)
        print(f"Saved router {router_name} data to MongoDB")

        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Error processing message: {e}")
        # ไม่ ack ให้ message อยู่ใน queue เพื่อ retry


# Consume messages
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=queue_name, on_message_callback=callback)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping Worker...")
    channel.stop_consuming()
    connection.close()
