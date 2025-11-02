from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask import jsonify
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from bson import ObjectId

sample = Flask(__name__)
sample.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(sample, cors_allowed_origins="*")

# MongoDB Connection
mongo_client = MongoClient('mongodb://mongo:27017/')
db = mongo_client['ipa2025']
routers_collection = db['routers']

data = []

@sample.route("/")
def main():
    routers = list(routers_collection.find())
    return render_template("index.html", data=data, routers=routers)

@socketio.on('send_message')
def handle_message(json_data):
    yourname = json_data.get('yourname')
    message = json_data.get('message')
    ip_address = request.remote_addr
    
    print(f"Received message from {yourname} ({ip_address}): {message}")
    
    if yourname and message:
        message_data = {
            "yourname": yourname, 
            "message": message, 
            "ip_address": ip_address
        }
        data.append(message_data)
        # ส่งข้อความไปยังทุกคนที่เชื่อมต่ออยู่
        print(f"Broadcasting message to all clients: {message_data}")
        emit('new_message', message_data, broadcast=True)

@sample.route("/delete", methods=["POST"])
def delete_comment():
    try:
        idx = int(request.form.get("idx"))
        if 0 <= idx < len(data):
            data.pop(idx)
            # แจ้งให้ทุกคนรีเฟรช
            socketio.emit('message_deleted', {'index': idx}, broadcast=True)
    except Exception:
        pass
    return redirect(url_for("main"))

# Router Management Routes
@sample.route("/router/add", methods=["POST"])
def add_router():
    try:
        ip = request.form.get("ip")
        username = request.form.get("username")
        password = request.form.get("password")
        
        if ip and username and password:
            router_data = {
                "ip": ip,
                "username": username,
                "password": password
            }
            routers_collection.insert_one(router_data)
            socketio.emit('router_added', router_data, broadcast=True)
    except Exception as e:
        print(f"Error adding router: {e}")
    
    return redirect(url_for("main"))

@sample.route("/router/delete/<router_id>", methods=["POST"])
def delete_router(router_id):
    try:
        routers_collection.delete_one({"_id": ObjectId(router_id)})
        socketio.emit('router_deleted', {'id': router_id}, broadcast=True)
    except Exception as e:
        print(f"Error deleting router: {e}")
    
    return redirect(url_for("main"))

@sample.route("/router/list", methods=["GET"])
def get_routers():
    try:
        routers = list(routers_collection.find())
        for router in routers:
            router['_id'] = str(router['_id'])
        return jsonify(routers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    socketio.run(sample, host="0.0.0.0", port=8080, debug=True, allow_unsafe_werkzeug=True)