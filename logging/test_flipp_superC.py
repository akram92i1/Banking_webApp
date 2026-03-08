import requests
import json
import os

def export_super_c_json():
    # Montreal postal code
    postal_code = "H2Z1E9" # Downtown Montreal
    target_store = "super c"
    
    # 1. Fetch Flyers for Postal Code
    flyers_url = f"https://backflipp.wishabi.com/flipp/flyers?locale=en-ca&postal_code={postal_code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    print(f"Fetching flyers for {postal_code}...")
    try:
        response = requests.get(flyers_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch flyers. HTTP {response.status_code}")
            return
            
        data = response.json()
        flyers = data.get("flyers", [])
        
        # 2. Find the first Super C flyer
        super_c_fid = None
        for f in flyers:
            merchant = f.get("merchant", "").lower()
            if target_store in merchant:
                super_c_fid = f.get("id")
                print(f"Found Super C flyer! ID: {super_c_fid}")
                break
                
        if not super_c_fid:
            print("No active Super C flyer found.")
            return

        # 3. Fetch all items in that specific flyer
        item_url = f"https://backflipp.wishabi.com/flipp/flyers/{super_c_fid}?locale=en-ca"
        print(f"Fetching all items from Super C flyer (ID: {super_c_fid})...")
        
        item_response = requests.get(item_url, headers=headers)
        if item_response.status_code == 200:
            items_data = item_response.json()
            
            # 4. Save the raw JSON to a file
            output_file = "super_c_raw_data.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(items_data, f, indent=2, ensure_ascii=False)
                
            print(f"\nSUCCESS! Exported complete Super C JSON structure to {output_file}")
            print(f"Total items exported: {len(items_data.get('items', []))}")
            
        else:
            print(f"Failed to fetch items: HTTP {item_response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    export_super_c_json()
