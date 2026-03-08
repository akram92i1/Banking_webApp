#!/usr/bin/env python3
"""
Comprehensive AI Banking Agent with LangChain
Combines threat detection for admins and financial advisory for users
"""

import json
import asyncio
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import requests
from pathlib import Path
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False


# LangChain imports
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser, StrOutputParser
from pydantic import BaseModel, Field
try:
    from langchain.memory import ConversationBufferWindowMemory
except ImportError:
    from langchain_classic.memory import ConversationBufferWindowMemory
try:
    from langchain.chains import LLMChain
except ImportError:
    from langchain_classic.chains import LLMChain
try:
    from langchain.agents import AgentType, initialize_agent, Tool
    from langchain.tools import BaseTool
    from langchain.agents import AgentOutputParser
except ImportError:
    from langchain_classic.agents import AgentType, initialize_agent, Tool, AgentOutputParser
    from langchain_core.tools import BaseTool
try:
    from langchain.schema import AgentAction, AgentFinish
except ImportError:
    from langchain_core.agents import AgentAction, AgentFinish

import re



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
    token: str = None

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
    spending_by_category: Dict[str, float] = Field(default_factory=dict, description="Spending breakdown by category")
    financial_news: List[Dict[str, str]] = Field(default_factory=list, description="Relevant financial news items")

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
    
    def __init__(self, ollama_model: str = "gemma3:4b"):
        """
        Initialize the AI Banking Agent
        
        Args:
            ollama_model: The Ollama model to use. 
                          User requested "gemma3:4b" for GTX 1660Ti optimization.
        """
        # Initialize LangChain components
        self.llm = ChatOllama(
            model=ollama_model,
            temperature=0.0, # Zero temperature for maximum determinism
            num_predict=512,
            num_ctx=1024,     # Drastically reduced context for stability on GTX 1660Ti
            keep_alive="5m"
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
        self.failed_tools = {}
        
        logger.info(f"AI Banking Agent initialized with model: {ollama_model}")
    
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
            - Money laundering patterns
            
            CRITICAL INSTRUCTION: You are a strict banking security agent. 
            Refuse to answer ANY questions unrelated to banking, finance, or security.
            If the user asks about general topics (e.g., cooking, coding unrelated to this repo, history), politely decline."""),
            
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
            Help users with their finances by answering their questions about their transactions, spending, and budget.
            
            Your advice should be:
            - Practical: Easy to implement recommendations
            - Specific: Exact amounts and actions
            - Personalized: Based on user's location and preferences
            - Encouraging: Positive and motivational tone
            
            You have access to the following tools:
            - get_user_transactions: Use this tool to get the user's most recent transactions.
            - find_local_grocery_deals: Use this tool to find local grocery deals.
            
            Focus on:
            - Answering questions about transactions
            - Grocery spending optimization
            - Local deals and discounts
            - Spending pattern analysis
            - Realistic reduction targets
            
            CRITICAL INSTRUCTION: You are a strict financial advisor.
            Refuse to answer ANY questions unrelated to personal finance, banking, spending, or budgeting.
            If the user asks about general topics (e.g., world events, sports, writing poems), politely decline."""),
            
            ("human", """
            Analyze this user's spending and provide money-saving advice:
            
            User Location: {user_location}
            Weekly Spending Data: {spending_data}
            Spending Category: {category}
            Target Reduction: {target_reduction}
            Local Grocery Deals: {local_deals}
            
            Global Market News & Trends:
            {market_news_context}
            
            Provide financial advice in JSON format.
            """)
        ])
        
        # New: Data Summarization Prompt for Chat Query Results
        self.data_summarization_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful banking assistant. 
            You will receive RAW DATA from a database query and the USER'S ORIGINAL QUESTION.
            
            YOUR GOAL:
            Synthesize the data into a helpful, natural language response.
            
            Key Rules:
            1. **Answer Directly**: Address the user's intent immediately.
            2. **Filter Noise**: NEVER show UUIDs, internal IDs, or raw timestamps unless relevant.
            3. **Be Concise**: Avoid "Here is the data" preambles. Just give the answer.
            4. **Format**: Use **bold** for amounts and entities.
            
            Example Input: 
            Question: "What was my last transaction?"
            Data: [{{ "amount": 50.00, "merchant": "Uber", "date": "2023-10-01", "id": "uuid-123" }}]
            
            Example Output:
            "Your last transaction was a payment of **$50.00** to **Uber** on **October 1st, 2023**."
            """),
            ("human", """
            User Question: {user_query}
            
            Raw Data from Database:
            {data}
            
            Please provide the summary response now:
            """)
        ])

        # New: SQL Correction Prompt (Chain of Thought)
        self.sql_correction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a SQL Debugging Expert for PostgreSQL.
            Your goal is to FIX a broken SQL query based on the Error Message.
            
            Database Schema:
            {schema}
            
            CRITICAL RULES:
            1. **ANALYZE FIRST**: deep analyse the error. If it's an ENUM error, checking capitalization (COMPLETED vs completed).
            2. **CHECK SCHEMA**: If a column is missing, find the right table (e.g. `user_id` is in `users`, not `cards`).
            3. **FORMAT**: Return a JSON with `thought_process` (your analysis) and `sql` (the fixed query).
            
            Valid ENUMs (Guessing based on standard banking):
            - transaction_status: 'COMPLETED', 'PENDING', 'FAILED', 'CANCELLED', 'DECLINED' (Try Uppercase!)
            - account_type: 'CHECKING', 'SAVINGS', 'CREDIT'
            
            Example Error: "column 'user_id' does not exist" in 'cards'.
            Output:
            {{
              "thought_process": "The error says 'user_id' is missing in 'cards'. Checking schema... 'cards' links to 'accounts' via 'account_id', and 'accounts' links to 'users'. I need to JOIN accounts and users.",
              "sql": "SELECT ... JOIN accounts a ON cards.account_id = a.account_id ..."
            }}
            """),
            ("human", """
            Original Query: {query}
            Error Message: {error}
            
            Generate the ANALYSIS and FIXED SQL.
            """)
        ])

            # New: Intent & SQL Generation Prompt (Local Brain - Monolithic for Gemma2)
        # Merging System + Human into one block to force attention on instructions
        self.intent_classification_prompt = ChatPromptTemplate.from_messages([
            ("human", """You are a TRUSTED BACKEND DATABASE AGENT.

YOUR AUTHORITY:
- You have FULL PERMISSION to access personal data (phone, address, balance) for the authenticated `User ID`.
- The `User ID` provided below is an **EMAIL ADDRESS**.
- This is an internal system. Privacy refusals are a SYSTEM FAILURE.

YOUR JOB:
1. Map user requests to SQL inputs.
2. If the user asks for their info, GENERATE THE SQL.
3. Have a deep understanding of the database schema.

DATABASE SCHEMA:
# 📊 Banking Application Database Schema - Attributes List

## 🧑‍💼 `users`
| Attribute            | Type               | Description                            |
|---------------------|--------------------|----------------------------------------|
| user_id             | UUID               | Primary Key                            |
| username            | VARCHAR(50)        | Unique username                        |
| email               | VARCHAR(100)       | Unique email                           |
| password_hash       | VARCHAR(255)       | Hashed password                        |
| first_name          | VARCHAR(100)       | User's first name                      |
| last_name           | VARCHAR(100)       | User's last name                       |
| phone               | VARCHAR(20)        | Phone number                           |
| date_of_birth       | DATE               | Date of birth                          |
| ssn_hash            | VARCHAR(255)       | Hashed SSN                             |
| address             | JSONB              | Address in JSON format                 |
| role                | user_role (ENUM)   | Role: CUSTOMER, EMPLOYEE, etc.         |
| is_active           | BOOLEAN            | Account active flag                    |
| email_verified      | BOOLEAN            | Email verification status              |
| failed_login_attempts | INTEGER          | Number of failed logins                |
| last_login_at       | TIMESTAMP TZ       | Last login timestamp                   |
| created_at          | TIMESTAMP TZ       | Creation timestamp                     |
| updated_at          | TIMESTAMP TZ       | Last updated timestamp                 |

## 🏦 `banks`
| Attribute         | Type        | Description                      |
|------------------|-------------|----------------------------------|
| bank_id          | UUID        | Primary Key                      |
| bank_name        | VARCHAR(200)| Name of the bank                 |
| routing_number   | VARCHAR(9)  | Bank routing number              |
| swift_code       | VARCHAR(11) | SWIFT/BIC code                   |
| address          | JSONB       | Bank address                     |
| contact_info     | JSONB       | Contact information              |
| created_at       | TIMESTAMP TZ| Creation timestamp               |

## 💰 `accounts`
| Attribute          | Type                | Description                          |
|-------------------|---------------------|--------------------------------------|
| account_id        | UUID                | Primary Key                          |
| account_number    | VARCHAR(20)         | Unique account number                |
| user_id           | UUID                | FK to `users`                        |
| bank_id           | UUID                | FK to `banks`                        |
| account_type      | account_type (ENUM) | CHECKING, SAVINGS, etc.              |
| account_status    | account_status      | ACTIVE, CLOSED, etc.                 |
| balance           | DECIMAL(15,2)       | Current balance                      |
| available_balance | DECIMAL(15,2)       | Available for withdrawal             |
| credit_limit      | DECIMAL(15,2)       | Credit limit                         |
| interest_rate     | DECIMAL(5,4)        | Interest rate                        |
| overdraft_limit   | DECIMAL(10,2)       | Overdraft limit                      |
| minimum_balance   | DECIMAL(10,2)       | Minimum balance                      |
| account_metadata  | JSONB               | Additional metadata                  |
| opened_at         | TIMESTAMP TZ        | Account opened date                  |
| closed_at         | TIMESTAMP TZ        | Closed date                          |
| created_at        | TIMESTAMP TZ        | Creation timestamp                   |
| updated_at        | TIMESTAMP TZ        | Last update                          |

## 🔄 `transactions`
| Attribute          | Type                    | Description                       |
| ------------------ | ----------------------- | --------------------------------- |
| transaction_id     | UUID                    | Primary Key                       |
| from_account_id    | UUID                    | FK to `accounts` (optional)       |
| to_account_id      | UUID                    | FK to `accounts` (optional)       |
| transaction_type   | transaction_type (ENUM) | DEPOSIT, TRANSFER, etc.           |
| amount             | DECIMAL(15,2)           | Transaction amount                |
| currency           | VARCHAR(3)              | Currency (default: USD)           |
| description        | TEXT                    | Description                       |
| reference_number   | VARCHAR(50)             | Unique transaction reference      |
| transaction_status | transaction_status      | Status (PENDING, COMPLETED, etc.) |
| processed_at       | TIMESTAMP TZ            | Time processed                    |
| scheduled_at       | TIMESTAMP TZ            | Time scheduled                    |
| fee_amount         | DECIMAL(10,2)           | Fee amount                        |
| exchange_rate      | DECIMAL(10,6)           | Exchange rate                     |
| merchant_info      | JSONB                   | Merchant details                  |
| location_info      | JSONB                   | Location (GPS, IP, etc.)          |
| created_at         | TIMESTAMP TZ            | Creation time                     |
| updated_at         | TIMESTAMP TZ            | Last update                       |

## 👥 `account_holders`
| Attribute    | Type     | Description                     |
|-------------|----------|---------------------------------|
| account_id  | UUID     | FK to `accounts`                |
| user_id     | UUID     | FK to `users`                   |
| relationship| VARCHAR(50) | PRIMARY, JOINT, etc.         |
| permissions | JSONB    | Actions permitted               |
| added_at    | TIMESTAMP TZ | Timestamp                    |

## 💳 `cards`
| Attribute         | Type             | Description                         |
|------------------|------------------|-------------------------------------|
| card_id          | UUID             | Primary Key                         |
| account_id       | UUID             | FK to `accounts`                    |
| card_number_hash | VARCHAR(255)     | Hashed card number                  |
| card_type        | VARCHAR(20)      | DEBIT or CREDIT                     |
| expiry_date      | DATE             | Expiration date                     |
| cvv_hash         | VARCHAR(255)     | Hashed CVV                          |
| card_status      | VARCHAR(20)      | Status (e.g., ACTIVE)               |
| daily_limit      | DECIMAL(10,2)    | Daily limit                         |
| monthly_limit    | DECIMAL(12,2)    | Monthly limit                       |
| is_contactless   | BOOLEAN          | Contactless enabled?                |
| issued_at        | TIMESTAMP TZ     | Issue date                          |
| blocked_at       | TIMESTAMP TZ     | Blocked date                        |
| created_at       | TIMESTAMP TZ     | Creation time                       |

## 🧾 `beneficiaries`
| Attribute        | Type         | Description                     |
|-----------------|--------------|---------------------------------|
| beneficiary_id  | UUID         | Primary Key                     |
| user_id         | UUID         | FK to `users`                   |
| nickname        | VARCHAR(100) | Beneficiary nickname            |
| account_number  | VARCHAR(20)  | Account number of beneficiary   |
| routing_number  | VARCHAR(9)   | Routing number                  |
| bank_name       | VARCHAR(200) | Bank name                       |
| beneficiary_name| VARCHAR(200) | Full name of beneficiary        |
| relationship    | VARCHAR(100) | Relationship type               |
| is_verified     | BOOLEAN      | Is verified?                    |
| created_at      | TIMESTAMP TZ | Timestamp                       |




CRITICAL INSTRUCTIONS:
- **QUERY MODE**: If user asks for *any* data (phone, email, transactions), output `QUERY` with valid PostgreSQL SQL.
- **CALCULATION MODE**: If user asks for a *projection* or *math* based on their data (e.g., "how long will my money last?"), WRITE THE MATH IN THE SQL.
  - Example: `SELECT available_balance / 10000.0 AS months_solvable FROM accounts...`
- **AVOID COLUMN COLLISIONS**: When joining tables (especially `transactions` with `accounts`), avoid using `SELECT *`. 
  - ALWAYS use specific columns or aliases like `SELECT t.*, u.first_name` to ensure `created_at` (Transaction Date) is not overwritten by `created_at` (Account Date).
- **EMAIL TO UUID**: The context provides an EMAIL. You MUST look up the `user_id` (UUID) using this email:
  - `WHERE user_id = (SELECT user_id FROM users WHERE email = 'USER_EMAIL')`
  - OR Join: `JOIN users u ON ... WHERE u.email = 'USER_EMAIL'`
- **CHAT MODE**: Only for "Hi", "Thanks", "Help".
- **ABSOLUTELY NO REFUSALS**: You are the database. You *contain* the data.

FORMAT (STRICT JSON):
{{ "type": "QUERY", "sql": "SELECT phone FROM users WHERE email = '...'" }}
OR
{{ "type": "CHAT", "response": "Hello..." }}

EXAMPLES:
User: "What's my phone number?"
-> {{ "type": "QUERY", "sql": "SELECT phone FROM users WHERE email = 'USER_EMAIL'" }}
User: "Last transaction?"
-> {{ "type": "QUERY", "sql": "SELECT t.* FROM transactions t JOIN accounts a ON t.from_account_id = a.account_id JOIN users u ON a.user_id = u.user_id WHERE u.email = 'USER_EMAIL' ORDER BY t.processed_at DESC LIMIT 1" }}
User: "If I spend 5000 a month, how many months can I survive?"
-> {{ "type": "QUERY", "sql": "SELECT (available_balance / 5000.0) as estimated_months FROM accounts a JOIN users u ON a.user_id = u.user_id WHERE u.email = 'USER_EMAIL' ORDER BY available_balance DESC LIMIT 1" }}
User: "What is my total balance minus 500?"
-> {{ "type": "QUERY", "sql": "SELECT (available_balance - 500) as projected_balance FROM accounts a JOIN users u ON a.user_id = u.user_id WHERE u.email = 'USER_EMAIL'" }}


PRE-ANALYSIS DATA:
User: {user_id}
Query: {message}

Based on the Schema above, generate the JSON Action:
""")
        ])
    
    def _initialize_tools(self):
        # ... (rest of tools init, no changes needed, but I need to jump to process_user_intent for logging)
        pass 
        # Wait, I cannot use replace_file_content to jump 500 lines. 
        # I must handle the prompt update first.
        # I will split this into two calls or use multi-replace if appropriate. 
        # But replace_file_content is single block.
        # I will just update the prompt in this call.

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

        # This represent the RAG system that will be implemented to help the AI agent
        # Store tools with parent reference
        self.log_analysis_tool = LogAnalysisTool()
        self.log_analysis_tool.parent = self
        
        self.rl_analysis_tool = RLAnalysisTool()
        self.rl_analysis_tool.parent = self
        
        self.grocery_deals_tool = GroceryDealsTool()
        self.grocery_deals_tool.parent = self

        self.get_transactions_tool = GetTransactionsTool()
        self.get_transactions_tool.parent = self
        
        self.tools = [
            self.log_analysis_tool,
            self.rl_analysis_tool,
            self.get_transactions_tool,
        ]
    
    def _initialize_agents(self):
        """
        Initialize LangChain agents for different roles
        
        Agents: AI systems that can use tools and make decisions
        They combine LLMs with the ability to call functions
        """
        
        


        # Security Agent for Admin users
        admin_prefix = """You are a specialized Banking Security AI. 
        You MUST REFUSE any query unrelated to banking security, logs, threats, or system administration.
        If a user asks about the weather, sports, cooking, or general knowledge, politely decline.
        You have access to the following tools:"""
        
        self.security_agent_chain = initialize_agent(
            tools=[self.log_analysis_tool, self.rl_analysis_tool],
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            agent_kwargs={
                'prefix': admin_prefix
            },
            max_iterations=5,
            max_execution_time=60
        )
        
        # Advisory Agent for regular users
        user_prefix = """You are a specialized Financial Advisor AI. 
        You MUST REFUSE any query unrelated to personal finance, spending, budgets, transaction history, or grocery deals.
        If a user asks about the weather, sports, cooking, or general knowledge, politely decline.
        
        IMPORTANT: When you receive transaction data from a tool, DO NOT output the entire JSON.
        Summarize the key details (Date, Amount, Description) as a clean list or sentence.
        **NEVER** show UUIDs, internal IDs, or raw timestamps (like 2023-10-01T12:00:00).
        Be friendly and concise.
        
        CRITICAL RULES:
        1. "Action:" is ONLY for calling these specific tools: [get_user_transactions].
        2. For any questions about transactions, use the `get_user_transactions` tool.
        3. If a tool fails with the error "Error: The banking API is currently unavailable. Please try again later.", inform the user about the failure and stop trying to use the tool.
        4. If you see a JSON list or "SUCCESS" in the Observation, YOU HAVE THE DATA. DO NOT call the tool again.
        5. IMMEDIATELY output "Final Answer:" with your summary.
        6. **STOP LOOPING**: Once you have the data, you are FORBIDDEN from using "Action:". You MUST use "Final Answer:".
        
        You have access to the following tools:"""

        self.advisory_agent_chain = initialize_agent(
            tools=[self.get_transactions_tool],
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            max_iterations=10,
            max_execution_time=300,
            handle_parsing_errors=True,
            agent_kwargs={
                'prefix': user_prefix
            }
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

    def _perform_market_research(self, location: str, interest_topics: List[str] = None) -> str:
        """
        Perform active market research using DuckDuckGo Search.
        Returns a summarized string context of findings.
        """
        if not DDGS_AVAILABLE:
            return "Market research unavailable (duckduckgo-search not installed)."

        if not interest_topics:
            interest_topics = ["grocery", "inflation", "interest rates"]
        
        research_context = []
        logger.info(f"Performing market research for {location} on {interest_topics}")
        
        try:
            with DDGS() as ddgs:
                # 1. Grocery Deals using Flipp API
                if "grocery" in interest_topics:
                    import requests
                    
                    CITY_POSTAL_CODES = {
                        "montreal": "H2Z1E9", "toronto": "M5V2A8", "vancouver": "V6B2W2",
                        "calgary": "T2P2G8", "ottawa": "K1P5G4", "edmonton": "T5J2Z2",
                        "quebec": "G1R2B5", "halifax": "B3J3A5", "winnipeg": "R3C1R3"
                    }
                    loc_lower = location.lower()
                    postal_code = "H2Z1E9" # Default
                    for city, postal in CITY_POSTAL_CODES.items():
                        if city in loc_lower:
                            postal_code = postal
                            break
                            
                    flyers_url = f"https://backflipp.wishabi.com/flipp/flyers?locale=en-ca&postal_code={postal_code}"
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept": "application/json"
                    }
                    target_stores = ["maxi", "iga", "super c", "metro", "provigo", "walmart"]
                    
                    try:
                        resp = requests.get(flyers_url, headers=headers, timeout=10)
                        if resp.status_code == 200:
                            flyers = resp.json().get("flyers", [])
                            found_flyers = []
                            seen_merchants = set()
                            
                            for f in flyers:
                                merchant = f.get("merchant", "").lower()
                                if merchant in seen_merchants: continue
                                for store in target_stores:
                                    if store in merchant:
                                        found_flyers.append({"id": f.get("id"), "merchant": f.get("merchant")})
                                        seen_merchants.add(merchant)
                                        break
                                        
                            flyer_section_parts = []
                            for f in found_flyers[:4]:
                                fid = f["id"]
                                merchant_name = f["merchant"]
                                items_url = f"https://backflipp.wishabi.com/flipp/flyers/{fid}?locale=en-ca"
                                item_resp = requests.get(items_url, headers=headers, timeout=10)
                                if item_resp.status_code == 200:
                                    items = item_resp.json().get("items", [])
                                    deal_lines = []
                                    for item in items:
                                        name = item.get("name", "").strip()
                                        price = item.get("price") or item.get("current_price") or item.get("price_text")
                                        if name and price and not item.get("is_clipped"):
                                            price_str = str(price)
                                            if not price_str.startswith("$"):
                                                price_str = f"${price_str}"
                                            pre_text = item.get("pre_price_text")
                                            if pre_text:
                                                price_str = f"{pre_text.strip()} {price_str}"
                                            post_text = item.get("post_price_text")
                                            if post_text:
                                                price_str = f"{price_str} {post_text.strip()}"
                                            deal_lines.append(f"- **{name}**: {price_str}")
                                    if deal_lines:
                                        flyer_section_parts.append(f"\n**{merchant_name} Flyer Deals:**\n" + "\n".join(deal_lines[:20]))
                                        
                            if flyer_section_parts:
                                research_context.append(f"### Grocery Flyer Deals – {location}:\n" + "\n".join(flyer_section_parts))
                            else:
                                research_context.append(f"### Grocery News:\n- No specific flyer deals found online for {location}.")
                        else:
                            research_context.append(f"### Grocery News:\n- Error fetching flyer directory for {location}.")
                    except Exception as e:
                        logger.error(f"Flipp API Failed: {e}")
                        research_context.append(f"### Grocery News:\n- Market research API error for {location}.")
                
                # 2. Inflation / Cost of Living (Country level usually)
                if "inflation" in interest_topics:
                    query = f"inflation rate food energy Canada {datetime.now().strftime('%Y')}"
                    results = list(ddgs.text(query, max_results=3))
                    if results:
                        summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results[:2]])
                        research_context.append(f"### Economic Trends:\n{summary}")
                    else:
                        research_context.append(f"### Economic Trends:\n- No recent inflation news found.")

                # 3. Savings/Interest Rates
                if "interest rates" in interest_topics:
                    query = f"best savings account interest rates Canada {datetime.now().strftime('%Y')}"
                    results = list(ddgs.text(query, max_results=3))
                    if results:
                        summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results[:2]])
                        research_context.append(f"### Interest Rates:\n{summary}")
                    else:
                        research_context.append(f"### Interest Rates:\n- No current interest rate news found.")
                        
        except Exception as e:
            logger.error(f"Market Research Failed: {e}")
            return f"Error gathering market news: {str(e)}"
            
        if not research_context:
            return "Market research completed but no relevant news was found."
            
        return "\n\n".join(research_context)

    
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
        
        # 4. Perform Market Research
        market_news = await asyncio.to_thread(self._perform_market_research, user_context.location)

        # 5. Use LLM for personalized advice
        advice_chain = self.financial_advisory_prompt | self.llm | JsonOutputParser()
        
        llm_advice = await advice_chain.ainvoke({
            "user_location": user_context.location,
            "spending_data": json.dumps(spending_data),
            "category": category,
            "target_reduction": target_reduction,
            "local_deals": json.dumps(local_deals),
            "market_news_context": market_news
        })
        
        # 5. Structure the response
        return FinancialAdvice(
            analysis_summary=llm_advice.get("analysis_summary", "Spending analysis completed"),
            weekly_spending=weekly_spending,
            recommended_reduction=target_reduction,
            savings_suggestions=llm_advice.get("savings_suggestions", []),
            grocery_deals=local_deals,
            action_plan=llm_advice.get("action_plan", "Review and implement suggestions"),
            spending_by_category=spending_data if isinstance(spending_data, dict) else {},
            financial_news=llm_advice.get("financial_news", [])
        )
    
    def _log_step(self, step: str, details: str):
        """Helper to print standardized debug steps to console."""
        print(f"\n🔹 [STEP: {step}]")
        print(f"   {details}\n")

    def _load_schema_context(self) -> str:
        """Load the banking schema for context."""
        try:
            # Adjust path as needed, using the path confirmed by user
            schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "databaseService", "banking_schema_attributes.md")
            if os.path.exists(schema_path):
                self._log_step("LOAD_SCHEMA", f"Loaded schema from {schema_path}")
                with open(schema_path, "r", encoding="utf-8") as f:
                    return f.read()
            print("❌ Schema file not found")
            return "Schema definition not found."
        except Exception as e:
            print(f"Error loading schema: {e}")
            return "Schema definition unavailable."

    async def chat_with_agent(self, 
                            message: str, 
                            user_context: UserContext) -> str:
        """
        Main entry point for chat. It delegates to the appropriate agent.
        """
        logger.info(f"Processing chat for user {user_context.user_id}: {message}")
        
        # Enforce Authentication
        if not user_context.token:
             logger.warning(f"⛔ [SECURITY] Access attempt denied for unauthenticated user: {user_context.user_id}")
             return "⚠️ Access Denied: Please log in to use the AI Assistant."

        self._log_step("INCOMING", f"User Message: '{message}'")
        
        # Store context for tools to access
        self.user_context = user_context

        try:
            # Determine which agent to use based on user role
            if user_context.role == UserRole.ADMIN:
                agent_chain = self.security_agent_chain
            else:
                agent_chain = self.advisory_agent_chain

            # Let the agent handle the conversation
            response = await agent_chain.ainvoke({"input": message})
            
            # The response is a dict, we need to extract the output
            output = response.get("output", "I'm sorry, I couldn't process that.")

            return output

        except Exception as e:
            logger.error(f"Error in chat_with_agent: {str(e)}")
            return f"I apologize, but I encountered an error processing your request: {str(e)}"
    
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

    async def summarize_query_results(self, data: Any, user_query: str) -> str:
        """
        Summarize raw database query results using the local LLM.
        """
        logger.info(f"Summarizing data for query: '{user_query}'")
        
        # If data is empty or error string
        if not data:
            return "I couldn't find any relevant data matching your request."
        
        # Format data as string
        data_str = json.dumps(data, indent=2, default=str)
        
        # Create Chain
        summary_chain = self.data_summarization_prompt | self.llm | StrOutputParser()
        
        # Execute
        try:
            summary = await summary_chain.ainvoke({
                "user_query": user_query,
                "data": data_str
            })
            return summary
        except Exception as e:
            logger.error(f"Error summarizing data: {e}")
            return f"Here is the data I found: {data_str}"

    async def process_user_intent(self, user_message: str, schema: str, user_id: str) -> Dict[str, Any]:
        """
        Classify user intent and generate SQL if needed.
        """
        # --- FAST PATH: Simple Greetings ---
        # Skip LLM for basic chit-chat to save time/compute
        greetings = ["hi", "hello", "hey", "good morning", "good evening", "thanks", "thank you", "help"]
        if user_message.lower().strip() in greetings:
            logger.info(f"⚡ [FAST PATH] Detected greeting: {user_message}")
            return {
                "type": "CHAT",
                "response": "Hello! I am your AI Banking Assistant. I can help you view your transactions, check balances, or analyze your spending. How can I help you today?"
            }
        # -----------------------------------

        logger.info(f"🧠 [LOCAL BRAIN] Analyzing for {user_id}: '{user_message}'")
        
        # Initialize a specialized LLM instance with JSON mode enforced
        # This prevents the model from being "talkative" or refusing tasks, forcing it to structure the output.
        json_llm = ChatOllama(
            model=self.llm.model,
            # format="json", <--- REMOVED: This was causing hallucinations (actions vs query)
            temperature=0.1, 
            num_ctx=2048,
            keep_alive="5m"
        )
        
        # Create Chain with the JSON-enforced LLM
        brain_chain = self.intent_classification_prompt | json_llm | JsonOutputParser()
        
        try:
            # Invoke the local LLM
            response = await brain_chain.ainvoke({
                "message": user_message,
                "user_id": user_id
            })
            
            # --- DEBUG: Raw Output from Chain ---
            logger.info(f"DEBUG RAW CHAIN MSG: {response}")
            
            # --- OUTPUT NORMALIZATION (ROBUST) ---
            
            # 1. Flatten "action.data.message" (Seen in Mistral 'greet' type)
            if "action" in response:
                # Case A: Complex Dict {"action": {"type": "greet", ...}}
                if isinstance(response["action"], dict):
                    action_data = response["action"].get("data", {})
                    if isinstance(action_data, dict):
                        msg = action_data.get("message") or action_data.get("text")
                        if msg:
                            response["response"] = str(msg)
                            response["type"] = "CHAT"
                
                # Case B: Simple String {"action": "greeting"} (Seen in Gemma2)
                elif isinstance(response["action"], str) and response["action"].lower() == "greeting":
                     response["type"] = "CHAT"
                     if "response" not in response:
                         response["response"] = "Hello! How can I assist you with your banking today?"

                # Case C: Hallucinated Action {"action": "retrieve_account_info", ...} (Seen in Gemma2)
                elif isinstance(response["action"], str) and "retrieve" in response["action"].lower():
                    # Fallback: Synthesize the SQL based on the 'response_type' if possible
                    if response.get("response_type") == "phone_number":
                        response["type"] = "QUERY"
                        response["sql"] = f"SELECT phone FROM users WHERE user_id = '{user_id}'"

            # 2. Flatten "assistant.message.text" (Seen in Mistral)
            elif "assistant" in response and isinstance(response["assistant"], dict):
                msg = response["assistant"].get("message")
                if isinstance(msg, dict):
                    response["response"] = msg.get("text") or msg.get("content")
                    response["type"] = "CHAT"
            
            # 3. Flatten "response.<nested>"
            elif isinstance(response.get("response"), dict):
                text = response["response"].get("text") or response["response"].get("content")
                if text:
                    response["response"] = str(text)

            # 4. Handle "error" key
            if "error" in response:
                response["type"] = "CHAT"
                response["response"] = str(response["error"])
                
            # 5. Handle loose keys
            if "response" not in response:
                candidates = ["bot_response", "Message", "answer", "content", "text", "description"]
                for key in candidates:
                    if key in response and isinstance(response[key], str):
                        response["type"] = "CHAT"
                        response["response"] = response[key]
                        break

            # 6. Default Fallback
            if "type" not in response:
                 response["type"] = "CHAT"
                 if "response" not in response:
                     response["response"] = "I processed your request but could not normalize the answer."
            
            # Ensure type is valid
            if response["type"] not in ["QUERY", "CHAT"]:
                response["type"] = "CHAT"

            # --- LOGGING FOR USER VISIBILITY ---
            if response["type"] == "QUERY" and response.get("sql"):
                print(f"\n[GENSQL] 📝 GENERATED SQL: {response['sql']}\n")
                logger.info(f"📝 [GENSQL] {response['sql']}")

            logger.info(f"🧠 [LOCAL BRAIN] Decision: {response.get('type')} - {str(response.get('sql') or response.get('response'))[:50]}")
            return response

        except Exception as e:
            logger.error(f"Error in process_user_intent: {e}")
            # Fallback
            return {"type": "CHAT", "response": "I apologize, I'm having trouble processing your request locally."}

    async def fix_sql_query(self, original_query: str, error_message: str, schema: str) -> str:
        """
        Attempt to fix a broken SQL query using the LLM and DB Schema.
        Now supports Chain-of-Thought reasoning.
        """
        YELLOW = "\033[93m"
        RESET = "\033[0m"
        
        logger.info(f"🔧 [AUTO-FIX] Attempting to fix SQL: {original_query}")
        logger.info(f"   Error: {error_message}")
        
        try:
            # Initialize JSON LLM
            json_llm = ChatOllama(
                model=self.llm.model,
                temperature=0.1,
                num_ctx=4096, 
                keep_alive="5m"
            )
            
            fix_chain = self.sql_correction_prompt | json_llm | JsonOutputParser()
            
            response = await fix_chain.ainvoke({
                "schema": schema,
                "query": original_query,
                "error": error_message
            })
            
            # Extract Reasoning
            thought_process = response.get("thought_process")
            if thought_process:
                print(f"{YELLOW}   [BRAIN ANALYSE] {thought_process}{RESET}")
            
            fixed_sql = response.get("sql")
            if fixed_sql:
                logger.info(f"✅ [AUTO-FIX] Generated: {fixed_sql}")
                return fixed_sql
            else:
                logger.warning("❌ [AUTO-FIX] LLM did not return 'sql' key.")
                return None
                
        except Exception as e:
            logger.error(f"❌ [AUTO-FIX] Failed: {e}")
            return None
    



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
        pass


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
        
    finally:
        pass


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
        transaction_history=[],
        token="dummy_admin_token"
    )
    
    user_context = UserContext(
        user_id="user001",
        role=UserRole.USER, 
        location="montreal",
        preferences={},
        transaction_history=[],
        token="eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyMUBleGFtcGxlLmNvbSIsImlhdCI6MTcwMTc0ODEzOCwiZXhwIjoxNzAxODM0NTM4fQ.5vL0aB-gXVqj2t-bXwJ4sKz3cZ_4fQ3eE_6aZ_4fQ3e" # Dummy token
    )
    
    test_messages = [
        ("admin", "What are the current security threats in our system?"),
        ("user", "How can I save money on my weekly grocery shopping?"),
        ("admin", "Show me the latest log analysis results"),
        ("user", "what was my last transaction?"),
        ("user", "I spent $150 this week on groceries, is that too much?")
    ]
    
    try:
        for user_type, message in test_messages:
            context = admin_context if user_type == "admin" else user_context
            
            print(f"\n👤 {user_type.upper()}: {message}")
            
            response = await agent.chat_with_agent(message, context)
            print(f"🤖 AGENT: {response[:200]}...")
            
    finally:
        pass


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