import asyncio
import os
import sys
import re
import logging
import requests
from datetime import datetime
from typing import List

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fallback postal codes for major Canadian cities to use with Flipp API
CITY_POSTAL_CODES = {
    "montreal": "H2Z1E9",
    "toronto": "M5V2A8",
    "vancouver": "V6B2W2",
    "calgary": "T2P2G8",
    "ottawa": "K1P5G4",
    "edmonton": "T5J2Z2",
    "quebec": "G1R2B5",
    "halifax": "B3J3A5",
    "winnipeg": "R3C1R3"
}

def get_postal_code_for_location(location: str) -> str:
    """Get a generic downtown postal code for a given city to query flyers."""
    loc_lower = location.lower()
    for city, postal in CITY_POSTAL_CODES.items():
        if city in loc_lower:
            return postal
    # Default to Montreal if unknown
    return "H2Z1E9"

def fetch_flipp_grocery_deals(location: str) -> str:
    """Fetch flyer details directly from Flipp API for Maxi, IGA, Super C, etc."""
    postal_code = get_postal_code_for_location(location)
    logger.info(f"Using postal code {postal_code} for location {location}")
    
    # Base URL for fetching nearby flyers
    flyers_url = f"https://backflipp.wishabi.com/flipp/flyers?locale=en-ca&postal_code={postal_code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    target_stores = ["maxi", "iga", "super c", "metro", "provigo", "walmart"]
    
    flyer_section_parts = []
    
    try:
        # 1. Fetch all flyers in the area
        response = requests.get(flyers_url, headers=headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch flyers API. HTTP {response.status_code}")
            return f"- Error fetching flyer directory for {location}."
            
        data = response.json()
        flyers = data.get("flyers", [])
        
        # 2. Filter for our specific grocery stores
        found_flyers = []
        seen_merchants = set()
        
        for f in flyers:
            merchant = f.get("merchant", "").lower()
            # Only keep one flyer per merchant to avoid duplicates (e.g., standard vs premium flyer)
            if merchant in seen_merchants:
                continue
                
            for store in target_stores:
                if store in merchant:
                    found_flyers.append({
                        "id": f.get("id"),
                        "merchant": f.get("merchant")
                    })
                    seen_merchants.add(merchant)
                    break
        
        if not found_flyers:
            return f"- No current flyers found for Maxi, IGA, Super C, etc. in {location}."
            
        logger.info(f"Found flyers for: {[f['merchant'] for f in found_flyers]}")
        
        # 3. For the top 4 flyers, fetch their specific items
        for f in found_flyers[:4]:
            fid = f["id"]
            merchant_name = f["merchant"]
            
            items_url = f"https://backflipp.wishabi.com/flipp/flyers/{fid}?locale=en-ca"
            item_resp = requests.get(items_url, headers=headers, timeout=10)
            
            if item_resp.status_code == 200:
                items_data = item_resp.json()
                items = items_data.get("items", [])
                
                if items:
                    logger.info(f"Sample item for {merchant_name}: {items[0]}")
                    
                deal_lines = []
                # Find deals that actually have a price listed
                for item in items:
                    name = item.get("name", "").strip()
                    price = item.get("price") or item.get("current_price") or item.get("price_text")
                    
                    if name and price and not item.get("is_clipped"):
                        # Format the price nicely with pre and post text
                        price_str = str(price)
                        if not price_str.startswith("$"):
                            price_str = f"${price_str}"
                            
                        pre_text = item.get("pre_price_text")
                        if pre_text:
                            price_str = f"{pre_text.strip()} {price_str}"
                            
                        post_text = item.get("post_price_text")
                        if post_text:
                            price_str = f"{price_str} {post_text.strip()}"
                            
                        deal_lines.append(f"- **{name}**: {price_str}")
                        
                if deal_lines:
                    flyer_section_parts.append(f"\n**{merchant_name} Flyer Deals:**")
                    # Just show top 100 deals per store
                    flyer_section_parts.extend(deal_lines[:100])
                    
                    # --- NEW: Export for RAG Training ---
                    try:
                        os.makedirs("Data/flyers", exist_ok=True)
                        safe_merchant = "".join(c for c in merchant_name if c.isalnum() or c in " _-").strip().replace(" ", "_")
                        file_path = f"Data/flyers/{safe_merchant}_{location}.txt"
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(f"Grocery Flyer Deals for {merchant_name} in {location}\n")
                            f.write("="*50 + "\n\n")
                            f.write("\n".join(deal_lines))
                        logger.info(f"Exported {len(deal_lines)} deals to {file_path} for RAG training.")
                    except Exception as export_e:
                        logger.warning(f"Failed to export {merchant_name} deals to file: {export_e}")

            else:
                logger.warning(f"Failed to fetch items for {merchant_name} (ID: {fid})")
                
    except Exception as e:
        logger.error(f"Error querying Flipp API: {e}")
        return f"- Market research API error: {str(e)}"
        
    if not flyer_section_parts:
        return f"- Could not extract specific deal items for {location}."
        
    return "\n".join(flyer_section_parts)

def _perform_market_research(location: str, interest_topics: List[str] = None) -> str:
    """
    Perform active market research using direct API integrations.
    """
    if not interest_topics:
        interest_topics = ["grocery"]

    research_context = []
    
    # 1. Grocery Flyer Deals using Flipp API
    if "grocery" in interest_topics:
        deals_text = fetch_flipp_grocery_deals(location)
        research_context.append(f"### Grocery Flyer Deals – {location}:\n{deals_text}")

    if not research_context:
        return "Market research completed but no relevant news was found."

    return "\n\n".join(research_context)

if __name__ == "__main__":
    print("--- Testing Flipp-based Market Research ---")
    
    result = _perform_market_research("Montreal", ["grocery"])
    
    print("\n" + "="*80)
    print(result)
    print("="*80 + "\n")
