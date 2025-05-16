
from flask import Flask, render_template, request
from openai import OpenAI
from notion_writer import write_to_notion
import os
import re

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    result_text = ""
    if request.method == "POST":
        plan_type = request.form.get("plan_type", "daily")
        gender = request.form.get("gender", "")
        age = request.form.get("age", "")
        height = request.form.get("height", "")
        weight = request.form.get("weight", "")
        goal = request.form.get("goal", "")
        mood = request.form.get("mood", "")
        email = request.form.get("email", "")

        if plan_type == "daily":
            prompt = f"""
你是一位溫柔且療癒的健康飲食顧問。請根據以下用戶資訊，設計「今日」的健康飲食建議。請提供：

1. 早餐、午餐、晚餐建議（各 1～2 道菜）
2. 一句鼓勵語錄
3. 請用條列式格式輸出

用戶資料：
性別：{gender}
年齡：{age}
身高：{height} cm
體重：{weight} kg
目標：{goal}
"""
        else:
            prompt = f"""
你是一位溫柔且療癒的健康顧問。請根據以下用戶資訊，設計一份「四週健身＋飲食建議」計畫，包含每週：

1. 每日三餐建議（簡潔）
2. 運動安排（訓練部位、動作名稱、組數）
3. 每週一句激勵語錄

請用繁體中文，每週用【第X週】開頭，條列呈現。

用戶資料：
性別：{gender}
年齡：{age}
身高：{height} cm
體重：{weight} kg
目標：{goal}
"""

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一位擅長療癒語氣與健康規劃的顧問。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1500
            )
            result_text = response.choices[0].message.content

            if plan_type == "daily":
                breakfast = re.findall(r"早餐[:：](.*)", result_text)
                lunch = re.findall(r"午餐[:：](.*)", result_text)
                dinner = re.findall(r"晚餐[:：](.*)", result_text)
                quote = re.findall(r"(?:語錄|鼓勵語|療癒語錄)[:：]?(.*)", result_text)

                b = breakfast[0].strip() if breakfast else ""
                l = lunch[0].strip() if lunch else ""
                d = dinner[0].strip() if dinner else ""
                q = quote[0].strip() if quote else ""

                write_to_notion(b, l, d, q, mood, email)

        except Exception as e:
            result_text = f"發生錯誤：{e}"

    return render_template("index.html", result=result_text)

if __name__ == "__main__":
    app.run(debug=True)
