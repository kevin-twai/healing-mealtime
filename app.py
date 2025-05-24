
from flask import Flask, request, jsonify, render_template
import openai
import os
import json

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    prompt = data.get("prompt", "")

    try:
        base_prompt = f"""
You are a professional health coach. Based on the following personal information, return 4 segments of advice in JSON format:
1. section1: summary of user's profile
2. section2: a week's daily meal suggestions (3 meals per day)
3. section3: pre- and post-workout meal suggestions
4. section4: a weekly workout plan (include equipment, method, and time)
User input: {prompt}
Format:
{{
  "section1": "...",
  "section2": "...",
  "section3": "...",
  "section4": "..."
}}
"""

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": base_prompt}],
            temperature=0.7,
        )

        reply = response.choices[0].message.content.strip()
        result = json.loads(reply)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
