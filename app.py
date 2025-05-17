
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    # 模擬回應內容
    return jsonify({"reply": f"已接收訊息「{user_input}」，並記錄成功！"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
