import os
from flask import Flask, request
import requests
import gspread
from google.oauth2.service_account import Credentials
import google.generativeai as genai
from datetime import datetime

# 1. ตั้งค่า LINE และ Gemini (ใส่ Key ของคุณให้ถูกต้อง)
LINE_ACCESS_TOKEN = "hv9ERohtfhe/2dqeOdem0Rcn0VRxMXKCWy/l7aVkEExFvGwpRKKUr8KSOsgRhxqoIwm+zU4Tk3t1QnDQy/jNJswcVeserDZQyaNxCxUMtELZrJxFHCzrXJGyndzAG95cMp+aRSCrlgXz415OaeeGlQdB04t89/1O/w1cDnyilFU="
GOOGLE_API_KEY = "AIzaSyBcA5eilUk3yDjymBvLJiLkhQHqUFs_muc" # จากรูปแรกของคุณ

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. ตั้งค่า Google Sheets
# ตรวจสอบว่าชื่อไฟล์ JSON ใน GitHub ตรงกับที่เขียนด้านล่างนี้นะครับ
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('service_account.json', scopes=scope)
client = gspread.authorize(creds)

# *** ใส่ชื่อไฟล์ Google Sheets ของคุณที่สร้างไว้ตรงนี้ ***
SHEET_NAME = "ไฟล์บอท อ่านไลน์" 
sheet = client.open(SHEET_NAME).sheet1

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is AI recording orders"

@app.route("/callback", methods=["POST"])
def callback():
    data = request.json
    if not data or 'events' not in data or len(data['events']) == 0:
        return "OK"

    event = data['events'][0]
    if event.get('type') == 'message' and event['message'].get('type') == 'text':
        user_message = event['message']['text']
        
        # ใช้ AI ช่วยแยกแยะออเดอร์
        prompt = f"Extract ordering information from this text: '{user_message}'. Output as 'Item, Amount'. If not an order, output 'None'."
        response = model.generate_content(prompt)
        ai_result = response.text.strip()

        if "None" not in ai_result:
            try:
                # บันทึกลง Sheets: [เวลา, ข้อความต้นฉบับ, ผลลัพธ์จาก AI]
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([now, user_message, ai_result])
                print(f"บันทึกออเดอร์สำเร็จ: {ai_result}")
            except Exception as e:
                print(f"Error recording to sheet: {e}")

    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


