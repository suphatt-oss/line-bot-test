import os
from flask import Flask, request
import requests

# เอา Token จาก LINE Developers มาใส่ตรงนี้
LINE_CHANNEL_ACCESS_TOKEN = "hv9ERohtfhe/2dqeOdem0Rcn0VRxMXKCWy/l7aVkEExFvGwpRKKUr8KSOsgRhxqoIwm+zU4Tk3t1QnDQy/jNJswcVeserDZQyaNxCxUMtELZrJxFHCzrXJGyndzAG95cMp+aRSCrlgXz415OaeeGlQdB04t89/1O/w1cDnyilFU="

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

@app.route("/callback", methods=["POST"])
def callback():
    data = request.json
    if not data or 'events' not in data or len(data['events']) == 0:
        return "OK"

    event = data['events'][0]
    if event.get('type') == 'message' and event['message'].get('type') == 'text':
        reply_token = event['replyToken']
        user_message = event['message']['text']
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
        }
        payload = {
            'replyToken': reply_token,
            'messages': [{'type': 'text', 'text': f"บอทตอบจาก Render: {user_message}"}]
        }
        # ใช้ .me ตามที่คุยกันเพื่อเลี่ยงปัญหา Proxy
        requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, json=payload)
    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

