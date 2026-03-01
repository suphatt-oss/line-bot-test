import os
from flask import Flask, request
import requests

# เก็บไว้เฉยๆ หรือลบทิ้งก็ได้เพราะเราจะไม่สั่ง Reply แล้ว
LINE_CHANNEL_ACCESS_TOKEN = "hv9ERohtfhe/2dqeOdem0Rcn0VRxMXKCWy/l7aVkEExFvGwpRKKUr8KSOsgRhxqoIwm+zU4Tk3t1QnDQy/jNJswcVeserDZQyaNxCxUMtELZrJxFHCzrXJGyndzAG95cMp+aRSCrlgXz415OaeeGlQdB04t89/1O/w1cDnyilFU="

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is watching silently"

@app.route("/callback", methods=["POST"])
def callback():
    data = request.json
    if not data or 'events' not in data or len(data['events']) == 0:
        return "OK"

    event = data['events'][0]
    
    # บอทจะเช็คว่าเป็นข้อความตัวอักษรไหม
    if event.get('type') == 'message' and event['message'].get('type') == 'text':
        user_message = event['message']['text']
        user_name = event['source'].get('userId', 'Unknown') # เก็บ ID คนพิมพ์ไว้ก่อน
        
        # ส่วนนี้คือจุดที่บอท "อ่าน"
        print(f"อ่านเจอข้อความ: {user_message} จาก: {user_name}")
        
        # --- เราลบคำสั่ง requests.post(Reply) ทิ้งไปแล้ว บอทจะไม่ตอบอะไรเลย ---

    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
