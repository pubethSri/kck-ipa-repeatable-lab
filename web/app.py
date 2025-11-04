"""Flask App"""

import os
import json

from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId

from producer import produce

APP = Flask(__name__)

MONGO_USER = os.environ.get("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASSWORD = os.environ.get("MONGO_INITDB_ROOT_PASSWORD")
MONGO_LOCATION = os.environ.get("MONGO_LOCATION")
RABBITMQ_HOST = os.environ.get("RABBITMQ_LOCATION", "rabbitmq")

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_LOCATION}:27017/"
DB_NAME = os.environ.get("DB_NAME")

CLIENT = MongoClient(MONGO_URI)
MYDB = CLIENT[DB_NAME]
MYCOL = MYDB["routers"]
INFO = MYDB["interface_status"]
MOTD = MYDB["motd_messages"]


@APP.route("/")
def main():
    return render_template("index.html", data=MYCOL.find())


@APP.route("/menu/<string:ip>")
def menu(ip):
    router = MYCOL.find_one({"router_ipaddr": ip})
    if router:
        return render_template("menu.html", router_ip=ip)
    return redirect("/")

@APP.route("/add", methods=["POST"])
def add_router():
    router_ipaddr = request.form.get("router_ipaddr")
    username = request.form.get("username")
    password = request.form.get("password")

    if router_ipaddr and username and password:
        router_info = {
            "router_ipaddr": router_ipaddr,
            "username": username,
            "password": password,
        }
        MYCOL.insert_one(router_info)
    return redirect("/")


@APP.route("/delete", methods=["POST"])
def delete_router():
    id = request.form.get("_id")
    try:
        print(f"Del: {id}")
        MYCOL.delete_one({"_id": ObjectId(id)})
    except Exception:
        pass
    return redirect(url_for("main"))


@APP.route("/router/<string:ip>")
def show_interfaces(ip):
    return render_template(
        "show_interface.html", data=INFO.find({"router_ip": ip}), router_ip=ip
    )


@APP.route("/motd/<string:ip>", methods=["GET", "POST"])
def show_motd(ip):
    router = MYCOL.find_one({"router_ipaddr": ip})
    if not router:
        return redirect("/")

    if request.method == "POST":
        motd = request.form.get("motd")
        if motd:
            produce(RABBITMQ_HOST, json.dumps({
                "action": "set_motd",
                "router_ipaddr": ip,
                "message": motd,
                "username": router["username"],
                "password": router["password"]
            }).encode("utf-8"))
        return redirect(url_for("menu", ip=ip))

    # Get the latest MOTD message for this router
    latest_motd = MOTD.find_one(
        {"router_ip": ip},
        sort=[("timestamp", -1)]
    )

    current_motd = latest_motd["message"] if latest_motd["message"] != "" else "No MOTD set"
    return render_template("show_motd.html", router_ip=ip, motd=current_motd)

@APP.route('/configure_loopback/<ip>')
def configure_loopback(ip):
    data = INFO.find_one({'router_ip': ip}, sort=[("timestamp", -1)])
    loopback = [
        iface for iface in data.get("interfaces", [])
        if iface["interface"].startswith("Loopback")
    ]
    return render_template("configure_loopback.html", data=loopback, router_ip=ip)

@APP.route("/create_loopback", methods=["POST"])
def create_loopback():
    loopbackNumber = request.form.get("loopbackNumber")
    interface_ip = request.form.get("interface_ip")
    ip = request.form.get("router_ip")
    router = MYCOL.find_one({"router_ipaddr": ip})
    print(loopbackNumber, interface_ip, ip)
    produce(RABBITMQ_HOST, json.dumps({
        "action": "create_loopback",
        "router_ipaddr": ip,
        "loopback_number": loopbackNumber,
        "interface_ip": interface_ip,
        "username": router["username"],
        "password": router["password"]
    }).encode("utf-8"))
    return redirect(url_for("menu", ip=ip))

@APP.route("/delete_loopback", methods=["POST"])
def delete_loopback():
    loopbackNumber = request.form.get("interface_name")[8:]
    interface_ip = request.form.get("interface_ip")
    ip = request.form.get("router_ip")
    router = MYCOL.find_one({"router_ipaddr": ip})
    print(loopbackNumber, interface_ip, ip)
    produce(RABBITMQ_HOST, json.dumps({
                "action": "delete_loopback",
                "router_ipaddr": ip,
                "loopback_number": loopbackNumber,
                "interface_ip": interface_ip,
                "username": router["username"],
                "password": router["password"]
            }).encode("utf-8"))
    return redirect(url_for("menu", ip=ip))

if __name__ == "__main__":
    APP.run(host="0.0.0.0", port=8080)
