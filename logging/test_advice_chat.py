import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_advice_chat():
    print("--- Testing Advice Chat Route ---")
    
    # 1. Asking without budget/frequency
    payload1 = {
        "user_id": "test_user_001",
        "message": "I need some help planning my meals this week."
    }
    print(f"\n[User]: {payload1['message']}")
    
    response1 = requests.post(f"{BASE_URL}/advice-chat", json=payload1)
    if response1.status_code == 200:
        print(f"[AI Agent]: {response1.json().get('response')}")
    else:
        print(f"Error: {response1.status_code} - {response1.text}")
        
    time.sleep(1)
        
    # 2. Providing budget
    payload2 = {
        "user_id": "test_user_001",
        "message": "My budget is $75 and I shop weekly."
    }
    print(f"\n[User]: {payload2['message']}")
    
    response2 = requests.post(f"{BASE_URL}/advice-chat", json=payload2)
    if response2.status_code == 200:
        print(f"[AI Agent]: {response2.json().get('response')}")
    else:
        print(f"Error: {response2.status_code} - {response2.text}")

if __name__ == "__main__":
    test_advice_chat()
