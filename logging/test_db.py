import asyncio
import asyncpg
import logging

# Database Configuration
DATABASE_URL = "postgresql://bank_database_admin:admin123@localhost:5433/my_finance_db"

async def test_connection():
    print(f"Testing connection to: {DATABASE_URL}")
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("SUCCESS: Connected to PostgreSQL!")
        await conn.close()
    except Exception as e:
        print(f"FAILURE: Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
