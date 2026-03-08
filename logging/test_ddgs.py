import time
from datetime import datetime
from duckduckgo_search import DDGS

try:
    with DDGS() as ddgs:
        queries = [
            f"grocery flyer deals Montreal {datetime.now().strftime('%B %Y')}",
            "Montreal Canada weekly grocery flyer deals",
            "Maxi IGA Metro Provigo Montreal flyer deals this week",
            "Montreal grocery sales flyers discounts"
        ]
        
        for q in queries:
            print(f"\n--- Query: {q} ---")
            results = list(ddgs.text(q, max_results=2, region='wt-wt'))
            if results:
                for r in results:
                    print(f"- {r.get('title')}: {r.get('body')[:100]}...")
            else:
                print("No results.")
            time.sleep(1) # Be nice to the API
except Exception as e:
    print(f"Error: {e}")
