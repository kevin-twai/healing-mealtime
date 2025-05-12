
from flask import Flask, render_template, request
import openai
import os

app = Flask(__name__)

# 從環境變數取得 OpenAI API 金鑰
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    meal_plan = ""
    if request.method == "POST":
        gender = request.form.get("gender", "")
        age = request.form.get("age", "")
        height = request.form.get("height", "")
        weight = request.form.get("weight", "")
        goal = request.form.get("goal", "")

        prompt = f"""
你是一位溫柔且療癒的健康飲食顧問。請根據以下用戶資訊，設計一份「七日健康飲食建議」，語氣請使用繁體中文，充滿鼓勵、療癒與實用性。每一天請提供：

1. 早餐、午餐、晚餐（每餐 1～2 個菜色）
2. 一句療癒語錄，幫助使用者面對生活壓力
3. 請使用條列格式顯示，每天標明「第X天」

用戶資料如下：
性別：{gender}
年齡：{age}
身高：{height} cm
體重：{weight} kg
目標：{goal}

請開始生成建議。
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位擅長療癒語氣的飲食顧問。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            meal_plan = response['choices'][0]['message']['content']
        except Exception as e:
            meal_plan = f"發生錯誤：{e}"

    return render_template("index.html", meal_plan=meal_plan)

if __name__ == "__main__":
    app.run(debug=True)
