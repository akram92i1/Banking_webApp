import requests
import json
import time
import sys

# Color codes
GREEN = '\033[92m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'

URL = "http://localhost:5000/api/chat"
HEADERS = {"Content-Type": "application/json"}

def test_query(message, query_type):
    print(f"\n{BLUE}--- Testing {query_type} ---{RESET}")
    print(f"User Query: '{message}'")
    
    payload = {
        "message": message,
        "user_id": "test_routing_user",
        "token": None # Will fallback to user_id in fastapi for testing
    }
    
    try:
        response = requests.post(URL, json=payload, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n{GREEN}Agent Response:{RESET}")
            print(data.get("response", "No response found"))
            return True
        else:
            print(f"\n{RED}Error Response (Status {response.status_code}):{RESET}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n{RED}Error: Could not connect to the API server. Is it running?{RESET}")
        return False

if __name__ == "__main__":
    print("Testing Query Routing Logic...")
    
    # Needs a moment if server is starting up
    time.sleep(2)
    
    # 1. Test standard DB query (should hit RAG/SQL)
    print("\n\n" + "="*50)
    test_query("What is my account balance?", "Database SQL Query")
    
    # 2. Test Market News query (should hit Research router)
    print("\n\n" + "="*50)
    test_query("Can you find me some grocery deals in Montreal?", "Market Research Query")
    
    print("\n\n" + "="*50)
    print("Verification complete.")
