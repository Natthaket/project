from flask import request, jsonify
from app.config import VERIFY_TOKEN, CSV_FILE_PATH
from app.models.load_data import load_csv
from app.recommender import content_based_recommender
from app.messenger import send_message, send_message_with_image
import logging

# ตั้งค่า logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# โหลดข้อมูลจาก CSV
try:
    df = load_csv(CSV_FILE_PATH)
    logger.info("CSV loaded successfully")
except Exception as e:
    df = None
    logger.error(f"Error loading CSV file: {e}")

# กำหนดคุณลักษณะที่จะใช้ในการแนะนำ
features = ['ชื่อสินค้า', 'ราคา', 'รูปภาพ']

def setup_routes(app):
    @app.route('/')
    def home():
        """หน้าแรกของ API"""
        return jsonify({"message": "Welcome to the Recommendation API!"})

    @app.route('/recommend', methods=['GET'])
    def recommend():
        """API สำหรับการแนะนำสินค้า"""
        product_name = request.args.get('product_name')
        
        if not product_name:
            return jsonify({"error": "กรุณาระบุชื่อสินค้า"}), 400

        if df is None:
            return jsonify({"error": "ไม่สามารถโหลดข้อมูลสินค้าได้"}), 500

        recommended_products = content_based_recommender(product_name, df, features)
        
        if 'error' in recommended_products:
            return jsonify(recommended_products), 404

        return jsonify(recommended_products), 200

    @app.route('/webhook', methods=['GET', 'POST'])
    def webhook():
        """Webhook สำหรับ Facebook Messenger"""
        if request.method == 'GET':
            # Debug logs
            logger.info(f"GET params: {request.args}")
            
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            logger.info(f"Verification attempt - Mode: {mode}, Token: {token}")
            
            # ตรวจสอบ token
            if mode and token:
                if mode == 'subscribe' and token == VERIFY_TOKEN:
                    logger.info("Webhook verified successfully")
                    return str(challenge)
                else:
                    logger.warning("Verification failed - Invalid token")
                    return 'Verification failed', 403
            
            logger.error("Invalid verification request")
            return 'Invalid request', 400

        elif request.method == 'POST':
            try:
                data = request.get_json()
                logger.info("Received webhook data")
                
                if not data:
                    logger.error("Empty payload received")
                    return 'Invalid payload', 400
                
                for entry in data.get('entry', []):
                    for messaging in entry.get('messaging', []):
                        try:
                            sender_id = messaging['sender']['id']
                            logger.info(f"Processing message from sender: {sender_id}")
                            
                            # ตรวจสอบว่ามีข้อความหรือไม่
                            if 'message' in messaging and 'text' in messaging['message']:
                                user_message = messaging['message']['text'].strip()
                                logger.info(f"Received message: {user_message}")
                                
                                if not user_message:
                                    send_message(sender_id, "กรุณาพิมพ์ข้อความที่ต้องการค้นหา")
                                    continue
                                
                                if df is None:
                                    send_message(sender_id, "ขออภัย ระบบไม่สามารถเข้าถึงข้อมูลสินค้าได้ในขณะนี้")
                                    continue

                                # แจ้งสถานะการค้นหา
                                send_message(sender_id, f"🔍 กำลังค้นหาสินค้าที่เกี่ยวกับ '{user_message}'...")
                                
                                # ค้นหาสินค้าที่แนะนำ
                                recommended_products = content_based_recommender(user_message, df, features)
                                
                                if 'recommendations' in recommended_products:
                                    recommendations = recommended_products['recommendations']
                                    if recommendations:
                                        for product in recommendations:
                                            message_text = (
                                                f"🚛 สินค้า: {product['ชื่อสินค้า']}\n"
                                                f"💰 ราคา: {product['ราคา']:,} บาท"
                                            )
                                            send_message_with_image(
                                                sender_id,
                                                message_text,
                                                product['รูปภาพ']
                                            )
                                            logger.info(f"Sent recommendation: {product['ชื่อสินค้า']}")
                                    else:
                                        send_message(sender_id, "❌ ไม่พบสินค้าที่ตรงกับการค้นหา")
                                else:
                                    error_message = recommended_products.get('error', 'เกิดข้อผิดพลาดในการค้นหา')
                                    send_message(sender_id, f"⚠️ {error_message}")
                                    logger.warning(f"Search error: {error_message}")
                            
                        except Exception as e:
                            logger.error(f"Error processing message: {e}", exc_info=True)
                            send_message(sender_id, "⚠️ ขออภัย เกิดข้อผิดพลาดในการประมวลผล")
                
                return 'OK', 200
                
            except Exception as e:
                logger.error(f"Error processing webhook: {e}", exc_info=True)
                return 'Error', 500

        return 'Method not allowed', 405

    return app