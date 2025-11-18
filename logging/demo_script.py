#!/usr/bin/env python3
"""
Complete Demo Script for AI Banking Agent
Shows both admin and user functionalities
"""

import asyncio
import json
from datetime import datetime, timedelta

# Import our AI agent components
from ai_banking_agent import AIBankingAgent, UserContext, UserRole


async def run_complete_demo():
    """
    Complete demonstration of the AI Banking Agent
    Shows both admin security features and user financial advisory
    """
    
    print("🏦" + "="*70)
    print("    AI BANKING AGENT WITH LANGCHAIN - COMPLETE DEMO")
    print("="*73)
    print("This demo showcases:")
    print("🔒 Admin: Security threat detection & analysis")
    print("💰 User: Financial advisory & spending optimization")
    print("🤖 LangChain: AI-powered insights & recommendations")
    print("="*73)
    
    # Initialize the AI agent
    print("\n🚀 Initializing AI Banking Agent...")
    try:
        agent = AIBankingAgent(ollama_model="llama3.2")  # Use llama3.2 or mistral
        print("✅ AI Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        print("💡 And model is available: ollama pull llama3.2")
        return
    
    await demo_admin_security_features(agent)
    await demo_user_financial_features(agent)
    await demo_chat_interactions(agent)
    await demo_real_world_scenarios(agent)
    
    # Cleanup
    agent.close()
    print("\n✅ Demo completed successfully!")
    print("\nNext steps:")
    print("1. Start the Flask API: python api_server.py")
    print("2. Start the React frontend: npm start")
    print("3. Interact with the AI Assistant in the web interface")


async def demo_admin_security_features(agent):
    """Demonstrate admin security analysis capabilities"""
    
    print("\n" + "🔒" + "="*60)
    print("ADMIN SECURITY ANALYSIS DEMO")
    print("="*62)
    
    # Create admin context
    admin_context = UserContext(
        user_id="admin001",
        role=UserRole.ADMIN,
        location="toronto",
        preferences={"notifications": True, "alert_level": "high"},
        transaction_history=[]
    )
    
    print(f"👤 Admin User: {admin_context.user_id}")
    print(f"📍 Location: {admin_context.location}")
    
    # Test Case 1: High-risk transaction analysis
    print("\n🎯 Test Case 1: High-Risk Transaction Analysis")
    print("-" * 50)
    
    suspicious_transaction = {
        "transaction_id": "txn_001",
        "amount": 25000,  # High amount
        "timestamp": datetime.now().isoformat(),
        "merchant_type": "unknown",
        "location": "foreign_country",
        "user_id": "user_12345",
        "device_fingerprint": "unknown_device",
        "ip_address": "45.142.212.61"  # Suspicious IP
    }
    
    print(f"💳 Transaction Amount: ${suspicious_transaction['amount']:,}")
    print(f"🌍 Location: {suspicious_transaction['location']}")
    print(f"📱 Device: {suspicious_transaction['device_fingerprint']}")
    
    try:
        threat_analysis = await agent.analyze_security_threats(
            transaction_data=suspicious_transaction,
            user_context=admin_context
        )
        
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"   🚨 Threat Detected: {threat_analysis.threat_detected}")
        print(f"   📋 Threat Type: {threat_analysis.threat_type}")
        print(f"   📈 Confidence Score: {threat_analysis.confidence_score:.2%}")
        print(f"   ⚠️  Severity Level: {threat_analysis.severity}")
        print(f"   💡 Recommendation: {threat_analysis.recommendation}")
        print(f"   📝 Explanation: {threat_analysis.explanation[:100]}...")
        
    except Exception as e:
        print(f"❌ Error in threat analysis: {e}")
    
    # Test Case 2: Admin chat for security queries
    print("\n🎯 Test Case 2: Admin Security Chat")
    print("-" * 50)
    
    security_queries = [
        "What are the current top security threats in our system?",
        "Analyze the log files for the last 24 hours",
        "Show me patterns in failed login attempts",
    ]
    
    for query in security_queries:
        print(f"\n👤 Admin Query: {query}")
        try:
            response = await agent.chat_with_agent(query, admin_context)
            print(f"🤖 AI Response: {response[:150]}...")
        except Exception as e:
            print(f"❌ Chat error: {e}")
    
    # Test Case 3: Generate security report
    print("\n🎯 Test Case 3: Security Report Generation")
    print("-" * 50)
    
    try:
        report = await agent.generate_admin_report(admin_context)
        print(f"📈 Report Type: {report['report_type']}")
        print(f"🕐 Generated At: {report['generated_at']}")
        print(f"🧠 AI Insights: {report['ai_insights'][:200]}...")
        
    except Exception as e:
        print(f"❌ Report generation error: {e}")


async def demo_user_financial_features(agent):
    """Demonstrate user financial advisory capabilities"""
    
    print("\n" + "💰" + "="*60)
    print("USER FINANCIAL ADVISORY DEMO")
    print("="*62)
    
    # Create user context
    user_context = UserContext(
        user_id="akram001",
        role=UserRole.USER,
        location="toronto",
        preferences={"budget_alerts": True, "deal_notifications": True},
        transaction_history=[]
    )
    
    print(f"👤 User: {user_context.user_id}")
    print(f"📍 Location: {user_context.location}")
    
    # Test Case 1: Spending analysis and advice
    print("\n🎯 Test Case 1: Weekly Spending Analysis")
    print("-" * 50)
    
    # Simulate 4 weeks of grocery spending
    spending_data = {
        "week1": 125.50,  # Reasonable
        "week2": 165.30,  # Higher than usual
        "week3": 145.80,  # Above average
        "week4": 180.20   # Concerning
    }
    
    total_spending = sum(spending_data.values())
    avg_weekly = total_spending / len(spending_data)
    
    print(f"📊 Spending Pattern (4 weeks):")
    for week, amount in spending_data.items():
        trend = "📈" if amount > avg_weekly else "📉"
        print(f"   {trend} {week}: ${amount:.2f}")
    print(f"   💰 Total: ${total_spending:.2f}")
    print(f"   📊 Average: ${avg_weekly:.2f}/week")
    
    try:
        advice = await agent.provide_financial_advice(
            user_context=user_context,
            spending_data=spending_data,
            category="grocery",
            target_reduction=25.00  # Try to save $25/week
        )
        
        print(f"\n🧠 AI FINANCIAL ANALYSIS:")
        print(f"   📈 Current Weekly Spending: ${advice.weekly_spending:.2f}")
        print(f"   🎯 Recommended Reduction: ${advice.recommended_reduction:.2f}")
        print(f"   📝 Summary: {advice.analysis_summary}")
        
        print(f"\n💡 SAVINGS SUGGESTIONS:")
        for i, suggestion in enumerate(advice.savings_suggestions[:4], 1):
            print(f"   {i}. {suggestion}")
        
        print(f"\n🛒 LOCAL GROCERY DEALS:")
        for deal in advice.grocery_deals[:3]:
            print(f"   🏪 {deal['store']}: {deal['item']} - {deal['price']} ({deal['discount']})")
        
        print(f"\n📋 ACTION PLAN:")
        print(f"   {advice.action_plan}")
        
    except Exception as e:
        print(f"❌ Error in financial analysis: {e}")
    
    # Test Case 2: Different spending scenarios
    print("\n🎯 Test Case 2: Various Spending Scenarios")
    print("-" * 50)
    
    scenarios = [
        {
            "name": "Student Budget",
            "data": {"week1": 45.20, "week2": 52.30, "week3": 38.80, "week4": 41.70},
            "target": 10.00
        },
        {
            "name": "Family Spending", 
            "data": {"week1": 220.50, "week2": 245.30, "week3": 235.80, "week4": 260.20},
            "target": 40.00
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Scenario: {scenario['name']}")
        avg_spending = sum(scenario['data'].values()) / len(scenario['data'])
        print(f"   Average: ${avg_spending:.2f}/week")
        
        try:
            quick_advice = await agent.provide_financial_advice(
                user_context=user_context,
                spending_data=scenario['data'],
                target_reduction=scenario['target']
            )
            print(f"   💡 Top Suggestion: {quick_advice.savings_suggestions[0][:80]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")


async def demo_chat_interactions(agent):
    """Demonstrate natural language chat capabilities"""
    
    print("\n" + "💬" + "="*60)
    print("NATURAL LANGUAGE CHAT DEMO")
    print("="*62)
    
    # Create both user contexts
    admin_context = UserContext("admin001", UserRole.ADMIN, "toronto", {}, [])
    user_context = UserContext("user001", UserRole.USER, "montreal", {}, [])
    
    # Conversation examples
    conversations = [
        {
            "context": admin_context,
            "role": "ADMIN",
            "messages": [
                "What security threats should I be most concerned about?",
                "How effective is our current threat detection system?",
                "Generate a summary of this week's security incidents"
            ]
        },
        {
            "context": user_context, 
            "role": "USER",
            "messages": [
                "I spent $180 on groceries this week, is that normal?",
                "What are some ways to reduce my food expenses?",
                "Find me deals on groceries in Montreal"
            ]
        }
    ]
    
    for conversation in conversations:
        print(f"\n👤 {conversation['role']} CONVERSATION:")
        print("-" * 40)
        
        for message in conversation['messages']:
            print(f"\n👤 {conversation['role']}: {message}")
            
            try:
                response = await agent.chat_with_agent(message, conversation['context'])
                # Limit response length for demo
                response_preview = response[:200] + "..." if len(response) > 200 else response
                print(f"🤖 AI: {response_preview}")
                
            except Exception as e:
                print(f"❌ Chat error: {e}")


async def demo_real_world_scenarios(agent):
    """Demonstrate real-world banking scenarios"""
    
    print("\n" + "🌍" + "="*60)
    print("REAL-WORLD SCENARIO SIMULATIONS")
    print("="*62)
    
    # Scenario 1: Fraud Detection
    print("\n🚨 Scenario 1: Credit Card Fraud Detection")
    print("-" * 50)
    
    admin_context = UserContext("security_admin", UserRole.ADMIN, "toronto", {}, [])
    
    fraud_transaction = {
        "amount": 3500,
        "location": "unknown_location",
        "timestamp": "03:30 AM",  # Unusual time
        "merchant": "online_electronics",
        "user_id": "regular_customer_001",
        "card_present": False,
        "previous_locations": ["toronto", "toronto", "toronto"]  # Sudden location change
    }
    
    print(f"💳 Suspicious Transaction:")
    print(f"   Amount: ${fraud_transaction['amount']}")
    print(f"   Time: {fraud_transaction['timestamp']}")  
    print(f"   Location: {fraud_transaction['location']}")
    print(f"   User History: {fraud_transaction['previous_locations']}")
    
    fraud_query = f"""
    Analyze this transaction for fraud:
    Amount: ${fraud_transaction['amount']} at {fraud_transaction['timestamp']}
    Location change from {fraud_transaction['previous_locations']} to {fraud_transaction['location']}
    Should this be flagged?
    """
    
    try:
        fraud_response = await agent.chat_with_agent(fraud_query, admin_context)
        print(f"\n🤖 AI Fraud Analysis: {fraud_response[:300]}...")
    except Exception as e:
        print(f"❌ Fraud analysis error: {e}")
    
    # Scenario 2: Budget Optimization
    print("\n💰 Scenario 2: Family Budget Optimization")
    print("-" * 50)
    
    user_context = UserContext("family_user", UserRole.USER, "vancouver", {}, [])
    
    family_spending = {
        "groceries_week1": 285.50,
        "groceries_week2": 310.30, 
        "groceries_week3": 295.80,
        "groceries_week4": 320.20
    }
    
    avg_family_spending = sum(family_spending.values()) / 4
    print(f"👨‍👩‍👧‍👦 Family Grocery Spending:")
    print(f"   Monthly Total: ${sum(family_spending.values()):.2f}")
    print(f"   Weekly Average: ${avg_family_spending:.2f}")
    
    budget_query = f"""
    Our family of 4 spends ${avg_family_spending:.2f} weekly on groceries in Vancouver.
    We want to reduce this by $50 per week without sacrificing nutrition.
    What specific strategies would you recommend?
    """
    
    try:
        budget_response = await agent.chat_with_agent(budget_query, user_context)
        print(f"\n🤖 AI Budget Advice: {budget_response[:300]}...")
    except Exception as e:
        print(f"❌ Budget advice error: {e}")
    
    # Scenario 3: Investment Advisory
    print("\n📈 Scenario 3: Investment Advisory")
    print("-" * 50)
    
    investment_query = """
    I have $500 extra each month after all expenses and want to start investing.
    I'm 28 years old, moderate risk tolerance, living in Toronto.
    What investment strategy would you recommend for someone in my situation?
    """
    
    try:
        investment_response = await agent.chat_with_agent(investment_query, user_context)
        print(f"💡 Investment Question: {investment_query[:100]}...")
        print(f"🤖 AI Investment Advice: {investment_response[:300]}...")
    except Exception as e:
        print(f"❌ Investment advice error: {e}")


def print_system_requirements():
    """Print system requirements and setup instructions"""
    
    print("\n" + "⚙️" + "="*60)
    print("SYSTEM REQUIREMENTS & SETUP")
    print("="*62)
    
    print("""
📋 REQUIREMENTS:
   • Python 3.8+
   • Ollama (Local LLM server)
   • Node.js 16+ (for React frontend)
   • 8GB+ RAM (for LLM)

🛠️ SETUP STEPS:

1. Install Ollama:
   curl -fsSL https://ollama.ai/install.sh | sh

2. Pull AI model:
   ollama pull llama3.2

3. Install Python dependencies:
   cd logging/
   pip install -r requirement.txt

4. Install frontend dependencies:
   cd finance_front_end/
   npm install lucide-react

5. Start services:
   # Terminal 1: Start Ollama
   ollama serve
   
   # Terminal 2: Start AI API
   python logging/api_server.py
   
   # Terminal 3: Start React app  
   npm start

🌐 ACCESS POINTS:
   • Frontend: http://localhost:3000
   • AI API: http://localhost:5001
   • Banking API: http://localhost:8082

💡 TIPS:
   • Ensure sufficient RAM for Ollama
   • Use smaller models (mistral) for lower-end hardware
   • Check firewall settings for local APIs
   • Monitor system resources during AI inference
    """)


if __name__ == "__main__":
    print("🚀 Starting AI Banking Agent Demo...")
    
    # Print setup information
    print_system_requirements()
    
    # Ask user if they want to continue
    response = input("\n❓ Do you have Ollama running and llama3.2 model available? (y/n): ")
    
    if response.lower() in ['y', 'yes']:
        try:
            # Run the complete demo
            asyncio.run(run_complete_demo())
        except KeyboardInterrupt:
            print("\n⏹️ Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            print("\n🔧 Troubleshooting:")
            print("1. Check if Ollama is running: curl http://localhost:11434/api/tags")
            print("2. Verify model is available: ollama list")
            print("3. Check Python dependencies: pip list")
    else:
        print("\n📋 Please complete the setup steps above before running the demo.")
        print("💡 Start with: ollama serve && ollama pull llama3.2")