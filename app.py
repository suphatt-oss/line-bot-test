import os
from flask import Flask, request
import gspread
from google.oauth2.service_account import Credentials
import google.generativeai as genai
from datetime import datetime

# 1. ข้อมูล Token และ API Key ของพี่
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
    sheet = client.open(SHEET_NAME).sheet1 # มั่นใจว่าชื่อ Tab ด้านล่างคือ Sheet1 นะครับ
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
            user_message = event['message']['text']
            
            # สั่งให้ AI แยกข้อมูลตามหัวตารางใหม่ของพี่
            prompt = f"""
            จากข้อความ: '{user_message}' 
            จงแยกข้อมูลเพื่อลงตาราง (ลำดับ, วันที่, สาขา, ชื่อสินค้า, ครบ, ไม่ครบ, ของไม่มี, ขาด, เกิน)
            ตอบกลับเป็น CSV 1 บรรทัดเท่านั้น โดยใช้เครื่องหมาย | แยกคอลัมน์ 
            (ตัวอย่าง: |02/03/2026|วงสว่าง|ขนมปัง|||5|| )
            ถ้าคอลัมน์ไหนไม่มีข้อมูลให้ปล่อยว่างไว้
            """
            try:
                response = model.generate_content(prompt)
                ai_result = response.text.strip().split('|')
                
                # ทำความสะอาดข้อมูลนิดนึง
                final_row = [item.strip() for item in ai_result]
                
                # ถ้า AI ตอบมายาวเกินหรือสั้นไป ให้ใช้แค่วันที่วันนี้ใส่ไปก่อน
                if len(final_row) < 2: 
                    continue

                # วันที่ (คอลัมน์ B)
                final_row[1] = datetime.now().strftime("%d/%m/%Y")
                
                sheet.append_row(final_row)
                print(f"จดลงตารางสำเร็จ: {final_row}")
            except Exception as e:
                print(f"AI หรือ Sheets พังเพราะ: {e}")

    return "OK"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
