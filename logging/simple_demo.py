#!/usr/bin/env python3
"""
Simplified Demo for AI Banking Agent
Works without complex dependencies for quick testing
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

# Check if LangChain is available
try:
    from langchain_ollama import ChatOllama
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
    print("✅ LangChain dependencies available")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    print(f"⚠️  LangChain not available: {e}")
    print("💡 Install with: pip install langchain langchain-ollama langchain-core")

# Mock classes for when LangChain isn't available
class MockLLM:
    def __init__(self, model="mock"):
        self.model = model
    
    async def ainvoke(self, prompt):
        # Return mock responses based on prompt content
        if "security" in prompt.lower() or "threat" in prompt.lower():
            return type('Response', (), {
                'content': """Based on the security data analysis:

🚨 THREAT ANALYSIS SUMMARY:
- Current threat level: MODERATE
- Detected 3 potential security incidents in the last 24 hours
- 2 blocked IP addresses from suspicious locations
- 1 user account flagged for unusual login patterns

🔍 KEY FINDINGS:
- Failed login attempts increased by 15% compared to last week
- Suspicious transaction patterns detected from IP 45.142.212.61
- Potential credential stuffing attack identified

💡 RECOMMENDATIONS:
1. Implement additional rate limiting on login endpoints
2. Review and update fraud detection algorithms
3. Consider implementing 2FA for high-risk accounts
4. Monitor the flagged user account closely

The system is performing well overall, but vigilance is required."""
            })()
        
        elif "money" in prompt.lower() or "grocery" in prompt.lower() or "spending" in prompt.lower():
            return type('Response', (), {
                'content': """💰 FINANCIAL ANALYSIS & RECOMMENDATIONS:

📊 SPENDING ANALYSIS:
Based on your grocery spending patterns, here are my insights:

Current Average: $140.45/week
Target Reduction: $25-30/week (18-21% savings)
Potential Annual Savings: $1,300-$1,560

💡 PERSONALIZED SAVINGS STRATEGIES:

1. **Smart Shopping Timing**
   - Shop Wednesday evenings for best markdowns
   - Use store apps for digital coupons (save $10-15/week)

2. **Bulk Buying Strategy**
   - Focus on non-perishables when on sale
   - Rice, pasta, canned goods (save $8-12/week)

3. **Local Deal Optimization**
   - Metro: 20% off bananas this week
   - Loblaws: Buy 2 get 1 free ground beef
   - No Frills: $0.50 off bread

4. **Meal Planning**
   - Plan meals around sales (save $5-8/week)
   - Prep vegetables to reduce waste

🎯 ACTION PLAN:
Week 1: Implement store apps and digital coupons
Week 2: Start bulk buying strategy for staples  
Week 3: Begin meal planning around store sales
Week 4: Review and optimize based on results

This approach should help you reach your $25/week savings goal! 🎉"""
            })()
        
        else:
            return type('Response', (), {
                'content': """Hello! I'm your AI Banking Assistant. I can help with:

🔒 **For Admins**: Security analysis, threat detection, log analysis
💰 **For Users**: Financial advice, spending analysis, saving tips

How can I assist you today?"""
            })()

class SimpleBankingAgent:
    """Simplified AI Banking Agent for demo purposes"""
    
    def __init__(self):
        if LANGCHAIN_AVAILABLE:
            try:
                self.llm = ChatOllama(model="llama3.2", temperature=0.1)
                self.llm_type = "ollama"
                print("✅ Using Ollama LLM")
            except Exception as e:
                print(f"⚠️  Ollama not available: {e}")
                self.llm = MockLLM()
                self.llm_type = "mock"
        else:
            self.llm = MockLLM()
            self.llm_type = "mock"
        
        self.conversation_history = []
        
    async def chat_response(self, message: str, user_role: str = "user", user_location: str = "toronto") -> str:
        """Generate chat response"""
        
        # Add context based on user role
        if user_role == "admin":
            system_prompt = """You are a cybersecurity expert for a banking system. 
            Analyze security threats, provide actionable insights, and prioritize risks.
            Focus on practical recommendations for banking security."""
        else:
            system_prompt = """You are a financial advisor specializing in personal budgeting and savings.
            Help users optimize spending, find deals, and achieve financial goals.
            Provide practical, actionable advice."""
        
        full_prompt = f"{system_prompt}\n\nUser location: {user_location}\nUser query: {message}"
        
        try:
            if self.llm_type == "ollama" and LANGCHAIN_AVAILABLE:
                response = await self.llm.ainvoke(full_prompt)
                return response.content if hasattr(response, 'content') else str(response)
            else:
                response = await self.llm.ainvoke(full_prompt)
                return response.content
                
        except Exception as e:
            return f"I apologize, but I encountered an error: {e}. Please try again with a different question."
    
    async def analyze_spending(self, spending_data: Dict[str, float], user_location: str = "toronto") -> Dict[str, Any]:
        """Analyze user spending patterns"""
        
        total_spending = sum(spending_data.values())
        avg_spending = total_spending / len(spending_data)
        weeks = len(spending_data)
        
        # Calculate trends
        values = list(spending_data.values())
        trend = "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "stable"
        
        # Generate advice
        advice_prompt = f"""
        Analyze this spending pattern and provide savings advice:
        
        Weekly spending: {spending_data}
        Location: {user_location}
        Average: ${avg_spending:.2f}/week
        Trend: {trend}
        
        Provide specific savings strategies.
        """
        
        advice = await self.chat_response(advice_prompt, user_role="user", user_location=user_location)
        
        return {
            "total_spending": total_spending,
            "average_weekly": avg_spending,
            "trend": trend,
            "weeks_analyzed": weeks,
            "ai_advice": advice,
            "potential_savings": avg_spending * 0.15,  # 15% potential savings
            "recommended_budget": avg_spending * 0.85
        }
    
    async def security_analysis(self, transaction_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze security threats"""
        
        # Mock security data
        mock_security_data = {
            "blocked_ips": 3,
            "suspicious_users": 1,
            "failed_logins": 45,
            "unusual_transactions": 2
        }
        
        analysis_prompt = f"""
        Analyze this security data for threats:
        
        Security metrics: {mock_security_data}
        Transaction data: {transaction_data or 'No specific transaction'}
        
        Provide threat assessment and recommendations.
        """
        
        threat_analysis = await self.chat_response(analysis_prompt, user_role="admin")
        
        return {
            "threat_level": "MODERATE",
            "confidence_score": 0.75,
            "blocked_ips": mock_security_data["blocked_ips"],
            "suspicious_users": mock_security_data["suspicious_users"],
            "ai_analysis": threat_analysis,
            "recommendations": [
                "Increase monitoring on flagged accounts",
                "Review login security policies", 
                "Update fraud detection rules"
            ]
        }

async def demo_user_features():
    """Demo user financial advisory features"""
    print("\n" + "💰" + "="*60)
    print("USER FINANCIAL ADVISORY DEMO")
    print("="*62)
    
    agent = SimpleBankingAgent()
    
    # Test 1: Spending Analysis
    print("\n🎯 Test 1: Weekly Spending Analysis")
    print("-" * 50)
    
    spending_data = {
        "week1": 125.50,
        "week2": 165.30, 
        "week3": 145.80,
        "week4": 180.20
    }
    
    print(f"📊 Spending Data: {spending_data}")
    
    analysis = await agent.analyze_spending(spending_data, "toronto")
    
    print(f"\n📈 ANALYSIS RESULTS:")
    print(f"   💰 Total Spending: ${analysis['total_spending']:.2f}")
    print(f"   📊 Weekly Average: ${analysis['average_weekly']:.2f}")
    print(f"   📈 Trend: {analysis['trend']}")
    print(f"   🎯 Potential Savings: ${analysis['potential_savings']:.2f}")
    print(f"   💡 Recommended Budget: ${analysis['recommended_budget']:.2f}")
    
    print(f"\n🤖 AI ADVICE:")
    print(analysis['ai_advice'][:500] + "..." if len(analysis['ai_advice']) > 500 else analysis['ai_advice'])
    
    # Test 2: Chat Interaction
    print("\n🎯 Test 2: Chat Interaction")
    print("-" * 50)
    
    user_questions = [
        "I spent $180 on groceries this week, is that too much?",
        "What are the best ways to save money on food?",
        "How can I reduce my weekly spending by $30?"
    ]
    
    for question in user_questions:
        print(f"\n👤 USER: {question}")
        response = await agent.chat_response(question, "user", "toronto")
        print(f"🤖 AI: {response[:200]}...")

async def demo_admin_features():
    """Demo admin security analysis features"""
    print("\n" + "🔒" + "="*60)
    print("ADMIN SECURITY ANALYSIS DEMO")
    print("="*62)
    
    agent = SimpleBankingAgent()
    
    # Test 1: Security Analysis
    print("\n🎯 Test 1: Security Threat Analysis")
    print("-" * 50)
    
    suspicious_transaction = {
        "amount": 15000,
        "location": "unknown",
        "timestamp": "3:30 AM",
        "user_id": "user_12345"
    }
    
    print(f"💳 Suspicious Transaction: {suspicious_transaction}")
    
    security_analysis = await agent.security_analysis(suspicious_transaction)
    
    print(f"\n🛡️ SECURITY ANALYSIS:")
    print(f"   🚨 Threat Level: {security_analysis['threat_level']}")
    print(f"   📊 Confidence: {security_analysis['confidence_score']:.0%}")
    print(f"   🚫 Blocked IPs: {security_analysis['blocked_ips']}")
    print(f"   👤 Suspicious Users: {security_analysis['suspicious_users']}")
    
    print(f"\n🤖 AI ANALYSIS:")
    print(security_analysis['ai_analysis'][:500] + "..." if len(security_analysis['ai_analysis']) > 500 else security_analysis['ai_analysis'])
    
    # Test 2: Admin Chat
    print("\n🎯 Test 2: Admin Security Chat")
    print("-" * 50)
    
    admin_questions = [
        "What are the current security threats?",
        "Analyze recent login failures",
        "Should I be concerned about unusual transaction patterns?"
    ]
    
    for question in admin_questions:
        print(f"\n👤 ADMIN: {question}")
        response = await agent.chat_response(question, "admin")
        print(f"🤖 AI: {response[:200]}...")

async def interactive_demo():
    """Interactive demo allowing user input"""
    print("\n" + "💬" + "="*60)
    print("INTERACTIVE CHAT DEMO")
    print("="*62)
    
    agent = SimpleBankingAgent()
    
    print("Welcome! Type your questions or 'quit' to exit.")
    print("Examples:")
    print("• 'How can I save money on groceries?'")
    print("• 'Analyze my spending patterns'") 
    print("• 'What security threats should I watch for?' (admin)")
    
    while True:
        print("\n" + "-"*50)
        user_input = input("👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Determine role based on keywords
        role = "admin" if any(word in user_input.lower() for word in ['security', 'threat', 'admin', 'attack']) else "user"
        
        print(f"🤖 AI ({role} mode): ", end="")
        
        try:
            response = await agent.chat_response(user_input, role)
            print(response)
        except Exception as e:
            print(f"Sorry, I encountered an error: {e}")

async def main():
    """Main demo function"""
    print("🏦" + "="*70)
    print("    AI BANKING AGENT - SIMPLIFIED DEMO")
    print("="*73)
    
    if not LANGCHAIN_AVAILABLE:
        print("⚠️  Running in MOCK mode (LangChain not available)")
        print("💡 For full functionality, install: pip install langchain langchain-ollama")
    
    print("\nThis demo showcases:")
    print("🔒 Admin: Security analysis & threat detection")
    print("💰 User: Financial advisory & spending optimization")
    print("🤖 AI: Intelligent responses using LangChain/Ollama")
    print("="*73)
    
    try:
        await demo_admin_features()
        await demo_user_features()
        
        # Ask if user wants interactive demo
        response = input("\n❓ Would you like to try the interactive chat? (y/n): ")
        if response.lower() in ['y', 'yes']:
            await interactive_demo()
            
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
    
    print("\n✅ Demo completed!")
    print("\nNext steps:")
    print("1. Install full dependencies: pip install -r requirement.txt")
    print("2. Install Ollama: https://ollama.ai/download")
    print("3. Run full system: python setup_and_run.py")

if __name__ == "__main__":
    asyncio.run(main())