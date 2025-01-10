from flask import Flask
from app.routes import setup_routes  # เปลี่ยนเป็น setup_routes

app = Flask(__name__)

# ตั้งค่าเพิ่มเติม
app.config['JSON_AS_ASCII'] = False  # สำหรับการรองรับภาษาไทย

# ตั้งค่าเส้นทาง (Routes)
setup_routes(app)