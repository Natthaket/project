import requests
from app.config import ACCESS_TOKEN

def send_message_with_image(recipient_id, message, image_url):
    url = f'https://graph.facebook.com/v11.0/me/messages?access_token={ACCESS_TOKEN}'
    headers = {'Content-Type': 'application/json'}
    
    # ส่งรูปภาพ
    payload = {
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": image_url,
                    "is_reusable": True
                }
            }
        }
    }
    requests.post(url, json=payload, headers=headers)

    # ส่งข้อความเพิ่มเติม
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    requests.post(url, json=payload, headers=headers)

def send_message(recipient_id, message):
    url = f'https://graph.facebook.com/v11.0/me/messages?access_token={ACCESS_TOKEN}'
    headers = {'Content-Type': 'application/json'}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message}
    }
    requests.post(url, json=payload, headers=headers)
