import os
from flask import Flask, request
import gspread
from google.oauth2.service_account import Credentials
import google.generativeai as genai
from datetime import datetime

# 1. ตั้งค่า Token และ API Key (ของพี่ถูกต้องอยู่แล้ว)
LINE_ACCESS_TOKEN = "hv9ERohtfhe/2dqeOdem0Rcn0VRxMXKCWy/17aVkEExFvGwpRKKUr8KSOsgRhxqoIwm+zU4Tk3t1QnDQy/jNJswcVeserDZQyaNxCxUMtELZrJxFHCzrXJGyndzAG95cMp+aRSCrlgXz415OaeeGlQdB04t89/1O/w1cDnyilFU="
GOOGLE_API_KEY = "AIzaSyBcA5eilUk3yDjymBvLJiLkhQHqUFs_muc"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. เชื่อมต่อ Google Sheets
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
try:
    creds = Credentials.from_service_account_file('service_account.json', scopes=scope)
    client = gspread.authorize(creds)
    SHEET_NAME = "ไฟล์บอท อ่านไลน์" 
    sheet = client.open(SHEET_NAME).worksheet("Sheet1") # เปลี่ยนเป็นชื่อ Tab ของพี่
except Exception as e:
    print(f"เชื่อมต่อ Sheets พังเพราะ: {e}")

app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    data = request.json
    if not data or 'events' not in data:
        return "OK"

    for event in data['events']:
        if event.get('type') == 'message' and event['message'].get('type') == 'text':
            user_msg = event['message']['text']
            
            # สั่ง AI แยกแยะข้อมูลตามหัวตารางใหม่ (A-I)
            prompt = f"""
            จงแยกข้อมูลจากข้อความนี้: '{user_msg}' 
            เพื่อนำไปลงตารางที่มีหัวข้อ: สาขา, ชื่อสินค้า, ครบ, ไม่ครบ, ของไม่มี, ขาด, เกิน
            ตอบกลับเป็นรูปแบบ CSV 1 บรรทัด โดยใช้เครื่องหมาย | แยกคอลัมน์ ดังนี้:
            สาขา | ชื่อสินค้า | ครบ | ไม่ครบ | ของไม่มี | ขาด | เกิน
            (ตัวอย่าง: วงสว่าง | ขนมปัง | | 5 | | | )
            ถ้าไม่มีข้อมูลในช่องไหนให้ปล่อยว่างไว้
            """
            try:
                response = model.generate_content(prompt)
                ai_data = response.text.strip().split('|')
                
                # เตรียมข้อมูล 9 คอลัมน์ (A-I)
                # ลำดับ (A), วันที่ (B), สาขา (C), ชื่อสินค้า (D), ครบ (E), ไม่ครบ (F), ของไม่มี (G), ขาด (H), เกิน (I)
                now = datetime.now().strftime("%d/%m/%Y")
                
                # ล้างช่องว่างและจัดแถวข้อมูล
                clean_data = [item.strip() for item in ai_data]
                row_to_add = ["", now] + clean_data # เพิ่มคอลัมน์ ลำดับ และ วันที่ ข้างหน้า
                
                sheet.append_row(row_to_add)
            except Exception as e:
                print(f"Error: {e}")
    return "OK"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
