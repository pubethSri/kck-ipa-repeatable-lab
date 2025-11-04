"""Producer"""

import pika
import os


RABBITMQ_USERNAME = os.environ.get("RABBITMQ_DEFAULT_USER")
RABBITMQ_PASSWORD = os.environ.get("RABBITMQ_DEFAULT_PASS")

CREDENTIALS = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)


def produce(host, body):
    """Produce work to RabbitMQ by Web"""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host, credentials=CREDENTIALS)
    )
    channel = connection.channel()

    channel.exchange_declare(exchange="jobs", exchange_type="direct")
    channel.queue_declare(queue="router_jobs")
    channel.queue_bind(
        queue="router_jobs", exchange="jobs", routing_key="check_interfaces"
    )

    channel.basic_publish(exchange="jobs", routing_key="check_interfaces", body=body)

    connection.close()


if __name__ == "__main__":
    produce("localhost", "192.168.255.15")
