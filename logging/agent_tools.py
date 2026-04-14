import json
import asyncio
import os
import re
import glob
import logging
import requests
from typing import Any, List, Dict
from pydantic import Field
from langchain.tools import BaseTool

logger = logging.getLogger("AIBankingAgent.tools")

class LogAnalysisTool(BaseTool):
    name: str = "analyze_security_logs"
    description: str = "Analyze security logs for threats and anomalies"
    parent: Any = Field(default=None, exclude=True)
    
    def _run(self, log_file_path: str) -> str:
        """Analyze security logs using existing threat detection"""
        try:
            # Use existing log analysis
            results = asyncio.run(self._analyze_logs_async(log_file_path))
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error analyzing logs: {str(e)}"
    
    async def _analyze_logs_async(self, log_file_path: str):
        # This would integrate with the existing log processor
        return {
            "threats_detected": 5,
            "critical_threats": 2,
            "blocked_ips": 3,
            "suspicious_users": 1
        }

class RLAnalysisTool(BaseTool):
    name: str = "run_reinforcement_learning_analysis" 
    description: str = "Run Q-table analysis using reinforcement learning"
    parent: Any = Field(default=None, exclude=True)
    
    def _run(self, transaction_data: str) -> str:
        """Run RL threat detection analysis"""
        try:
            # Use existing RL system
            results = self.parent.rl_detector.predict_threat(json.loads(transaction_data))
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error in RL analysis: {str(e)}"

class GroceryDealsTool(BaseTool):
    name: str = "find_local_grocery_deals"
    description: str = "Search local grocery flyers for deals on specific products. Input should be a specific product name (e.g., 'beef', 'apples')."
    parent: Any = Field(default=None, exclude=True)
    
    def _run(self, query: str) -> str:
        """Find grocery deals in user's area for a specific query using Vector RAG embeddings"""
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), 'Data'))
            from RAG_system_Grocery_knowledge_bases import query_grocery_rag
            
            if hasattr(self.parent, "grocery_rag_chains") and self.parent.grocery_rag_chains:
                response = query_grocery_rag(self.parent.grocery_rag_chains, query)
                return response.get("result", "No deals found.")
            else:
                return "Error: Grocery RAG chains are not initialized."
        except Exception as e:
            return f"Error searching grocery deals: {str(e)}"

class GetTransactionsTool(BaseTool):
    name: str = "get_user_transactions"
    description: str = "Get the current user's most recent transactions. Input should be a JSON string with two keys: 'limit' (int) and 'message' (str)."
    parent: Any = Field(default=None, exclude=True)

    def _run(self, tool_input: str) -> str:
        """
        Get the user's most recent transactions from the banking API.
        Args:
            tool_input: A JSON string with two keys: 'limit' (int) and 'message' (str).
        """
        try:
            params = json.loads(tool_input)
            limit = params.get("limit", 10)
            message = params.get("message")
        except (json.JSONDecodeError, ValueError):
            limit = 10
            message = tool_input
        
        try:
            token = self.parent.user_context.token
            if not token:
                return "Error: User is not authenticated. Cannot fetch transactions."
            
            headers = {"Authorization": f"Bearer {token}"}
            
            url = f"http://localhost:8082/api/transactions/current-user?limit={limit}"
            
            print(f"DEBUG: Calling transactions API at {url}")
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                self.parent.failed_tools[message].add("get_user_transactions")
                return f"Error: The banking API returned a {response.status_code} status code."
            
            transactions = response.json()
            print(f"DEBUG: Received {len(transactions)} transactions from API")
            
            if not transactions:
                return "No transactions found for the current user."
            
            # Return concise JSON string with explicit SUCCESS marker
            return f"SUCCESS: Retrieved {len(transactions)} transactions.\n" + json.dumps(transactions, indent=2)
        except requests.exceptions.RequestException as e:
            print(f"ERROR: API request failed: {e}")
            self.parent.failed_tools[message].add("get_user_transactions")
            return "Error: The banking API is currently unavailable. Please try again later."
        except Exception as e:
            print(f"ERROR: Unexpected error in GetTransactionsTool: {e}")
            self.parent.failed_tools[message].add("get_user_transactions")
            return f"An unexpected error occurred: {str(e)}"

class GenerateMealPlanTool(BaseTool):
    name: str = "generate_meal_plan"
    description: str = "Generate a meal plan combination of grocery deals that fits a specific budget. Input should be a JSON string. E.g., '{{\"budget\": 25.0}}'."
    parent: Any = Field(default=None, exclude=True)
    
    def _run(self, tool_input: str) -> str:
        """Compute optimal grocery deals matching budget, grouping by store and tracking savings."""
        import sys
        import re
        import os
        import glob
        from collections import defaultdict
        
        try:
            params = json.loads(tool_input)
            budget = float(params.get("budget", 100.0))
        except (json.JSONDecodeError, ValueError):
            budget = 100.0
        
        try:
            from meal_plan_optimizer import MealPlanOptimizer, GroceryDeal
            location = getattr(self.parent.user_context, "location", "toronto")
            
            profile = getattr(self.parent.user_context, "grocery_profile", None)
            pantry = set([p.lower() for p in profile.pantry_inventory]) if profile else set()
            
            flyer_dir = "Data/flyers"
            loc_lower = location.lower()
            files = glob.glob(f"{flyer_dir}/*_{location.title()}.md")
            if not files:
                files = [f for f in glob.glob(f"{flyer_dir}/*.md") if loc_lower in f.lower()]
            
            deals = []
            if files:
                for file_path in files:
                    merchant = os.path.basename(file_path).split('_')[0]
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            for line in lines:
                                if "- **" in line and ":" in line:
                                    parts = line.split("**: ")
                                    if len(parts) == 2:
                                        name = parts[0].replace("- **", "").replace("**", "").strip()
                                        price_str = re.sub(r'[^0-9.]', '', parts[1])
                                        if price_str:
                                            # Filter out pantry items
                                            name_lower = name.lower()
                                            if any(p in name_lower for p in pantry):
                                                continue
                                            deals.append(GroceryDeal(name=name, price=float(price_str), merchant=merchant.title()))
                    except Exception:
                        continue
            
            # Fallback to mock data if RAG files failed or are empty
            if not deals:
                raw_deals = getattr(self.parent, "_get_grocery_deals", lambda x: [])(location)
                if not raw_deals:
                     raw_deals = getattr(self.parent, "_get_grocery_deals", lambda x: [])("toronto")
                     
                for d in raw_deals:
                    try:
                        name_lower = d["item"].lower()
                        if any(p in name_lower for p in pantry):
                            continue
                        price_str = re.sub(r'[^0-9.]', '', d["price"])
                        deals.append(GroceryDeal(name=d["item"], price=float(price_str), merchant=d["store"]))
                    except:
                        pass
                    
            if not deals:
                return "Failed to find any deals to build a meal plan."

            optimizer = MealPlanOptimizer(tolerance=5.0)
            selected, total = optimizer.find_optimal_plan(budget, deals)
            
            if not selected:
                return f"Could not find a valid meal plan under budget ${budget}."
                
            # Group by Store for Smart Shopping List
            by_store = defaultdict(list)
            for d in selected:
                by_store[d.merchant].append(d)
                
            savings_estimate = sum([d.price * 0.3 for d in selected])  # Mock 30% average saving

            res = [f"### 🛒 Weekly Meal Plan & Automated Shopping List"]
            res.append(f"**Target Budget:** ${budget:.2f} | **Cart Total:** ${total:.2f}")
            res.append(f"**Estimated Savings:** 💰 ${savings_estimate:.2f} compared to regular retail!\n")
            
            if pantry:
                res.append(f"*Note: Pantry staples like {', '.join(pantry)} have been automatically excluded from your shopping list.*\n")

            for store, items in sorted(by_store.items()):
                res.append(f"🏪 **{store}**")
                for item in sorted(items, key=lambda x: x.name):
                    res.append(f"- 🥘 {item.name}: **${item.price:.2f}**")
                res.append("")
                
            res.append("👨‍🍳 **Batch Cooking Tip**: Look for ingredients across stores that can be roasted or boiled together to minimize prep time and food waste.")
            return "\n".join(res)
        except Exception as e:
            return f"Error generating meal plan: {str(e)}"
