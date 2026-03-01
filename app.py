import os
from flask import Flask, request
import gspread
from google.oauth2.service_account import Credentials
import google.generativeai as genai

# 1. ข้อมูลส่วนตัวของคุณ
LINE_ACCESS_TOKEN = "hv9ERohtfhe/2dqeOdem0Rcn0VRxMXKCWy/l7aVkEExFvGwpRKKUr8KSOsgRhxqoIwm+zU4Tk3t1QnDQy/jNJswcVeserDZQyaNxCxUMtELZrJxFHCzrXJGyndzAG95cMp+aRSCrlgXz415OaeeGlQdB04t89/1O/w1cDnyilFU="
GOOGLE_API_KEY = "AIzaSyBcA5eilUk3yDjymBvLJiLkhQHqUFs_muc"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. เชื่อมต่อ Google Sheets
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
try:
    # อ่านไฟล์กุญแจจาก GitHub
    creds = Credentials.from_service_account_file('service_account.json', scopes=scope)
    client = gspread.authorize(creds)
    
    # *** ใส่ชื่อไฟล์ Google Sheets ของคุณให้ถูกต้อง ***
    SHEET_NAME = "ไฟล์บอท อ่านไลน์" 
    sheet = client.open(SHEET_NAME).sheet1
except Exception as e:
    print(f"เชื่อมต่อ Sheets พังเพราะ: {e}")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is watching..."

@app.route("/callback", methods=["POST"])
def callback():
    data = request.json
    if not data or 'events' not in data:
        return "OK"

    for event in data['events']:
        if event.get('type') == 'message' and event['message'].get('type') == 'text':
            msg = event['message']['text']
            # AI ช่วยแยกออเดอร์
            prompt = f"Extract order: '{msg}'. Format: 'Item, Amount'. If none, reply 'None'."
            try:
                response = model.generate_content(prompt)
                res = response.text.strip()
                if "None" not in res:
                    sheet.append_row([msg, res])
            except:
                pass
    return "OK"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
