
from flask import Flask, render_template, request, jsonify
import os
import openai

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    if not user_input:
        return jsonify({"reply": "請輸入訊息"}), 400

    # 模擬 GPT 分段回覆格式
    sections = [
        {"title": "基本資料", "content": f"你輸入的是：{user_input}"},
        {"title": "飲食建議", "content": "這是本週每日三餐建議"},
        {"title": "訓練前後建議", "content": "這是訓練前後建議"},
        {"title": "運動計劃", "content": "這是完整的一週運動建議"}
    ]
    reply = "\n\n".join([f"📌 {s['title']}\n{s['content']}" for s in sections])

    return jsonify({ "reply": reply })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
