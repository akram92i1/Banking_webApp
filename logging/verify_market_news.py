import asyncio
import os
import sys
import json
from datetime import datetime

# Ensure we can import the agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_banking_agent import AIBankingAgent, UserContext, UserRole, FinancialAdvice

async def test_market_news():
    print("--- Starting Market News Verification ---")
    
    # 1. Initialize Agent
    try:
        agent = AIBankingAgent()
        print("✅ Agent initialized successfully.")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return

    # 2. Mock Data
    user_context = UserContext(
        user_id="test_user",
        role=UserRole.USER,
        location="Toronto",
        preferences={},
        transaction_history=[],
        token="test_token"
    )
    
    spending_data = {
        "grocery": 150.00,
        "transport": 50.00,
        "entertainment": 30.00
    }
    
    # 3. Test _perform_market_research directly first
    print("\nTesting _perform_market_research directly...")
    try:
        if hasattr(agent, '_perform_market_research'):
            research_result = await asyncio.to_thread(agent._perform_market_research, "Toronto", ["grocery", "inflation"])
            print(f"✅ Market Research Result Length: {len(research_result)}")
            if len(research_result) > 100:
                print(f"✅ Snippet: {research_result[:200]}...")
            else:
                print(f"⚠️ Result seems short: {research_result}")
        else:
            print("❌ Agent does not have _perform_market_research method.")
    except Exception as e:
        print(f"❌ Error during direct research test: {e}")

    # 4. Test provide_financial_advice (Full Flow)
    print("\nTesting provide_financial_advice (Full Integration)...")
    try:
        advice = await agent.provide_financial_advice(
            user_context=user_context,
            spending_data=spending_data,
            category="grocery"
        )
        
        print("\n--- Advice Result ---")
        print(f"Action Plan: {advice.action_plan[:100]}...")
        
        if advice.financial_news:
             print(f"✅ Financial News Found ({len(advice.financial_news)} items):")
             for item in advice.financial_news:
                 print(f"  - {item}")
        else:
            print("⚠️ No financial news parsed in the final JSON.")
        
        print("\n✅ Verification Complete.")
        
    except Exception as e:
        print(f"❌ Error during advice generation: {e}")

if __name__ == "__main__":
    asyncio.run(test_market_news())
