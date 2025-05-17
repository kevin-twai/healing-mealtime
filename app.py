
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

def format_reply(text):
    lines = text.split("\n")
    formatted = []
    for line in lines:
        if "性別" in line or "身高" in line or "體重" in line or "目標" in line:
            if not line.startswith("-"):
                line = "- " + line.strip()
        elif any(x in line for x in ["早餐", "午餐", "晚餐", "點心", "禁忌"]):
            if not line.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
                line = f"- {line.strip()}"
        elif "週" in line and "：" in line:
            line = "- " + line.strip()
        elif any(day in line for day in ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]):
            line = f"<br>🍽️ <b>{line.strip()}</b>"
        formatted.append(line.strip())
    return "\n".join(formatted)

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
                        "你是一位健康教練，根據使用者的個人資料與目標，請產出完整建議。\n"
                        "內容請包含：\n"
                        "👤 基本資料（條列）\n"
                        "🥗 飲食建議：提供一週每日三餐詳細菜單（星期一到星期日）\n"
                        "🏃‍♂️ 運動建議：每週安排（例如週一至週日的健身活動建議）\n"
                        "請使用段落與條列式格式，避免自由敘述"
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )
        raw_reply = response.choices[0].message.content.strip()
        gpt_reply = format_reply(raw_reply)
        gpt_html = gpt_reply.replace("\n", "<br>")

        notion_payload = {
            "parent": { "database_id": DATABASE_ID },
            "properties": {
                "內容": { "title": [ { "text": { "content": user_input[:50] } } ] },
                "建議": { "rich_text": [ { "text": { "content": gpt_reply[:1900] } } ] }
            }
        }
        requests.post("https://api.notion.com/v1/pages", json=notion_payload, headers=headers)

        return jsonify({ "reply": gpt_html })

    except Exception as e:
        return jsonify({ "reply": f"⚠️ 發生錯誤：{str(e)}" })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
