import sys
import os
import json

# Add current directory to path so we can import RAG system
sys.path.append("/home/cactus1549/Banking_webApp/logging")

try:
    from langchain_community.chat_models import ChatOllama
    from Data.RAG_system_knowledge_based import summarize_results
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

# Mock Data from User Logs
MOCKED_RESULTS = json.dumps([
  {
    "processed_at": None,
    "amount": 500.0,
    "transaction_type": "DEPOSIT",
    "description": "Transfer to savings",
    "transaction_status": "COMPLETED",
    "reference_number": "TXN1001",
    "fee_amount": 0.0,
    "currency": "USD"
  },
  {
    "processed_at": None,
    "amount": 200.0,
    "transaction_type": "WITHDRAWAL",
    "description": "Transfer to savings",
    "transaction_status": "COMPLETED",
    "reference_number": "TXN1001",
    "fee_amount": 0.0,
    "currency": "USD"
  },
  {
    "processed_at": "2025-10-05T08:18:15.948962+00:00",
    "amount": 100.0,
    "transaction_type": "TRANSFER",
    "description": "Transfer from checking to savings",
    "transaction_status": "COMPLETED",
    "reference_number": None,
    "fee_amount": None,
    "currency": "USD"
  },
  {
    "processed_at": "2025-12-09T10:13:08.123647+00:00",
    "amount": 22.3,
    "transaction_type": "TRANSFER",
    "description": "Test ",
    "transaction_status": "COMPLETED",
    "reference_number": None,
    "fee_amount": 0.0,
    "currency": "CAD"
  },
  {
    "processed_at": "2025-12-10T06:34:15.858696+00:00",
    "amount": 22.3,
    "transaction_type": "TRANSFER",
    "description": "Weekend Pizza",
    "transaction_status": "CANCELLED",
    "reference_number": None,
    "fee_amount": 0.0,
    "currency": "CAD"
  }
])

USER_QUERY = "can i get my last transactions ?"

def test_summarization():
    print("--- Starting Summarization Test ---")
    try:
        # Initialize LLM directly
        print("Initializing LLM (gemma3:4b)...")
        llm = ChatOllama(model="gemma3:4b")
        
        print(f"Calling summarize_results with {len(json.loads(MOCKED_RESULTS))} items...")
        
        # Call the function being tested
        summary = summarize_results(llm, MOCKED_RESULTS, USER_QUERY)
        
        print("\n--- TEST RESULT ---")
        print(summary)
        print("-------------------")
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_summarization()
