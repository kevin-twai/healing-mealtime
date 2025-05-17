
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

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一位專業的健康教練，根據使用者提供的個人資料，請產出一週的飲食與健身建議。\n"
                        "請依照以下格式嚴格條列並分段，避免長段文字：\n"
                        "===\n"
                        "👤 基本資料：\n"
                        "- 性別：...\n"
                        "- 年齡：...\n"
                        "- 身高：...\n"
                        "- 體重：...\n"
                        "- 目標：...\n\n"
                        "🥗 飲食建議（條列）：\n"
                        "1. 早餐：...\n"
                        "2. 午餐：...\n"
                        "3. 晚餐：...\n"
                        "4. 點心建議：...\n"
                        "5. 禁忌食物：...\n\n"
                        "🏃‍♂️ 運動建議（每週安排）：\n"
                        "- 週一：...\n"
                        "- 週二：...\n"
                        "- 週三：...\n"
                        "- 週四：...\n"
                        "- 週五：...\n"
                        "- 週六：...\n"
                        "- 週日：...\n"
                        "===\n"
                        "請依照上述格式嚴格輸出，內容要精簡明確，並便於複製貼到 Notion。"
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )
        gpt_reply = response.choices[0].message.content.strip()

        notion_payload = {
            "parent": { "database_id": DATABASE_ID },
            "properties": {
                "內容": { "title": [ { "text": { "content": user_input[:50] } } ] },
                "建議": { "rich_text": [ { "text": { "content": gpt_reply[:1900] } } ] }
            }
        }
        requests.post("https://api.notion.com/v1/pages", json=notion_payload, headers=headers)

        return jsonify({ "reply": gpt_reply })

    except Exception as e:
        return jsonify({ "reply": f"⚠️ 發生錯誤：{str(e)}" })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
