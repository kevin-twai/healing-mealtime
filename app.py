
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
            line = "- " + line.strip()
        elif "週" in line and "：" in line or "星期" in line:
            line = "🔹 " + line.strip()
        elif "使用器材" in line:
            line = "  - 使用器材：" + line.split("：")[-1].strip()
        elif "訓練方式" in line:
            line = "  - 訓練方式：" + line.split("：")[-1].strip()
        elif "時間" in line:
            line = "  - 時間：" + line.split("：")[-1].strip()
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
                        "你是一位專業健康教練，請根據使用者的性別、年齡、身高、體重與目標，"
                        "提供以下完整建議：\n"
                        "1. 👤 基本資料（條列）\n"
                        "2. 🥗 飲食建議（每日三餐，每週七天）\n"
                        "3. 🏋️‍♀️ 運動建議（週一～週日，且每項包含「使用器材」、「訓練方式」、「訓練時間」）\n"
                        "請用清楚段落與條列格式回答，禁止自由敘述。"
                    )
                },
                {"role": "user", "content": user_input}
            ]
        )
        raw_reply = response.choices[0].message.content.strip()
        gpt_reply = format_reply(raw_reply)
        gpt_html = gpt_reply.replace("\n", "<br>")

        # 寫入 Notion
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
