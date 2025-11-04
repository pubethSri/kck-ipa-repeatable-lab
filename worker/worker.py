import pika
import os
import time
from callback import callback


RABBITMQ_USERNAME = os.environ.get("RABBITMQ_DEFAULT_USER")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_DEFAULT_PASS")
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")

CREDENTIALS = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)


def consume(host):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host, credentials=CREDENTIALS)
    )
    channel = connection.channel()

    channel.queue_declare(queue="router_jobs")
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="router_jobs", on_message_callback=callback)

    channel.start_consuming()


if __name__ == "__main__":
    for attempt in range(10):
        try:
            print(f"Connecting to RabbitMQ (try {attempt})...")
            consume(RABBITMQ_HOST)
            break
        except Exception as e:
            print(f"Failed: {e}")
            time.sleep(5)
    else:
        print("Could not connect after 10 attempts")
        exit(1)
