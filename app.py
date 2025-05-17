
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
                        "你是一位專業的健康教練，根據使用者提供的個人資料，請產出一週的飲食與健身建議。
"
                        "請依照以下格式嚴格條列並分段，避免長段文字：
"
                        "===
"
                        "👤 基本資料：
"
                        "- 性別：...
"
                        "- 年齡：...
"
                        "- 身高：...
"
                        "- 體重：...
"
                        "- 目標：...

"
                        "🥗 飲食建議（條列）：
"
                        "1. 早餐：...
"
                        "2. 午餐：...
"
                        "3. 晚餐：...
"
                        "4. 點心建議：...
"
                        "5. 禁忌食物：...

"
                        "🏃‍♂️ 運動建議（每週安排）：
"
                        "- 週一：...
"
                        "- 週二：...
"
                        "- 週三：...
"
                        "- 週四：...
"
                        "- 週五：...
"
                        "- 週六：...
"
                        "- 週日：...
"
                        "===
"
                        "請依照上述格式嚴格輸出，內容要精簡明確，並便於複製貼到 Notion。"
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )
        gpt_reply = response.choices[0].message.content.strip()

        # 寫入 Notion
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
