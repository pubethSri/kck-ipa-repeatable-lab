"""Scheduler"""

import time
from producer import produce
from bson import json_util
from database import get_router_info
import os

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")


def scheduler():
    """Send router info to RabbitMQ"""
    INTERVAL = 60.0
    next_run = time.monotonic()
    count = 0
    while True:
        now = time.time()
        now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
        ms = int((now % 1) * 1000)
        now_str_with_ms = f"{now_str}.{ms:03d}"
        print(f"[{now_str_with_ms}] run #{count}")

        try:
            for data in get_router_info():
                data["action"] = "get_interfaces"
                body_bytes = json_util.dumps(data).encode("utf-8")
                produce(RABBITMQ_HOST, body_bytes)
            for data in get_router_info():
                data["action"] = "get_motd"
                body_bytes = json_util.dumps(data).encode("utf-8")
                produce(RABBITMQ_HOST, body_bytes)
        except Exception as e:
            print(e)
            time.sleep(3)
        count += 1
        next_run += INTERVAL
        time.sleep(max(0.0, next_run - time.monotonic()))


scheduler()
