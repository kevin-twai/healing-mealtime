
from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("input", "")
    if not user_input:
        return jsonify({"error": "Missing input"}), 400

    # 分段請求與回應格式範例（模擬）
    sections = [
        {"title": "基本資料分析", "content": f"根據使用者輸入：{user_input}，這是基本資料分析結果。"},
        {"title": "一週飲食建議", "content": "這裡是一週每日三餐的飲食建議。"},
        {"title": "運動建議", "content": "這裡是針對減脂／健身等目標的運動建議。"},
        {"title": "訓練前後飲食建議", "content": "這裡是訓練前後應搭配的飲食建議。"}
    ]

    return jsonify({"sections": sections})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
