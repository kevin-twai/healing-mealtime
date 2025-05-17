from flask import Flask, render_template, request, jsonify
import openai
import os
import requests

app = Flask(__name__)

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def ask_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        gender = data.get("gender")
        age = data.get("age")
        height = data.get("height")
        weight = data.get("weight")
        goal = data.get("goal")

        base = f"性別：{gender}，年齡：{age}，身高：{height}cm，體重：{weight}kg，目標：{goal}"

        prompts = {
            "📌 基本資料摘要": f"請根據以下資料，產出條列式摘要：{base}",
            "🍽 每日三餐建議": f"請根據以下資料，提供一週七天每日三餐建議（條列式）：{base}",
            "🍌 訓練前後飲食建議": f"根據以下資料，提供七天訓練前與訓練後的飲食建議（條列式）：{base}",
            "🏃‍♂️ 一週運動建議": f"根據以下資料，產出一週七天的運動建議（包含器材、方式、時間，條列式）：{base}"
        }

        reply = []
        for title, prompt in prompts.items():
            answer = ask_gpt(prompt)
            reply.append({"title": title, "content": answer})

        # 寫入 Notion（每日建議）
        notion_payload = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "標題": {"title": [{"text": {"content": f"{gender}-{goal} 建議"}}]},
                "建議": {"rich_text": [{"text": {"content": reply[1]["content"][:1900]}}]}
            }
        }
        requests.post("https://api.notion.com/v1/pages", headers=headers, json=notion_payload)

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500