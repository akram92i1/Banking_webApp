import requests
import json

def test_financial_advice_endpoint():
    print("Testing /api/user/financial-advice endpoint...")
    url = "http://localhost:8000/api/user/financial-advice"
    
    # Mock payload
    payload = {
        "user_id": "test_user",
        "spending_data": {"week1": 100.0},
        "category": "grocery",
        "target_reduction": 10.0
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if "success" in data and data["success"]:
                advice = data["advice"]
                print("\n✅ Endpoint Success!")
                
                # Verify new fields
                if "spending_by_category" in advice:
                    print("✅ Found 'spending_by_category'")
                    print(json.dumps(advice["spending_by_category"], indent=2))
                else:
                    print("❌ Missing 'spending_by_category'")

                if "financial_news" in advice:
                    print("✅ Found 'financial_news'")
                    print(f"   News items count: {len(advice['financial_news'])}")
                else:
                    print("❌ Missing 'financial_news'")
            else:
                print("❌ API returned failure response")
                print(data)
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")

if __name__ == "__main__":
    test_financial_advice_endpoint()
