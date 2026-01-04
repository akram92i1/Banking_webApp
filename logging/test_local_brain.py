import asyncio
import logging
from ai_banking_agent import AIBankingAgent

# Configure logging to see full output
logging.basicConfig(level=logging.INFO)

async def test_brain():
    print("Initializing Agent...")
    agent = AIBankingAgent() # Uses default model
    
    schema = """
    Transactions: [transaction_id, from_account_id, amount, description, processed_at]
    Accounts: [account_id, user_id, type, balance]
    Users: [user_id, username, email]
    """
    
    user_id = "test_user_123"
    
    # Test 1: Chat Intent
    print("\n--- TEST 1: CHAT ---")
    msg1 = "Hi, who are you?"
    resp1 = await agent.process_user_intent(msg1, schema, user_id)
    print(f"Response: {resp1}")
    
    # Test 2: Query Intent
    print("\n--- TEST 2: QUERY ---")
    msg2 = "What was my last transaction?"
    resp2 = await agent.process_user_intent(msg2, schema, user_id)
    print(f"Response: {resp2}")

if __name__ == "__main__":
    asyncio.run(test_brain())
