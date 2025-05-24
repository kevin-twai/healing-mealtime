
from flask import Flask, request, jsonify, render_template
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def call_gpt(prompt, system_message="你是一位專業的健康顧問，請根據使用者提供的資料提供具體清楚的建議"):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=1200
    )
    return response['choices'][0]['message']['content']

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        prompt = data.get("prompt", "")
        if not prompt:
            return jsonify({"error": "未提供 prompt"}), 400

        sections = [
            "基本資料摘要分析（包含 BMI、健康目標評估）",
            "每日三餐飲食建議（具體列出早餐、午餐、晚餐）",
            "訓練前後的飲食建議（具體食材與時間建議）",
            "一週運動建議（包含器材、方式與時間建議）"
        ]

        results = []
        for i, topic in enumerate(sections):
            sub_prompt = f"{prompt}\n請僅產生以下內容第 {i+1} 段：{topic}，請條列清楚、具體豐富"
            reply = call_gpt(sub_prompt)
            results.append(reply)

        return jsonify({
            "section1": results[0],
            "section2": results[1],
            "section3": results[2],
            "section4": results[3]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
