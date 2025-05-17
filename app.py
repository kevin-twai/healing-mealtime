
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
        if any(day in line for day in ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]):
            line = f"<br>🍽️ <b>{line.strip()}</b>"
        elif "早餐" in line or "午餐" in line or "晚餐" in line:
            line = f"- {line.strip()}"
        elif "訓練前" in line or "訓練後" in line:
            line = f"🔸 {line.strip()}"
        elif "器材" in line:
            line = f"  - 使用器材：{line.split('：')[-1].strip()}"
        elif "訓練方式" in line:
            line = f"  - 訓練方式：{line.split('：')[-1].strip()}"
        elif "時間" in line:
            line = f"  - 時間：{line.split('：')[-1].strip()}"
        formatted.append(line)
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
            max_tokens=1000,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一位專業健康教練，請根據使用者提供的性別、年齡、身高、體重與目標，提供以下完整建議：\n"
                        "1. 👤 基本資料（條列）\n"
                        "2. 🥗 一週每日三餐飲食建議（星期一到星期日，各列出 早餐、午餐、晚餐）\n"
                        "   - 每天請額外補充：訓練前飲食建議、訓練後飲食建議\n"
                        "3. 🏋️‍♀️ 運動建議（週一～週日，包含：使用器材、訓練方式、訓練時間）\n"
                        "請使用清楚段落與條列方式輸出，避免自由敘述與過長句。"
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
