import os
import re
import json
import asyncio
import logging
import requests
import asyncpg
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

# Check if we need to add the current directory to sys.path for RAG imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from Data.RAG_system_knowledge_based import setup_rag_system, query_rag, summarize_results
    from Data.RAG_system_Grocery_knowledge_bases import setup_grocery_rag_system, query_grocery_rag
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"Error importing RAG system: {e}")
    RAG_AVAILABLE = False

try:
    import mock_banking_service
    MOCK_AVAILABLE = True
except ImportError as e:
    print(f"Error importing Mock Banking system: {e}")
    MOCK_AVAILABLE = False

from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# --- CONFIGURATION ---
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "databaseService", "banking_schema_attributes.md")

# Database Configuration
DATABASE_URL = "postgresql://ai_agent_readonly:readonly_agent_secure_2024@localhost:5432/my_finance_db"

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FastAPIServer")

# ANSI Colors (module-level so all functions can use them)
BLUE = "\033[94m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# --- DATA MODELS ---
class ChatRequest(BaseModel):
    user_id: str
    message: str
    token: Optional[str] = None

class FinancialAdviceRequest(BaseModel):
    user_id: str
    spending_data: Optional[Dict[str, float]] = None
    category: str = "grocery"
    target_reduction: Optional[float] = None
    token: Optional[str] = None

class SecurityAnalysisRequest(BaseModel):
    user_id: str = "admin"
    location: str = "toronto"
    log_file_path: Optional[str] = None
    transaction_data: Optional[Dict[str, Any]] = None
    security_context: Optional[Dict[str, Any]] = None
    token: Optional[str] = None

class SpendingAnalysisRequest(BaseModel):
    email: str
    transactions: List[Dict[str, Any]] = []
    time_period: str = "weekly"

# --- APP LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB
    print(f"{BLUE}--- STARTING FASTAPI SERVER ---{RESET}")
    print(f"{BLUE}Connecting to Database at {DATABASE_URL[:20]}...{RESET}")
    try:
        app.state.pool = await asyncpg.create_pool(DATABASE_URL)
        print(f"{GREEN}[SUCCESS] Database Connected Successfully!{RESET}")
        
        if MOCK_AVAILABLE:
            await mock_banking_service.init_simulator_tables()
            
    except Exception as e:
        print(f"{RED}[ERROR] Database Connection Failed: {e}{RESET}")
        app.state.pool = None

    # Startup: Initialize RAG System
    print(f"{BLUE}Initializing RAG System...{RESET}")
    if RAG_AVAILABLE:
        # Run synchronous RAG setup in a separate thread
        app.state.rag_chain = await asyncio.to_thread(setup_rag_system)
        app.state.grocery_rag_chain = await asyncio.to_thread(lambda: setup_grocery_rag_system(force_recreate_db=False))
        if app.state.rag_chain:
             print(f"{GREEN}[SUCCESS] RAG System Initialized!{RESET}")
        else:
             print(f"{RED}[ERROR] RAG System Initialization Failed.{RESET}")
        if app.state.grocery_rag_chain:
             print(f"{GREEN}[SUCCESS] Grocery RAG System Initialized!{RESET}")
        else:
             print(f"{RED}[ERROR] Grocery RAG System Initialization Failed.{RESET}")
    else:
        print(f"{RED}[WARNING] RAG System not available (Import Error).{RESET}")
        app.state.rag_chain = None
        app.state.grocery_rag_chain = None

    yield

    # Shutdown: Close DB
    print(f"{BLUE}--- SHUTTING DOWN ---{RESET}")
    if app.state.pool:
        await app.state.pool.close()
        print(f"{BLUE}Database Connection Closed.{RESET}")

# --- APP SETUP ---
app = FastAPI(title="Banking AI Microservice", lifespan=lifespan)

# Add Mock Banking Router
if MOCK_AVAILABLE:
    app.include_router(mock_banking_service.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL STATE ---

# Define structures locally to avoid strong dependency on ai_banking_agent (which imports pandas)
from dataclasses import dataclass
from enum import Enum

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
    token: Optional[str] = None

# Try to import only AIBankingAgent, not the others we just defined
try:
    from ai_banking_agent import AIBankingAgent
    internal_agent = AIBankingAgent()
except Exception as e:
    # Catch any error during import (ImportError, ValueError from numpy, etc)
    logger.error(f"Could not import AIBankingAgent: {e}")
    internal_agent = None

# --- HELPER FUNCTIONS ---

def load_schema() -> str:
    """Load the banking schema markdown"""
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "Schema not found."

def extract_user_from_token(token: str) -> str:
    """
    Extracts the user ID (subject) from a JWT token without verifying signature.
    Useful for logging and context before passing to secured backend.
    """
    try:
        # JWT is header.payload.signature
        parts = token.split(".")
        if len(parts) < 2:
            return "unknown_user"

        payload_b64 = parts[1]
        # Fix Base64 padding
        padding = '=' * (4 - len(payload_b64) % 4)
        payload_b64 += padding

        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload_data = json.loads(payload_bytes)

        # Standard claims: 'sub' is usually user ID. 'preferred_username' is also common.
        return payload_data.get("sub") or payload_data.get("username") or "unknown_user"
    except Exception as e:
        logger.error(f"Error extracting user from token: {e}")
        return "unknown_user"


def extract_token_from_header(request_token: Optional[str], authorization: Optional[str]) -> Optional[str]:
    """Extract token from either request body or Authorization header."""
    token = request_token
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = authorization
    return token


def scrub_sensitive_data(text: str) -> str:
    """Remove any hash-like patterns from LLM responses as a final safety net.
    Catches hex strings (32+ chars) that look like password/SSN hashes."""
    # Match hex strings that are 32+ characters (MD5, SHA-256, bcrypt, etc.)
    scrubbed = re.sub(r'\b[a-fA-F0-9]{32,}\b', '[REDACTED]', text)
    # Match bcrypt-style hashes ($2a$, $2b$, etc.)
    scrubbed = re.sub(r'\$2[aby]?\$\d+\$[./A-Za-z0-9]{53}', '[REDACTED]', scrubbed)
    return scrubbed


async def get_user_email(user_id: str, pool) -> str:
    """
    Fetch user email from the database using the user_id (username/sub).
    Required for RAG agent which filters by email.
    """
    if not pool:
        return None
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT email FROM users WHERE email = $1 OR username = $1 OR CAST(user_id AS TEXT) = $1", user_id)
            if row:
                return row['email']
    except Exception as e:
        logger.error(f"Error fetching email for {user_id}: {e}")
    return None


# --- ROUTES ---

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "fastapi-banking-agent",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, authorization: Optional[str] = Header(None)):
    """
    Main Chat Entry Point.
    Routes to RAG system for knowledge-based responses.
    """
    token = extract_token_from_header(request.token, authorization)

    # Extract User ID from Token
    user_id = request.user_id
    if token:
        extracted_user = extract_user_from_token(token)
        if extracted_user and extracted_user != "unknown_user":
            user_id = extracted_user
        else:
            print(f"{YELLOW}[WARN] Invalid or unparseable token. Rejecting request.{RESET}")
            raise HTTPException(status_code=401, detail="Authentication required: Invalid token")
    else:
        print(f"{YELLOW}[WARN] No token provided. Authorization required.{RESET}")
        raise HTTPException(status_code=401, detail="Authentication required: No token provided")

    print(f"\n[INFO] [FASTAPI] Incoming Chat from {BLUE}{user_id}{RESET}: '{request.message}'")
    logger.info(f"Incoming Chat: {request.message}")

    # 1. Build User Context (kept for logging/stub)
    user_context = UserContext(
        user_id=user_id,
        role=UserRole.USER,
        location="unknown",
        preferences={},
        transaction_history=[],
        token=token
    )

    # 2. Get User Email for RAG
    user_email = await get_user_email(user_id, app.state.pool)
    if not user_email:
        print(f"{YELLOW}[WARN] Could not find email for user {user_id}. utilizing user_id as fallback.{RESET}")
        user_email = user_id

    # 3. Call RAG Agent
    if not app.state.rag_chain:
        return {"response": "AI Service (RAG) is currently unavailable.", "timestamp": datetime.now().isoformat()}

    print(f"   [FASTAPI] calling RAG Agent for {user_email}...")

    # Run the synchronous RAG query in a thread
    rag_response = await asyncio.to_thread(query_rag, app.state.rag_chain, request.message, user_email)

    print(f"[DEBUG] RAG Response: {rag_response}")

    # 4. Handle Response
    if rag_response.get("is_research"):
        print(f"   [FASTAPI] Research Intent Detected. Fetching market news...")
        research_data = rag_response.get("result", {})
        
        # Extract parameters from LLM's JSON 
        topics = research_data.get("research", ["grocery", "inflation"])
        if not isinstance(topics, list):
            topics = [str(topics)]
            
        location = research_data.get("location", "Montreal") # Default or extract from user context if available
        
        try:
            # Use the internal agent's active research capability
            if internal_agent:
                research_context = await asyncio.to_thread(internal_agent._perform_market_research, location, topics)
                
                # Format a nice response
                response_text = f"Here is the latest market research for {location}:\n\n{research_context}"
            else:
                response_text = "Market research agent is currently unavailable."
        except Exception as e:
            logger.error(f"Market Research Error: {e}")
            response_text = "I encountered an error while fetching market news. Please try again."
            
        return {"response": response_text, "timestamp": datetime.now().isoformat()}

    elif rag_response.get("is_sql"):
        result_data = rag_response.get("result")

        print(f"   [FASTAPI] Summarizing SQL results for user...")

        if isinstance(result_data, dict) and "error" in result_data:
             logger.error(f"SQL Execution Error: {result_data['error']}")
             response_text = "I encountered an internal error while accessing the data. Please contact support."
        else:
            try:
                llm = app.state.rag_chain.combine_documents_chain.llm_chain.llm
                response_text = await asyncio.to_thread(
                    summarize_results,
                    llm,
                    result_data,
                    request.message
                )
            except Exception as e:
                print(f"[ERROR] Summarization failed: {e}")
                # SECURITY: Never send raw DB data to client
                response_text = "I found some information but had trouble formatting it. Please try rephrasing your question."

        # SECURITY: Scrub any hash-like patterns from the response
        response_text = scrub_sensitive_data(response_text)
        return {"response": response_text, "timestamp": datetime.now().isoformat()}
    else:
        response_text = rag_response.get("result", "I couldn't generate a response.")
        response_text = scrub_sensitive_data(response_text)
        return {"response": response_text, "timestamp": datetime.now().isoformat()}


@app.post("/api/user/financial-advice")
async def manual_advice_endpoint(request: FinancialAdviceRequest, authorization: Optional[str] = Header(None)):
    """Direct advice endpoint (Legacy/Direct Access)"""
    try:
        token = extract_token_from_header(request.token, authorization)

        # Extract User ID from Token
        user_id = request.user_id
        if token:
            extracted_user = extract_user_from_token(token)
            if extracted_user and extracted_user != "unknown_user":
                user_id = extracted_user

        print(f"\n[INFO] [FASTAPI] Financial Advice Request for {BLUE}{user_id}{RESET}")

        real_transactions = []
        if token:
             headers = {"Authorization": f"Bearer {token}"}
             try:
                 print("   [INTERNAL] Fetching transactions from Spring API...")
                 response = requests.get(f"http://localhost:8082/api/transactions/current-user?limit=100", headers=headers, timeout=5)
                 if response.status_code == 200:
                     real_transactions = response.json()
                     print(f"   [INTERNAL] Got {len(real_transactions)} transactions.")
             except Exception as e:
                 print(f"   [INTERNAL] Transaction fetch failed: {e}")

        # Calculate Spending
        spending_data = {}
        if real_transactions:
            pass  # Simplified for resilience, relying on Agent to analyze list.
        else:
             spending_data = request.spending_data or {
                'week1': 120.50, 'week2': 145.30, 'week3': 135.80, 'week4': 160.20
            }

        user_context = UserContext(
            user_id=user_id,
            role=UserRole.USER,
            location="toronto",
            preferences={},
            transaction_history=real_transactions,
            token=token
        )

        if internal_agent:
            print("   [INTERNAL] Calling Agent for Advice...")

            advice = await internal_agent.provide_financial_advice(
                user_context=user_context,
                spending_data=spending_data,
                category=request.category,
                target_reduction=request.target_reduction
            )

            return {
                "success": True,
                "advice": {
                    "analysis_summary": advice.analysis_summary,
                    "weekly_spending": advice.weekly_spending,
                    "recommended_reduction": advice.recommended_reduction,
                    "savings_suggestions": advice.savings_suggestions,
                    "grocery_deals": advice.grocery_deals,
                    "action_plan": advice.action_plan,
                    "spending_by_category": getattr(advice, 'spending_by_category', {}),
                    "financial_news": getattr(advice, 'financial_news', [])
                },
                "real_data": {
                    "transaction_count": len(real_transactions),
                    "data_source": "database" if real_transactions else "mock",
                    "spending_breakdown": spending_data
                },
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"Advice Error: {e}")
        return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}

    return {"success": False, "error": "AI Agent not initialized. Ensure Ollama is running.", "timestamp": datetime.now().isoformat()}


@app.post("/api/admin/security-analysis")
async def admin_security_analysis(request: SecurityAnalysisRequest, authorization: Optional[str] = Header(None)):
    """Admin endpoint for comprehensive security analysis."""
    try:
        token = extract_token_from_header(request.token, authorization)

        user_id = request.user_id
        if token:
            extracted_user = extract_user_from_token(token)
            if extracted_user and extracted_user != "unknown_user":
                user_id = extracted_user

        print(f"\n[INFO] [FASTAPI] Security Analysis Request from {BLUE}{user_id}{RESET}")

        if not internal_agent:
            return {"success": False, "error": "AI Agent not available. Ensure Ollama is running.", "timestamp": datetime.now().isoformat()}

        admin_context = UserContext(
            user_id=user_id,
            role=UserRole.ADMIN,
            location=request.location,
            preferences={},
            transaction_history=[],
            token=token
        )

        result = await internal_agent.analyze_security_threats(
            log_file_path=request.log_file_path,
            transaction_data=request.transaction_data,
            user_context=admin_context
        )

        return {
            "success": True,
            "analysis": {
                "threat_detected": result.threat_detected,
                "threat_type": result.threat_type,
                "confidence_score": result.confidence_score,
                "severity": result.severity,
                "recommendation": result.recommendation,
                "explanation": result.explanation
            },
            "system_data": request.security_context or {},
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Security Analysis Error: {e}")
        return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}


@app.get("/api/admin/dashboard")
async def admin_dashboard():
    """Get admin security dashboard data."""
    try:
        if not internal_agent:
            return {"success": False, "error": "AI Agent not available. Ensure Ollama is running.", "timestamp": datetime.now().isoformat()}

        dashboard_data = await asyncio.to_thread(
            internal_agent.security_agent.get_security_dashboard
        )

        return {
            "success": True,
            "dashboard": dashboard_data,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Dashboard Error: {e}")
        return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}


@app.get("/api/grocery-deals/{location}")
async def get_grocery_deals(location: str):
    """Get grocery deals for a specific location."""
    try:
        if not internal_agent:
            return {"success": False, "error": "AI Agent not available.", "timestamp": datetime.now().isoformat()}

        deals = await asyncio.to_thread(internal_agent._get_grocery_deals, location)

        return {
            "success": True,
            "location": location,
            "deals": deals,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Grocery Deals Error: {e}")
        return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}


@app.post("/api/user/spending-analysis")
async def analyze_user_spending(request: SpendingAnalysisRequest):
    """Analyze user spending patterns from transaction history."""
    try:
        transactions = request.transactions

        # Analyze spending patterns
        total_spending = 0.0
        categories = {}

        for transaction in transactions:
            amount_raw = transaction.get('amount', '0')
            if isinstance(amount_raw, str):
                amount = float(amount_raw.replace('$', '').replace('-', '').replace('+', ''))
            else:
                amount = abs(float(amount_raw))
            total_spending += amount

            category = transaction.get('description', 'Other')
            categories[category] = categories.get(category, 0) + amount

        spending_analysis = {
            "total_spending": total_spending,
            "transaction_count": len(transactions),
            "categories": categories,
            "trends": "spending_increasing" if len(transactions) > 0 else "no_data",
            "recommendations": [
                "Consider setting a weekly budget limit",
                "Look for recurring subscriptions you can cancel",
                "Compare prices before making purchases"
            ]
        }

        return {
            "success": True,
            "analysis": spending_analysis,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Spending Analysis Error: {e}")
        return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}


@app.post("/api/advice-chat")
async def advice_chat_endpoint(request: ChatRequest, authorization: Optional[str] = Header(None)):
    """
    Advice Chat Entry Point.
    Routes to Grocery RAG system for meal planning and budget advice.
    """
    token = extract_token_from_header(request.token, authorization)
    user_id = request.user_id
    if token:
        extracted_user = extract_user_from_token(token)
        if extracted_user and extracted_user != "unknown_user":
            user_id = extracted_user

    print(f"\n[INFO] [FASTAPI] Incoming Advice Chat from {BLUE}{user_id}{RESET}: '{request.message}'")
    
    # Define a basic user context for the agent
    user_context = UserContext(
        user_id=user_id,
        role=UserRole.USER,
        location="montreal",  # Standard location for grocery checks
        preferences={},
        transaction_history=[],
        token=token
    )

    if internal_agent:
        response_text = await internal_agent.chat_with_agent(request.message, user_context)
    else:
        # Fallback to direct RAG
        rag_response = await asyncio.to_thread(query_grocery_rag, app.state.grocery_rag_chain, request.message)
        response_text = rag_response.get("result", "I couldn't generate a response.")
        
    return {"response": response_text, "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    print("--- Starting AI Banking Agent FastAPI Server ---")
    print("Available endpoints:")
    print("   GET  /api/health")
    print("   POST /api/chat")
    print("   POST /api/user/financial-advice")
    print("   POST /api/admin/security-analysis")
    print("   GET  /api/admin/dashboard")
    print("   GET  /api/grocery-deals/{location}")
    print("   POST /api/user/spending-analysis")
    uvicorn.run("fastapi_server:app", host="0.0.0.0", port=5000, reload=True)
