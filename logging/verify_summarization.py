
import asyncio
import json
import sys
import os
from unittest.mock import MagicMock, patch

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_banking_agent import AIBankingAgent
from Data.RAG_system_knowledge_based import summarize_results

async def test_summarization():
    print("\n--- Testing Response Summarization ---")
    
    # Mock LLM to return a "concise" response (since we can't run real LLM)
    # But wait, we want to test that the PROMPT is correct.
    # We can inspect the prompt sent to the LLM if we mock the generic `invoke`.
    
    with patch('Data.RAG_system_knowledge_based.ChatOllama') as MockOllama:
        mock_llm = MockOllama.return_value
        mock_llm.invoke.return_value = "Concise Response"
        
        raw_data = [
            {"id": "uuid-123", "amount": 2.50, "desc": "Ticket", "date": "2025-12-10"}
        ]
        
        # We need to manually trigger the function that uses the prompt.
        # summarize_results in RAG uses a passed-in 'llm'.
        
        summarize_results(mock_llm, raw_data, "Did anyone send me money?")
        
        # Check calls
        calls = mock_llm.invoke.call_args_list
        if not calls:
            print("❌ FAIL: LLM not invoked.")
            return

        last_call_arg = calls[0][0][0] # The prompt string
        
        print("Prompt sent to LLM:")
        print(last_call_arg)
        
        if "Filter the Data" in last_call_arg and "Ignore technical fields" in last_call_arg:
            print("✅ PASS: Prompt contains new filter instructions.")
        else:
             print("❌ FAIL: Prompt missing new instructions.")

        if "Answer Directly" in last_call_arg:
             print("✅ PASS: Prompt instruction for direct answer found.")

if __name__ == "__main__":
    asyncio.run(test_summarization())
