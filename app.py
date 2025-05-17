
from flask import Flask, request, render_template, jsonify
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    messages = [{"role": "user", "content": f"你是一位專業的健康教練，根據使用者提供的基本資料：{user_input}，請產出以下格式回應：\n\n1. 基本資料摘要\n2. 每日三餐飲食建議（7日）\n3. 訓練前後飲食建議（條列式）\n4. 一週運動建議（含器材、訓練方式與時間）"}]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
