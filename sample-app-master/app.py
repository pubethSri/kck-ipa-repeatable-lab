from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask_socketio import SocketIO, emit

sample = Flask(__name__)
sample.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(sample, cors_allowed_origins="*")

data = []

@sample.route("/")
def main():
    return render_template("index.html", data=data)

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

if __name__ == "__main__":
    socketio.run(sample, host="0.0.0.0", port=8080, debug=True, allow_unsafe_werkzeug=True)