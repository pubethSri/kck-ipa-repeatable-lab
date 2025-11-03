import time
import os
from bson import json_util
from producer import produce
from database import get_router_info


RABBIT_HOST = os.getenv("RABBIT_HOST")


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
            for router in get_router_info():
                # สร้าง message ให้ Worker1
                message = {
                    "router_name": router.get("name", "Router"),
                    "router_ip": router.get("ip"),
                    "username": router.get("username", "admin"),
                    "password": router.get("password", "cisco"),
                }

                # แปลงเป็น bytes
                body_bytes = json_util.dumps(message).encode("utf-8")

                # ส่งไป RabbitMQ
                produce(body_bytes)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)

        count += 1
        next_run += INTERVAL
        time.sleep(max(0.0, next_run - time.monotonic()))


if __name__ == "__main__":
    scheduler()
