import time
import os
from bson import json_util
from producer import produce
from database import get_router_info

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")

def scheduler():
    INTERVAL = 60
    next_run = time.monotonic()
    count = 0

    while True:
        now = time.time()
        now_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
        ms = int((now % 1) * 1000)
        now_str_with_ms = f"{now_str}.{ms:03d}"
        print(f"[{now_str_with_ms}] run #{count}")

        try:
            all_routers = list(get_router_info())

            for data in all_routers:
                data["action"] = "get_interfaces"
                body_bytes = json_util.dumps(data).encode("utf-8")
                produce(RABBITMQ_HOST, body_bytes)

            # for data in all_routers:
            #     data["action"] = "get_motd"
            #     body_bytes = json_util.dumps(data).encode("utf-8")
            #     produce(RABBITMQ_HOST, body_bytes)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)

        count += 1
        next_run += INTERVAL
        time.sleep(max(0.0, next_run - time.monotonic()))


if __name__ == "__main__":
    scheduler()