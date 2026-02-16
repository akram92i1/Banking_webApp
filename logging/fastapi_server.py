import os
import json
import asyncio
import logging
import requests
import asyncpg
from typing import Dict, Any, List, Optional
from datetime import datetime
from datetime import datetime
from contextlib import asynccontextmanager

# Check if we need to add the current directory to sys.path for RAG imports
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

try:
    from Data.RAG_system_knowledge_based import setup_rag_system, query_rag, summarize_results
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"Error importing RAG system: {e}")
    RAG_AVAILABLE = False

from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# --- CONFIGURATION ---
OPENROUTER_API_KEY = "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"
SITE_URL = "http://localhost:8000"
SITE_NAME = "MyFastAPIApp"
SCHEMA_PATH = r"e:\Banking_application\Banking_webApp\databaseService\banking_schema_attributes.md"

# Database Configuration
DATABASE_URL = "postgresql://bank_database_admin:admin123@localhost:5432/my_finance_db"

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FastAPIServer")

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

# --- APP LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"
    
    print(f"{BLUE}--- STARTING FASTAPI SERVER ---{RESET}")
    print(f"{BLUE}Connecting to Database at {DATABASE_URL[:20]}...{RESET}")
    try:
        app.state.pool = await asyncpg.create_pool(DATABASE_URL)
        print(f"{GREEN}[SUCCESS] Database Connected Successfully!{RESET}")
    except Exception as e:
        print(f"{RED}[ERROR] Database Connection Failed: {e}{RESET}")
        app.state.pool = None
        
    # Startup: Initialize RAG System
    print(f"{BLUE}Initializing RAG System...{RESET}")
    if RAG_AVAILABLE:
        # Run synchronous RAG setup in a separate thread
        app.state.rag_chain = await asyncio.to_thread(setup_rag_system)
        if app.state.rag_chain:
             print(f"{GREEN}[SUCCESS] RAG System Initialized!{RESET}")
        else:
             print(f"{RED}[ERROR] RAG System Initialization Failed.{RESET}")
    else:
        print(f"{RED}[WARNING] RAG System not available (Import Error).{RESET}")
        app.state.rag_chain = None

    yield
    
    # Shutdown: Close DB
    print(f"{BLUE}--- SHUTTING DOWN ---{RESET}")
    if app.state.pool:
        await app.state.pool.close()
        print(f"{BLUE}Database Connection Closed.{RESET}")

# --- APP SETUP ---
app = FastAPI(title="Banking AI Microservice", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL STATE ---
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

import base64

def load_schema() -> str:
    """Load the banking schema markdown"""
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "Schema not found."

def extract_user_from_token(token: str) -> str:
    """
    Extracts the user ID (subject) from a JWT token without verifying signature.
    Useful for logging and context context before passing to secured backend.
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


# Removed call_openrouter_brain - logic moved to internal_agent.process_user_intent

async def get_user_email(user_id: str, pool) -> str:
    """
    Fetch user email from the database using the user_id (username/sub).
    Required for RAG agent which filters by email.
    """
    if not pool:
        return None
    try:
        async with pool.acquire() as conn:
            # Assuming 'users' table has 'username' (which is user_id here) and 'email'
            # Adjust column names if your schema is different!
            # Based on schema in RAG file: users (user_id, username, email, phone, role...)
            # If user_id passed to this func is actually the username:
            row = await conn.fetchrow("SELECT email FROM users WHERE username = $1 OR user_id = $1", user_id)
            if row:
                return row['email']
    except Exception as e:
        logger.error(f"Error fetching email for {user_id}: {e}")
    return None

# Removed execute_raw_sql as RAG now handles SQL generation & execution internally

# --- ROUTES ---

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "fastapi-banking-agent"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest, authorization: Optional[str] = Header(None)):
    """
    Main Entry Point.
    1. Calls OpenRouter to classify.
    2. Routes to appropriate internal function.
    """
    token = request.token
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = authorization

    # Extract User ID from Token (Security Best Practice)
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

    # ANSI Color for Blue
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
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
        # Fallback if email not found, though RAG might fail for personal queries
        print(f"{YELLOW}[WARN] Could not find email for user {user_id}. utilizing user_id as fallback.{RESET}")
        user_email = user_id # Fallback, though RAG expects email for replacement

    # 3. Call RAG Agent
    if not app.state.rag_chain:
        return {"response": "AI Service (RAG) is currently unavailable."}

    print(f"   [FASTAPI] calling RAG Agent for {user_email}...")
    
    # Run the synchronous RAG query in a thread
    rag_response = await asyncio.to_thread(query_rag, app.state.rag_chain, request.message, user_email)
    
    print(f"[DEBUG] RAG Response: {rag_response}")

    # 4. Handle Response
    if rag_response.get("is_sql"):
        # It was a SQL query result
        result_data = rag_response.get("result")
        
        # Format the JSON result for display
        print(f"   [FASTAPI] Summarizing SQL results for user...")
        
        # Use simple formatting for errors
        if isinstance(result_data, dict) and "error" in result_data:
             logger.error(f"SQL Execution Error: {result_data['error']}")
             response_text = "I encountered an internal error while accessing the data. Please contact support."
        else:
            # Use LLM to summarize the data
            # Note: app.state.rag_chain is a RetrievalQA chain. 
            # We access the underlying LLM via .combine_documents_chain.llm_chain.llm
            # Or just create a new ChatOllama if needed, but reusing is better.
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
                # Fallback to raw data
                response_text = f"Found records: {result_data}"

        return {"response": response_text}
    else:
        # Normal chat response
        return {"response": rag_response.get("result", "I couldn't generate a response.")}

@app.post("/api/user/financial-advice")
async def manual_advice_endpoint(request: FinancialAdviceRequest, authorization: Optional[str] = Header(None)):
    """Direct advice endpoint (Legacy/Direct Access)"""
    # ANSI Color for Blue
    BLUE = "\033[94m"
    RESET = "\033[0m"
    
    try:
        # Extract Token
        token = request.token
        if not token and authorization:
            if authorization.startswith("Bearer "):
                token = authorization.split(" ")[1]
            else:
                token = authorization
        
        # Extract User ID from Token
        user_id = request.user_id # Fallback
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
                 # Verify port 8082 or 8080. Previous code used 8082.
                 response = requests.get(f"http://localhost:8082/api/transactions/current-user?limit=100", headers=headers, timeout=5)
                 if response.status_code == 200:
                     real_transactions = response.json()
                     print(f"   [INTERNAL] Got {len(real_transactions)} transactions.")
             except Exception as e:
                 print(f"   [INTERNAL] Transaction fetch failed: {e}")
        
        # Calculate Spending
        spending_data = {}
        if real_transactions:
            now = datetime.now()
            # Simple weekly aggregation
            # ... (Logic copied from Flask)
            pass # Simplified for resilience, relying on Agent to analyze list.
        else:
             spending_data = request.spending_data or {
                'week1': 120.50, 'week2': 145.30, 'week3': 135.80, 'week4': 160.20
            }

        user_context = UserContext(
            user_id=user_id,
            role=UserRole.USER,
            location="toronto", # Default
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
                    "spending_by_category": advice.spending_by_category,
                    "financial_news": advice.financial_news
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
        return {"success": False, "error": str(e)}

    return {"status": "error", "message": "Agent not initialized"}

if __name__ == "__main__":
    import uvicorn
    # Use lifespan logic
    uvicorn.run("fastapi_server:app", host="0.0.0.0", port=5000, reload=True)
