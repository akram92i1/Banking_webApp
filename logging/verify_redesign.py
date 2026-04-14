import asyncio
from typing import Dict, Any

from agent_types import UserContext, UserRole, GroceryProfile
from finance_agent import FinanceAgent
from grocery_agent import GroceryAgent

async def run_verification():
    print("Initializing Agents...")
    finance_agent = FinanceAgent()
    grocery_agent = GroceryAgent()
    
    context = UserContext(
        user_id="test_user",
        role=UserRole.USER,
        location="montreal",
        preferences={},
        transaction_history=[]
    )
    # The agent will automatically assign a mock grocery_profile in __post_init__ 
    
    print("\n--- Test 1: Ask Finance Agent about transactions ---")
    resp1 = await finance_agent.chat_with_agent("What are my recent transactions? I need to build a budget.", context)
    print("RESPONSE:\n", resp1)
    
    print("\n--- Test 2: Ask Finance Agent about Grocery Deals (Should decline) ---")
    resp2 = await finance_agent.chat_with_agent("Tell me my account balance, and also what is the price of apples at Maxi?", context)
    print("RESPONSE:\n", resp2)
    
    print("\n--- Test 3: Ask Grocery Agent for Meal Plan ---")
    resp3 = await grocery_agent.chat_with_agent("Can you generate a meal plan for my family? We have $30.", context)
    print("RESPONSE:\n", resp3)

if __name__ == "__main__":
    asyncio.run(run_verification())
