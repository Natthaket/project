import os
from dotenv import load_dotenv
import pandas as pd

# โหลดไฟล์ .env
load_dotenv()

# ดึงเส้นทางไฟล์ CSV จาก .env
CSV_FILE_PATH = r"C:\Users\ACE\Downloads\ข้อมูลรถในร้านเดิอนธันวาคม - ชีต1.csv"  # ใช้ raw string หรือ "C:\\..."

def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)  # ใช้ file_path ที่รับมาจาก parameter
        return df
    except FileNotFoundError:
        raise FileNotFoundError("CSV file not found. Check the file path.")
    except Exception as e:
        raise Exception(f"Error reading CSV file: {e}")

# เรียกใช้ฟังก์ชันโหลดไฟล์ CSV
df = load_csv(CSV_FILE_PATH)
print(df.head())  # แสดง 5 แถวแรกของข้อมูล
