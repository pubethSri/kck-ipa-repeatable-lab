import pika
import os


def produce(body):
    rabbitmq_uri = os.getenv("RABBITMQ_URI")

    params = pika.URLParameters(rabbitmq_uri)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.exchange_declare(exchange="jobs", exchange_type="direct", durable=True)
    channel.queue_declare(queue="router_jobs", durable=True)
    channel.queue_bind(
        queue="router_jobs", exchange="jobs", routing_key="check_interfaces"
    )

    channel.basic_publish(exchange="jobs", routing_key="check_interfaces", body=body)

    connection.close()
