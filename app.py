from flask import Flask, request, jsonify, render_template
import openai
import os

app = Flask(__name__)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_prompt(user_input, section):
    return f"你是一位專業健康教練，根據以下使用者資料：{user_input}，請提供「{section}」的建議，條列式說明並以繁體中文撰寫。"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        section = data.get("section")
        user_input = data.get("user_input")

        prompt = build_prompt(user_input, section)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return jsonify({"section": section, "content": response.choices[0].message.content.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500