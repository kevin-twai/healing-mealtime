
from flask import Flask, render_template, request
import openai

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("user_input", "")
    # 這裡是 GPT 呼叫的簡化版，實際部署時請加入 GPT 回應邏輯
    response = f"這是你輸入的內容：{user_input}"
    return render_template("index.html", user_input=user_input, response=response)

if __name__ == "__main__":
    app.run()
