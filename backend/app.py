
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    # 模擬 GPT 回覆邏輯
    reply = f"收到你的紀錄：「{message}」，已寫入 Notion！"
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
