
from notion_client import Client
from datetime import datetime

NOTION_TOKEN = "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"
DATABASE_ID = "1f560966dde0800d9c7ecab993aa4d45"

notion = Client(auth=NOTION_TOKEN)

def write_to_notion(breakfast, lunch, dinner, quote, mood="", email=""):
    today = datetime.now().strftime("%Y-%m-%d")

    properties = {
        "日期": {"date": {"start": today}},
        "早餐": {"rich_text": [{"text": {"content": breakfast}}]},
        "午餐": {"rich_text": [{"text": {"content": lunch}}]},
        "晚餐": {"rich_text": [{"text": {"content": dinner}}]},
        "建議語錄": {"rich_text": [{"text": {"content": quote}}]},
    }

    if mood:
        properties["心情"] = {"select": {"name": mood}}

    if email:
        properties["用戶信箱"] = {"email": email}

    notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties=properties
    )
