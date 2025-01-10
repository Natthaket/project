from app import app
from pyngrok import ngrok, conf
import atexit
import os
import signal

def setup_ngrok():
    try:
        # กำหนดค่า config
        conf.get_default().config_path = "./ngrok.yml"
        
        # Kill existing sessions
        os.system('taskkill /f /im ngrok.exe')
        ngrok.kill()
        
        # Start new tunnel
        http_tunnel = ngrok.connect(5000)
        print(f'New Public URL: {http_tunnel.public_url}')
        return http_tunnel
    except Exception as e:
        print(f"Error setting up ngrok: {e}")
        return None

def cleanup(signum, frame):
    print("Cleaning up ngrok...")
    ngrok.kill()
    exit(0)

if __name__ == '__main__':
    # Register cleanup handler
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    tunnel = setup_ngrok()
    if tunnel:
        print("ngrok tunnel established successfully")
    app.run(port=5000)