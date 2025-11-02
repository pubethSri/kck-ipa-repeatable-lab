from flask import Flask
from flask import request
from flask import render_template
from flask import redirect
from flask import url_for

sample = Flask(__name__)

data = []

@sample.route("/")
def main():
    return render_template("index.html", data=data)

@sample.route("/add", methods=["POST"])
def add_comment():
    yourname = request.form.get("yourname")
    message = request.form.get("message")

    if yourname and message:
        data.append({"yourname": yourname, "message": message})
    return redirect(url_for("main"))

@sample.route("/delete", methods=["POST"])
def delete_comment():
    try:
        idx = int(request.form.get("idx"))
        if 0 <= idx < len(data):
            data.pop(idx)
    except Exception:
        pass
    return redirect(url_for("main"))

if __name__ == "__main__":
    sample.run(host="0.0.0.0", port=8080)