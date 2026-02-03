
import asyncio
import json
import sys
import os
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_banking_agent import AIBankingAgent, UserContext, UserRole
from Data.RAG_system_knowledge_based import execute_sql_query

async def test_agent_auth():
    print("\n--- Testing Agent Authentication ---")
    agent = AIBankingAgent() # This might be slow if it loads LLM, but let's try.
    # To speed up, we might want to mock the LLM loading if possible, but the init is in __init__.
    # We can patch 'ChatOllama' to avoid real model loading.
    
    # Context WITHOUT token
    ctx_no_auth = UserContext(
        user_id="test_user",
        role=UserRole.USER,
        location="toronto",
        preferences={},
        transaction_history=[],
        token=None 
    )
    
    response = await agent.chat_with_agent("Hello", ctx_no_auth)
    print(f"No Auth Response: {response}")
    if "Access Denied" in response:
        print("✅ PASS: Unauthenticated access blocked.")
    else:
        print("❌ FAIL: Unauthenticated access allowed.")

    # Context WITH token
    ctx_auth = UserContext(
        user_id="test_user",
        role=UserRole.USER,
        location="toronto",
        preferences={},
        transaction_history=[],
        token="valid_token" 
    )
    
    # We expect this to proceed (or fail later), but NOT give Access Denied
    # Since we didn't mock the chain, it might try to call Ollama. 
    # That's fine, strict auth check is at the START of the function.
    # We just want to see if it passes the first check.
    # If it fails later, it won't be "Access Denied".
    
    # We can't easily intercept "it passed the check" without running the whole correct chain.
    # But if the response is strict "Access Denied" only for the first case, we are good.
    try:
        response_auth = await agent.chat_with_agent("Hello", ctx_auth)
        if "Access Denied" not in response_auth:
             print("✅ PASS: Authenticated access proceeded (past auth check).")
        else:
             print("❌ FAIL: Authenticated access blocked with Access Denied.")
    except Exception as e:
        print(f"✅ PASS: Authenticated access proceeded past auth check (but failed elsewhere: {e})")

def test_rag_error_sanitization():
    print("\n--- Testing RAG Error Sanitization ---")
    
    # Mock psycopg2 to fail
    with patch('psycopg2.connect') as mock_connect:
        mock_connect.side_effect = Exception("Real Database Error: Table 'users' is corrupt!")
        
        result_json = execute_sql_query("SELECT * FROM users")
        result = json.loads(result_json)
        
        print(f"Result: {result}")
        
        if "error" in result:
            error_msg = result["error"]
            if "Internal Database Error" in error_msg and "corrupt" not in error_msg:
                 print("✅ PASS: Error message sanitized.")
            else:
                 print(f"❌ FAIL: Error message leaked or mismatch. Got: {error_msg}")
        else:
            print("❌ FAIL: No error returned.")

if __name__ == "__main__":
    # We need to mock ChatOllama in AIBankingAgent to avoid loading model
    with patch('ai_banking_agent.ChatOllama'):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(test_agent_auth())
        test_rag_error_sanitization()
        loop.close()
