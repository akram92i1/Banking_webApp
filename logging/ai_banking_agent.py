#!/usr/bin/env python3
"""
Comprehensive AI Banking Agent with LangChain
Combines threat detection for admins and financial advisory for users
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import requests
from pathlib import Path

# LangChain imports
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from pydantic import BaseModel, Field
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.tools import BaseTool

# Import existing modules
from testRFL import ThreatDetectionSystem
from threatDetection import BankingSecurityAgent, LogProcessor, SecurityEvent, ThreatLevel, AttackType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIBankingAgent")

class AgentMode(Enum):
    ADMIN_SECURITY = "admin_security"
    USER_ADVISORY = "user_advisory"

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

@dataclass
class UserContext:
    user_id: str
    role: UserRole
    location: str
    preferences: Dict[str, Any]
    transaction_history: List[Dict[str, Any]]

# Pydantic models for structured outputs
class ThreatAnalysisResult(BaseModel):
    threat_detected: bool = Field(description="Whether a threat was detected")
    threat_type: str = Field(description="Type of threat detected")
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    severity: str = Field(description="Threat severity: LOW, MEDIUM, HIGH, CRITICAL")
    recommendation: str = Field(description="Recommended action")
    explanation: str = Field(description="Detailed explanation of the threat")

class FinancialAdvice(BaseModel):
    analysis_summary: str = Field(description="Summary of spending analysis")
    weekly_spending: float = Field(description="Current weekly spending amount")
    recommended_reduction: float = Field(description="Recommended spending reduction")
    savings_suggestions: List[str] = Field(description="List of specific savings suggestions")
    grocery_deals: List[Dict[str, str]] = Field(description="List of grocery deals found")
    action_plan: str = Field(description="Step-by-step action plan")

class AIBankingAgent:
    """
    Main AI Banking Agent that provides both security analysis and financial advisory
    
    Key LangChain Concepts Used:
    - ChatOllama: Local LLM integration for private banking data
    - PromptTemplate: Structured prompts for consistent AI responses  
    - Memory: Conversation history for context-aware interactions
    - Agents & Tools: Modular functions the AI can call
    - Output Parsers: Structured data extraction from AI responses
    """
    
    def __init__(self, ollama_model: str = "tinyllama"):
        """
        Initialize the AI Banking Agent
        
        Args:
            ollama_model: The Ollama model to use (e.g., "llama3.2", "mistral")
        """
        # Initialize LangChain components
        self.llm = ChatOllama(
            model=ollama_model,
            temperature=0.3,
            top_p=0.9,
            num_predict=256,  # Reduced to 256 for faster responses
            num_ctx=1024,     # Reduced context window for speed
            num_thread=4,     # Use multiple threads
            num_gpu=1,        # Enable GPU offloading if available
            keep_alive="5m",  # Keep model loaded for 5 minutes
            request_timeout=300.0  # Increased to 5 mins so backend outlives frontend timeout
        )
        
        # Memory for conversation context - keeps last 10 exchanges
        self.memory = ConversationBufferWindowMemory(
            k=10,
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize existing security components
        self.security_agent = BankingSecurityAgent()
        self.rl_detector = ThreatDetectionSystem()
        self.log_processor = LogProcessor(self.security_agent)
        
        # Initialize prompts and chains
        self._initialize_prompts()
        self._initialize_tools()
        self._initialize_agents()
        
        # Mock data for demonstration
        self.grocery_stores = self._load_grocery_store_data()
        
        logger.info("AI Banking Agent initialized successfully")
    
    def _initialize_prompts(self):
        """
        Initialize LangChain prompts for different agent functions
        
        PromptTemplate: Creates reusable prompt structures with variables
        ChatPromptTemplate: For multi-message conversations
        """
        
        # Admin Security Analysis Prompt
        self.security_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a cybersecurity expert specializing in banking security.
            Analyze the provided log data and security events to identify threats and provide actionable insights.
            
            Your analysis should be:
            - Comprehensive: Cover all potential security implications
            - Actionable: Provide specific recommendations
            - Risk-focused: Prioritize threats by severity
            - Technical: Use cybersecurity terminology appropriately
            
            Consider these threat types:
            - SQL Injection, XSS, CSRF attacks
            - Account takeover attempts
            - Fraudulent transactions
            - API abuse and DDoS
            - Insider threats
            - Money laundering patterns"""),
            
            ("human", """
            Analyze the following security data:
            
            Log Analysis Results: {log_analysis}
            Reinforcement Learning Results: {rl_analysis}
            Recent Security Events: {recent_events}
            System Metrics: {system_metrics}
            
            Provide a comprehensive threat analysis in JSON format.
            """)
        ])
        
        # User Financial Advisory Prompt
        self.financial_advisory_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a personal financial advisor specializing in spending optimization.
            Help users reduce their expenses by analyzing spending patterns and finding deals.
            
            Your advice should be:
            - Practical: Easy to implement recommendations
            - Specific: Exact amounts and actions
            - Personalized: Based on user's location and preferences
            - Encouraging: Positive and motivational tone
            
            Focus on:
            - Grocery spending optimization
            - Local deals and discounts
            - Spending pattern analysis
            - Realistic reduction targets"""),
            
            ("human", """
            Analyze this user's spending and provide money-saving advice:
            
            User Location: {user_location}
            Weekly Spending Data: {spending_data}
            Spending Category: {category}
            Target Reduction: {target_reduction}
            Local Grocery Deals: {local_deals}
            
            Provide financial advice in JSON format.
            """)
        ])
    
    def _initialize_tools(self):
        """
        Initialize LangChain tools that the agent can use
        
        Tools: Functions that the AI can call to perform specific tasks
        Each tool has a name, description, and function
        """
        
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
            description: str = "Find local grocery deals and discounts"
            parent: Any = Field(default=None, exclude=True)
            
            def _run(self, location: str) -> str:
                """Find grocery deals in user's area"""
                deals = self.parent._get_grocery_deals(location)
                return json.dumps(deals, indent=2)
        
        # Store tools with parent reference
        self.log_analysis_tool = LogAnalysisTool()
        self.log_analysis_tool.parent = self
        
        self.rl_analysis_tool = RLAnalysisTool()
        self.rl_analysis_tool.parent = self
        
        self.grocery_deals_tool = GroceryDealsTool()
        self.grocery_deals_tool.parent = self
        
        self.tools = [
            self.log_analysis_tool,
            self.rl_analysis_tool,
            self.grocery_deals_tool
        ]
    
    def _initialize_agents(self):
        """
        Initialize LangChain agents for different roles
        
        Agents: AI systems that can use tools and make decisions
        They combine LLMs with the ability to call functions
        """
        
        # Security Agent for Admin users
        self.security_agent_chain = initialize_agent(
            tools=[self.log_analysis_tool, self.rl_analysis_tool],
            llm=self.llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            max_iterations=3
        )
        
        # Advisory Agent for regular users
        self.advisory_agent_chain = initialize_agent(
            tools=[self.grocery_deals_tool],
            llm=self.llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            max_iterations=3
        )
    
    def _load_grocery_store_data(self) -> Dict[str, List[Dict]]:
        """Load mock grocery store data for different locations"""
        return {
            "toronto": [
                {"store": "Metro", "item": "Bananas", "price": "$1.99/lb", "discount": "20% off"},
                {"store": "Loblaws", "item": "Ground Beef", "price": "$8.99/lb", "discount": "Buy 2 get 1 free"},
                {"store": "No Frills", "item": "Bread", "price": "$2.49", "discount": "50¢ off"},
            ],
            "montreal": [
                {"store": "IGA", "item": "Chicken Breast", "price": "$12.99/kg", "discount": "30% off"},
                {"store": "Maxi", "item": "Apples", "price": "$3.99/bag", "discount": "$1 off"},
            ],
            "vancouver": [
                {"store": "Save-On-Foods", "item": "Salmon", "price": "$16.99/lb", "discount": "25% off"},
                {"store": "T&T", "item": "Rice", "price": "$8.99/bag", "discount": "Buy 1 get 1 half price"},
            ]
        }
    
    def _get_grocery_deals(self, location: str) -> List[Dict]:
        """Get grocery deals for a specific location"""
        location_key = location.lower()
        return self.grocery_stores.get(location_key, [])
    
    async def analyze_security_threats(self, 
                                     log_file_path: str = None,
                                     transaction_data: Dict = None,
                                     user_context: UserContext = None) -> ThreatAnalysisResult:
        """
        Analyze security threats for admin users
        Combines log analysis, RL analysis, and LLM reasoning
        """
        
        if user_context.role != UserRole.ADMIN:
            raise ValueError("Security analysis only available for admin users")
        
        logger.info("Starting comprehensive security threat analysis...")
        
        # 1. Analyze logs if provided
        log_analysis = {}
        if log_file_path:
            await self.log_processor.process_logs_from_file(log_file_path)
            log_analysis = self.security_agent.get_security_dashboard()
        
        # 2. Run RL analysis if transaction data provided
        rl_analysis = {}
        if transaction_data:
            rl_analysis = self.rl_detector.predict_threat(transaction_data)
        
        # 3. Get recent security events
        recent_events = list(self.security_agent.recent_events)[-10:]  # Last 10 events
        
        # 4. Prepare system metrics
        system_metrics = {
            "blocked_ips_count": len(self.security_agent.blocked_ips),
            "suspicious_users_count": len(self.security_agent.suspicious_users),
            "total_events": len(self.security_agent.recent_events)
        }
        
        # 5. Use LLM for comprehensive analysis
        analysis_chain = self.security_analysis_prompt | self.llm | JsonOutputParser()
        
        llm_analysis = await analysis_chain.ainvoke({
            "log_analysis": json.dumps(log_analysis),
            "rl_analysis": json.dumps(rl_analysis),
            "recent_events": json.dumps([{
                "type": event.attack_type.value,
                "level": event.threat_level.value,
                "confidence": event.confidence_score,
                "description": event.description
            } for event in recent_events]),
            "system_metrics": json.dumps(system_metrics)
        })
        
        # 6. Structure the response
        return ThreatAnalysisResult(
            threat_detected=llm_analysis.get("threat_detected", False),
            threat_type=llm_analysis.get("threat_type", "unknown"),
            confidence_score=llm_analysis.get("confidence_score", 0.0),
            severity=llm_analysis.get("severity", "LOW"),
            recommendation=llm_analysis.get("recommendation", "Continue monitoring"),
            explanation=llm_analysis.get("explanation", "No specific threats identified")
        )
    
    async def provide_financial_advice(self,
                                     user_context: UserContext,
                                     spending_data: Dict[str, float],
                                     category: str = "grocery",
                                     target_reduction: float = None) -> FinancialAdvice:
        """
        Provide financial advice for regular users
        Analyzes spending patterns and suggests savings opportunities
        """
        
        logger.info(f"Providing financial advice for user {user_context.user_id}")
        
        # 1. Calculate current weekly spending
        weekly_spending = sum(spending_data.values()) / len(spending_data) if spending_data else 0
        
        # 2. Set default target reduction if not provided
        if target_reduction is None:
            target_reduction = weekly_spending * 0.15  # 15% reduction by default
        
        # 3. Get local grocery deals
        local_deals = self._get_grocery_deals(user_context.location)
        
        # 4. Use LLM for personalized advice
        advice_chain = self.financial_advisory_prompt | self.llm | JsonOutputParser()
        
        llm_advice = await advice_chain.ainvoke({
            "user_location": user_context.location,
            "spending_data": json.dumps(spending_data),
            "category": category,
            "target_reduction": target_reduction,
            "local_deals": json.dumps(local_deals)
        })
        
        # 5. Structure the response
        return FinancialAdvice(
            analysis_summary=llm_advice.get("analysis_summary", "Spending analysis completed"),
            weekly_spending=weekly_spending,
            recommended_reduction=target_reduction,
            savings_suggestions=llm_advice.get("savings_suggestions", []),
            grocery_deals=local_deals,
            action_plan=llm_advice.get("action_plan", "Review and implement suggestions")
        )
    
    async def chat_with_agent(self, 
                            message: str, 
                            user_context: UserContext) -> str:
        """
        General chat interface that routes to appropriate agent based on user role
        
        This demonstrates LangChain's agent capabilities:
        - Automatic tool selection based on user input
        - Context-aware responses using memory
        - Role-based agent routing
        """
        
        # Determine which agent to use based on user role and message content
        print(f"\n📨 [DEBUG] Received message from {user_context.role.value}: '{message}'")
        start_time = datetime.now()

        if user_context.role == UserRole.ADMIN and any(keyword in message.lower() 
                                                      for keyword in ["security", "threat", "attack", "log"]):
            print("🛡️ [DEBUG] Routing to Security Agent...")
            # Use security agent for admin security queries
            response = await self.security_agent_chain.arun(
                input=message,
                user_role=user_context.role.value
            )
        elif any(keyword in message.lower() 
                for keyword in ["money", "spending", "save", "grocery", "budget"]):
            print("💰 [DEBUG] Routing to Advisory Agent...")
            # Use advisory agent for financial queries
            response = await self.advisory_agent_chain.arun(
                input=message,
                user_location=user_context.location
            )
        else:
            print("🤖 [DEBUG] Routing to General Chat Agent...")
            # General purpose response
            general_prompt = f"""
            You are a helpful banking assistant. The user is a {user_context.role.value}.
            Respond appropriately to their query: {message}
            """
            response = await self.llm.ainvoke(general_prompt)
            response = response.content if hasattr(response, 'content') else str(response)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"✅ [DEBUG] Agent responded in {duration:.2f} seconds")
        print(f"📤 [DEBUG] Response snippet: {response[:100]}...")
        
        return response
    
    async def generate_admin_report(self, user_context: UserContext) -> Dict[str, Any]:
        """Generate comprehensive admin security report"""
        
        if user_context.role != UserRole.ADMIN:
            raise ValueError("Admin reports only available for admin users")
        
        # Get security dashboard
        dashboard = self.security_agent.get_security_dashboard()
        
        # Generate AI insights using LLM
        insights_prompt = f"""
        Based on this security data: {json.dumps(dashboard)}
        
        Provide executive summary insights including:
        1. Overall security posture
        2. Key risks and trends
        3. Recommended actions
        4. Resource allocation suggestions
        """
        
        ai_insights = await self.llm.ainvoke(insights_prompt)
        
        return {
            "dashboard": dashboard,
            "ai_insights": ai_insights.content if hasattr(ai_insights, 'content') else str(ai_insights),
            "generated_at": datetime.now().isoformat(),
            "report_type": "security_summary"
        }
    
    def close(self):
        """Clean up resources"""
        if hasattr(self.security_agent, 'db_connection'):
            self.security_agent.db_connection.close()
        logger.info("AI Banking Agent closed successfully")


# Example usage and testing functions
async def demo_admin_security_analysis():
    """Demonstrate admin security analysis features"""
    print("\n" + "="*60)
    print("🔒 ADMIN SECURITY ANALYSIS DEMO")
    print("="*60)
    
    # Initialize agent
    agent = AIBankingAgent()
    
    # Create admin user context
    admin_context = UserContext(
        user_id="admin001",
        role=UserRole.ADMIN,
        location="toronto",
        preferences={"notifications": True},
        transaction_history=[]
    )
    
    # Mock transaction data for RL analysis
    transaction_data = {
        "amount": 15000,
        "timestamp": datetime.now().isoformat(),
        "merchant_type": "unknown",
        "location": "foreign",
        "user_id": "suspicious_user_123"
    }
    
    try:
        # Run comprehensive threat analysis
        threat_analysis = await agent.analyze_security_threats(
            transaction_data=transaction_data,
            user_context=admin_context
        )
        
        print(f"🎯 Threat Detection Results:")
        print(f"   Threat Detected: {threat_analysis.threat_detected}")
        print(f"   Threat Type: {threat_analysis.threat_type}")
        print(f"   Confidence Score: {threat_analysis.confidence_score:.2f}")
        print(f"   Severity: {threat_analysis.severity}")
        print(f"   Recommendation: {threat_analysis.recommendation}")
        print(f"   Explanation: {threat_analysis.explanation}")
        
        # Generate admin report
        admin_report = await agent.generate_admin_report(admin_context)
        print(f"\n📊 Admin Report Generated:")
        print(f"   Report Type: {admin_report['report_type']}")
        print(f"   Generated At: {admin_report['generated_at']}")
        print(f"   AI Insights: {admin_report['ai_insights'][:200]}...")
        
    except Exception as e:
        print(f"❌ Error in security analysis: {e}")
    finally:
        agent.close()


async def demo_user_financial_advisory():
    """Demonstrate user financial advisory features"""
    print("\n" + "="*60)
    print("💰 USER FINANCIAL ADVISORY DEMO")
    print("="*60)
    
    # Initialize agent
    agent = AIBankingAgent()
    
    # Create user context
    user_context = UserContext(
        user_id="user001",
        role=UserRole.USER,
        location="toronto",
        preferences={"budget_alerts": True},
        transaction_history=[]
    )
    
    # Mock spending data (weekly spending by category)
    spending_data = {
        "week1": 120.50,
        "week2": 145.30,
        "week3": 135.80,
        "week4": 160.20
    }
    
    try:
        # Get financial advice
        advice = await agent.provide_financial_advice(
            user_context=user_context,
            spending_data=spending_data,
            category="grocery",
            target_reduction=30.00  # Reduce by $30/week
        )
        
        print(f"📈 Financial Analysis:")
        print(f"   Current Weekly Spending: ${advice.weekly_spending:.2f}")
        print(f"   Recommended Reduction: ${advice.recommended_reduction:.2f}")
        print(f"   Analysis Summary: {advice.analysis_summary}")
        
        print(f"\n💡 Savings Suggestions:")
        for i, suggestion in enumerate(advice.savings_suggestions, 1):
            print(f"   {i}. {suggestion}")
        
        print(f"\n🛒 Local Grocery Deals:")
        for deal in advice.grocery_deals:
            print(f"   {deal['store']}: {deal['item']} - {deal['price']} ({deal['discount']})")
        
        print(f"\n📋 Action Plan:")
        print(f"   {advice.action_plan}")
        
    except Exception as e:
        print(f"❌ Error in financial advisory: {e}")
    finally:
        agent.close()


async def demo_chat_interface():
    """Demonstrate chat interface for both admin and user"""
    print("\n" + "="*60)
    print("💬 CHAT INTERFACE DEMO")
    print("="*60)
    
    agent = AIBankingAgent()
    
    # Test with admin user
    admin_context = UserContext(
        user_id="admin001", 
        role=UserRole.ADMIN,
        location="toronto",
        preferences={},
        transaction_history=[]
    )
    
    user_context = UserContext(
        user_id="user001",
        role=UserRole.USER, 
        location="montreal",
        preferences={},
        transaction_history=[]
    )
    
    test_messages = [
        ("admin", "What are the current security threats in our system?"),
        ("user", "How can I save money on my weekly grocery shopping?"),
        ("admin", "Show me the latest log analysis results"),
        ("user", "I spent $150 this week on groceries, is that too much?")
    ]
    
    try:
        for user_type, message in test_messages:
            context = admin_context if user_type == "admin" else user_context
            
            print(f"\n👤 {user_type.upper()}: {message}")
            
            response = await agent.chat_with_agent(message, context)
            print(f"🤖 AGENT: {response[:200]}...")
            
    except Exception as e:
        print(f"❌ Error in chat demo: {e}")
    finally:
        agent.close()


# Main demonstration function
async def main():
    """Run all demonstrations"""
    print("🏦 AI Banking Agent with LangChain - Comprehensive Demo")
    print("This agent provides both security analysis and financial advisory services")
    
    await demo_admin_security_analysis()
    await demo_user_financial_advisory()
    await demo_chat_interface()
    
    print("\n✅ Demo completed successfully!")
    print("\nKey LangChain concepts demonstrated:")
    print("• ChatOllama for local LLM integration")
    print("• PromptTemplate for structured AI interactions")
    print("• Memory for conversation context")
    print("• Tools for function calling")
    print("• Agents for intelligent decision making")
    print("• Output Parsers for structured data")


if __name__ == "__main__":
    asyncio.run(main())