
from flask import Flask, request, jsonify, render_template
import os
import requests
from openai import OpenAI

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

def ask_gpt(prompt, user_input, max_tokens=1000):
    response = client.chat.completions.create(
        model="gpt-4",
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content.strip()

def format_reply(text):
    return text.replace("\n", "<br>").replace("訓練前", "🔸 訓練前").replace("訓練後", "🔸 訓練後")

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    try:
        intro_prompt = (
            "請整理使用者的基本資料摘要，包含性別、年齡、身高、體重、目標，使用條列格式輸出。"
        )
        diet_prompt = (
            "請提供一週每日三餐建議（星期一至星期日），每一天請列出：早餐、午餐、晚餐，格式請用條列式與段落清楚。"
        )
        prepost_prompt = (
            "請針對星期一至星期日，列出每日的『訓練前飲食建議』與『訓練後飲食建議』，"
            "每天獨立列出，並清楚標示。"
        )
        fitness_prompt = (
            "請提供星期一至星期日的運動建議，每日包含：使用器材、訓練方式與訓練時間，格式用段落條列方式呈現。"
        )

        intro_text = ask_gpt(intro_prompt, user_input)
        diet_text = ask_gpt(diet_prompt, user_input)
        prepost_text = ask_gpt(prepost_prompt, user_input)
        fitness_text = ask_gpt(fitness_prompt, user_input)

        full_reply = (
            f"👤 使用者基本資料：<br>{format_reply(intro_text)}"
            f"<br><br>🍽️ 一週三餐建議：<br>{format_reply(diet_text)}"
            f"<br><br>🍌 訓練前後飲食建議：<br>{format_reply(prepost_text)}"
            f"<br><br>🏋️‍♀️ 一週運動建議：<br>{format_reply(fitness_text)}"
        )

        notion_payload = {
            "parent": { "database_id": DATABASE_ID },
            "properties": {
                "內容": { "title": [ { "text": { "content": user_input[:50] } } ] },
                "建議": {
                    "rich_text": [
                        {
                            "text": {
                                "content": (
                                    intro_text[:300]
                                    + "\n" + diet_text[:500]
                                    + "\n" + prepost_text[:300]
                                    + "\n" + fitness_text[:300]
                                )[:1900]
                            }
                        }
                    ]
                }
            }
        }
        requests.post("https://api.notion.com/v1/pages", json=notion_payload, headers=headers)
        return jsonify({ "reply": full_reply })

    except Exception as e:
        return jsonify({ "reply": f"⚠️ 發生錯誤：{str(e)}" })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
