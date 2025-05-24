from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# 設定你的 OpenAI API 金鑰
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        # 使用 GPT-4 並要求回傳格式為明確段落
        completion = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "你是一位專業健康顧問，請用繁體中文回應，分成四段清楚條列式內容。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1600
        )

        # 切割回應
        full_text = completion.choices[0].message.content.strip()
        sections = full_text.split("\n\n")  # 兩個換行為段落分界

        return jsonify({
            "section1": sections[0] if len(sections) > 0 else "無法取得建議",
            "section2": sections[1] if len(sections) > 1 else "無法取得建議",
            "section3": sections[2] if len(sections) > 2 else "無法取得建議",
            "section4": sections[3] if len(sections) > 3 else "無法取得建議",
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
