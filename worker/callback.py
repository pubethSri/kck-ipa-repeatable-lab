import json
import time
import pika
import os
from workload import (
    create_loopback,
    delete_loopback,
    show_interface,
    create_motd,
    show_motd,
)
from database import insert_interface_status, insert_motd_message


def get_motd(router_ip, username, password):
    message = show_motd(router_ip, username, password)
    insert_motd_message({"router_ip": router_ip, "timestamp": "", "message": message})


def get_interfaces(router_ip, username, password):
    interfaces_data = show_interface(router_ip, username, password)
    insert_interface_status(
        {"router_ip": router_ip, "timestamp": "", "interfaces": interfaces_data}
    )


def callback(ch, method, properties, body):
    data = json.loads(body.decode())
    router_ip = data.get("router_ipaddr")
    username = data.get("username")
    password = data.get("password")
    if data["action"] == "set_motd":
        result = create_motd(
            router_ip,
            username,
            password,
            data.get("message", ""),
        )
        print(f"Set MOTD result for router {router_ip}: {result}")
        get_motd(router_ip, username, password)
    elif data["action"] == "get_motd":
        get_motd(router_ip, username, password)
    elif data["action"] == "create_loopback":
        loopback_number = data.get("loopback_number")
        loopback_ip = data.get("interface_ip")
        result = create_loopback(
            router_ip,
            username,
            password,
            loopback_number,
            loopback_ip,
        )
        interfaces_data = show_interface(router_ip, username, password)
        insert_interface_status(
            {"router_ip": router_ip, "timestamp": "", "interfaces": interfaces_data}
        )
        print(f"Create Loopback result for router {router_ip}: {result}")
    elif data["action"] == "delete_loopback":
        loopback_number = data.get("loopback_number")
        result = delete_loopback(
            router_ip,
            username,
            password,
            loopback_number,
        )
        interfaces_data = show_interface(router_ip, username, password)
        insert_interface_status(
            {"router_ip": router_ip, "timestamp": "", "interfaces": interfaces_data}
        )
        print(f"Delete Loopback result for router {router_ip}: {result}")
    else:
        interfaces_data = show_interface(router_ip, username, password)
        insert_interface_status(
            {"router_ip": router_ip, "timestamp": "", "interfaces": interfaces_data}
        )

    print(f"Received job for router {router_ip}")
    print(json.dumps(interfaces_data, indent=2))

    time.sleep(body.count(b"."))
    ch.basic_ack(delivery_tag=method.delivery_tag)
