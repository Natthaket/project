import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# ฟังก์ชันโหลดไฟล์ CSV
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        raise FileNotFoundError("CSV file not found. Check the file path.")
    except Exception as e:
        raise Exception(f"Error reading CSV file: {e}")

# ฟังก์ชันเรคคอมเมนเดอร์
def content_based_recommender(title, metadata, features):
    # รวมข้อมูลจากฟีเจอร์ที่กำหนด
    content = metadata[features].copy()

    # แปลงข้อมูลในคอลัมน์ให้เป็น lower case
    for feature in features:
        content[feature] = content[feature].astype(str).str.lower()

    # รวมฟีเจอร์ทั้งหมดเป็นข้อความเดียว
    content['combined'] = content[features].agg(' '.join, axis=1)

    # ใช้ TF-IDF แปลงข้อมูล
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(content['combined'])

    # คำนวณ cosine similarity
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # สร้าง mapping ระหว่างชื่อสินค้าและ index
    indices = pd.Series(content.index, index=content['ชื่อสินค้า'].str.strip().str.lower()).drop_duplicates()

    # ตรวจสอบว่าชื่อสินค้ามีอยู่ในฐานข้อมูลหรือไม่
    try:
        idx = indices[title.lower().strip()]
    except KeyError:
        return {"error": f"ไม่พบสินค้า '{title}' ในฐานข้อมูล"}

    # คำนวณคะแนนความคล้ายคลึงและเรียงลำดับ
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:4]  # เลือกสินค้า 3 รายการที่คล้ายที่สุด
    product_indices = [i[0] for i in sim_scores]

    # คืนค่าข้อมูลสินค้าแนะนำ
    recommended_products = metadata.iloc[product_indices][['ชื่อสินค้า', 'รูปภาพ']]
    return {"recommendations": recommended_products.to_dict(orient='records')}

# เส้นทางไฟล์ CSV
CSV_FILE_PATH = r"C:\Users\ACE\Downloads\ข้อมูลรถในร้านเดิอนธันวาคม - ชีต1.csv"

# โหลดข้อมูล
df = load_csv(CSV_FILE_PATH)

# ระบุคอลัมน์ที่ใช้ในการแนะนำสินค้า
features = ['ชื่อสินค้า', 'ยี่ห้อ', 'สเปค', 'หมวดหมู่']

# ระบุชื่อสินค้าที่ต้องการค้นหา
product_name = "FTR 240"

# เรียกใช้ฟังก์ชันแนะนำสินค้า
recommendations = content_based_recommender(product_name, df, features)

# แสดงผลลัพธ์
if "error" in recommendations:
    print(recommendations["error"])
else:
    print("สินค้าที่แนะนำ:")
    for rec in recommendations["recommendations"]:
        print(f"ชื่อสินค้า: {rec['ชื่อสินค้า']}, รูปภาพ: {rec['รูปภาพ']}")
