import requests
import json
import time

# 1. Configuration
API_URL = "http://127.0.0.1:5000/improve-ai"
CONVERSATION_FILE = "conversation.json" # Ensure this file is in the same folder

def run_auto_training():
    try:
        with open(CONVERSATION_FILE, 'r') as f:
            data = json.load(f)
            
        #assuming conversations.json is a list of turns of intercations 
        for i, turn in enumerate(data):
            print(f"🔄 Training on Case #{i+1}...")
            
            payload = {
                "clientSequence": turn.get("client_message", ""),
                "chatHistory": turn.get("chat_history", []),
                "consultantReply": turn.get("consultant_reply", "")
            }
            
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                print(f"✅ Success! Prompt updated for: {turn.get('client_message')[:30]}...")
            else:
                print(f"❌ Failed: {response.text}")
            
            # CRITICAL: Sleep for 5 seconds to stay under Gemini Free Tier Rate Limits (RPM)
            time.sleep(5) 

    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    run_auto_training()