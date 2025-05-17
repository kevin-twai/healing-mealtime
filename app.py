from flask import Flask, request, render_template, jsonify
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

PROMPT_TEMPLATE = """
你是一位專業的健康教練，使用者提供了以下個人資料：

性別：{gender}
年齡：{age}
身高：{height} cm
體重：{weight} kg
目標：{goal}

請根據這些資料，依照下列格式產生建議，每一段落清楚條列，並使用繁體中文：
1. 📌 基本資料摘要
2. 🍽 每日三餐飲食建議（一週）
3. 🍌 訓練前後飲食建議
4. 🏃‍♂️ 一週完整運動建議（含器材、方式與時間）
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form["user_input"]
        gender, age, height, weight, goal = user_input.split("，")

        prompt = PROMPT_TEMPLATE.format(
            gender=gender.strip(),
            age=age.strip(),
            height=height.strip(),
            weight=weight.strip(),
            goal=goal.strip()
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            reply = response.choices[0].message.content
            return jsonify({"response": reply})
        except Exception as e:
            return jsonify({"error": str(e)})

    return render_template("index.html")
