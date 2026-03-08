import requests
import json
import urllib.parse
from datetime import datetime

def test_flipp_api():
    # Montreal postal code
    postal_code = "H2Z1E9" # Downtown Montreal
    
    # Stores to check
    stores = ["Maxi", "IGA", "Super C"]
    
    # Products to look for (optional, if we want to search items instead of just store flyers)
    # The backflipp API search endpoint:
    url = f"https://backflipp.wishabi.com/flipp/flyers?locale=en-ca&postal_code={postal_code}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    print(f"Testing Flipp Flyers API for {postal_code}...")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            flyers = data.get("flyers", [])
            print(f"Found {len(flyers)} flyers.")
            
            target_stores_lower = [s.lower() for s in stores]
            
            target_flyer_ids = []
            for f in flyers:
                merchant = f.get("merchant", "").lower()
                for t in target_stores_lower:
                    if t in merchant:
                        print(f"Found {merchant} flyer! ID: {f.get('id')}")
                        target_flyer_ids.append(f.get("id"))
                        break
            
            if not target_flyer_ids:
                print("No flyers found for target stores.")
                return

            print(f"\nTarget flyer IDs: {target_flyer_ids}")
            
            # Now instead of fetching a full flyer, let's try searching specifically for meat
            # to see if weight info is provided in a search response.
            search_url = f"https://backflipp.wishabi.com/flipp/items/search?locale=en-ca&postal_code={postal_code}&q=beef"
            print(f"Searching for 'beef' to inspect weight pricing...")
            
            search_response = requests.get(search_url, headers=headers)
            if search_response.status_code == 200:
                search_data = search_response.json()
                items = search_data.get("items", [])
                
                print(f"Found {len(items)} beef items.")
                print("\nInspecting schema of top 3 beef items:")
                for item in items[:3]:
                    print(json.dumps(item, indent=2))
            else:
                print(f"Failed to fetch search items: HTTP {search_response.status_code}")
                
        else:
            print(f"Failed to fetch data: HTTP {response.status_code}")
            print(response.text[:200])
            
    except Exception as e:
        print(f"Error querying Flipp: {e}")

if __name__ == "__main__":
    test_flipp_api()
