import asyncio
import os
import asyncpg
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import yfinance as yf

router = APIRouter(prefix="/api/simulator", tags=["Banking Simulator"])

# Use a writable connection string for initialization
INIT_DB_URL = "postgresql://bank_database_admin:admin123@localhost:5432/my_finance_db"
# Use a service connection for actual API calls
API_DB_URL = "postgresql://bank_database_admin:admin123@localhost:5432/my_finance_db"

DB_POOL = None

async def get_db_pool():
    global DB_POOL
    if DB_POOL is None:
        DB_POOL = await asyncpg.create_pool(API_DB_URL)
    return DB_POOL

async def init_simulator_tables():
    """Create isolated tables if they don't exist using admin credentials."""
    print("--- Initializing Simulator Tables ---")
    
    try:
        # Connect directly with the admin URL to create tables safely
        admin_conn = await asyncpg.connect(INIT_DB_URL)
        # Table 1: Mock Accounts
        await admin_conn.execute("""
            CREATE TABLE IF NOT EXISTS mock_bank_accounts (
                account_id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                balance NUMERIC(15, 2) DEFAULT 5000.00
            )
        """)
        # Table 2: Simulated Transactions
        await admin_conn.execute("""
            CREATE TABLE IF NOT EXISTS mock_transactions (
                transaction_id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                amount NUMERIC(15, 2) NOT NULL,
                merchant VARCHAR(255),
                category VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Table 3: Savings Goals (Budget)
        await admin_conn.execute("""
            CREATE TABLE IF NOT EXISTS saving_goals (
                goal_id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                weekly_budget NUMERIC(15, 2) NOT NULL
            )
        """)
        # Table 4: Virtual Investments
        await admin_conn.execute("""
            CREATE TABLE IF NOT EXISTS virtual_investments (
                investment_id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                total_invested NUMERIC(15, 2) DEFAULT 0.00,
                symbol VARCHAR(50) DEFAULT 'SPY'
            )
        """)
        
        # Ensure a test user exists
        await admin_conn.execute("""
            INSERT INTO mock_bank_accounts (user_id, balance) 
            VALUES ('user001', 5000.00) 
            ON CONFLICT (user_id) DO NOTHING
        """)
        await admin_conn.execute("""
            INSERT INTO saving_goals (user_id, weekly_budget) 
            VALUES ('user001', 100.00) 
            ON CONFLICT (user_id) DO NOTHING
        """)
        await admin_conn.execute("""
            INSERT INTO virtual_investments (user_id, total_invested, symbol) 
            VALUES ('user001', 0.00, 'SPY') 
            ON CONFLICT (user_id) DO NOTHING
        """)
        await admin_conn.close()
        print("[SUCCESS] Simulator Tables Initialized")
    except Exception as e:
        print(f"[ERROR] initializing simulator tables: {e}")

# --- API MODELS ---
class TransactionRequest(BaseModel):
    user_id: str
    amount: float
    merchant: str

class GoalRequest(BaseModel):
    user_id: str
    budget: float

# --- ENDPOINTS ---
@router.post("/log-grocery")
async def log_grocery_transaction(req: TransactionRequest):
    """Logs a simulated grocery transaction and triggers auto-invest."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # 1. Deduct from mock bank
        await conn.execute("UPDATE mock_bank_accounts SET balance = balance - $1 WHERE user_id = $2", req.amount, req.user_id)
        
        # 2. Log transaction
        await conn.execute(
            "INSERT INTO mock_transactions (user_id, amount, merchant, category) VALUES ($1, $2, $3, 'Grocery')", 
            req.user_id, req.amount, req.merchant
        )
        
        # 3. Check savings goal to auto-invest
        goal = await conn.fetchrow("SELECT weekly_budget FROM saving_goals WHERE user_id = $1", req.user_id)
        saved_amount = 0.0
        
        if goal and req.amount < goal['weekly_budget']:
            saved_amount = float(goal['weekly_budget']) - req.amount
            
            # 4. Move savings to investment
            await conn.execute("UPDATE mock_bank_accounts SET balance = balance - $1 WHERE user_id = $2", saved_amount, req.user_id)
            await conn.execute("UPDATE virtual_investments SET total_invested = total_invested + $1 WHERE user_id = $2", saved_amount, req.user_id)
            
        return {
            "success": True,
            "transaction_amount": req.amount,
            "budget_target": float(goal['weekly_budget']) if goal else None,
            "saved_amount": saved_amount,
            "message": f"Saved ${saved_amount:.2f} and auto-invested!" if saved_amount > 0 else "Transaction logged. No savings to invest."
        }

@router.get("/dashboard/{user_id}")
async def get_simulator_dashboard(user_id: str):
    """Returns the mock banking balance and live virtual investment data."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        account = await conn.fetchrow("SELECT balance FROM mock_bank_accounts WHERE user_id = $1", user_id)
        investment = await conn.fetchrow("SELECT total_invested, symbol FROM virtual_investments WHERE user_id = $1", user_id)
        
        if not account or not investment:
            raise HTTPException(status_code=404, detail="Simulator data not found for user")
            
        # Get live market data for the symbol (e.g., SPY)
        symbol = investment['symbol']
        try:
            ticker = yf.Ticker(symbol)
            todays_data = ticker.history(period='1d')
            current_price = todays_data['Close'].iloc[0]
            prev_close = ticker.info.get('previousClose', current_price)
            daily_change_pct = ((current_price - prev_close) / prev_close) * 100
        except Exception as e:
            print(f"Error fetching yfinance data: {e}")
            current_price = 0
            daily_change_pct = 0
            
        # Mock calculation: Assuming the user bought at exactly the current price for simplicity,
        # but displaying the daily change of the ETF to make it feel "live".
        invested_value = float(investment['total_invested'])
        live_value = invested_value * (1 + (daily_change_pct / 100))
        
        return {
            "bank_balance": float(account['balance']),
            "investment_portfolio": {
                 "symbol": symbol,
                 "total_contributed": invested_value,
                 "live_value": live_value,
                 "market_change_pct": round(daily_change_pct, 2)
            }
        }
