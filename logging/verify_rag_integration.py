
import sys
import os
import asyncio
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the RAG system BEFORE importing fastapi_server
# This prevents different import errors or actual initialization
sys.modules["Data.RAG_system_knowledge_based"] = MagicMock()
from Data.RAG_system_knowledge_based import setup_rag_system, query_rag

# Mock ai_banking_agent to avoid pandas/numpy binary incompatibility issues
mock_agent_module = MagicMock()
# Define UserContext and UserRole for the mock
from dataclasses import dataclass
from enum import Enum
@dataclass
class UserContext:
    user_id: str
    role: str
    location: str
    preferences: dict
    transaction_history: list
    token: str

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

mock_agent_module.UserContext = UserContext
mock_agent_module.UserRole = UserRole
mock_agent_module.AIBankingAgent = MagicMock()

sys.modules["ai_banking_agent"] = mock_agent_module

# AsyncMock helper
from unittest.mock import Mock

class AsyncMock(Mock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

# Now import the app
from fastapi_server import app

client = TestClient(app)

def test_chat_sql_response():
    """Test that SQL responses from RAG are formatted correctly."""
    print("\n--- Testing SQL Response ---")
    
    # Mock RAG response for SQL
    with patch("fastapi_server.query_rag") as mock_query:
        mock_query.return_value = {
            "result": [{"id": 1, "name": "Test User", "balance": 1000}],
            "is_sql": True,
            "source_documents": []
        }
        
        # Mock app.state.rag_chain to be truthy
        app.state.rag_chain = MagicMock()
        
        # Mock DB pool for email lookup
        app.state.pool = MagicMock()
        
        # Mock get_user_email logic effectively by mocking the pool behavior or the function itself
        # Easier to patch the helper function in fastapi_server
        with patch("fastapi_server.get_user_email", new_callable=AsyncMock) as mock_email:
            mock_email.return_value = "test@example.com"
            
            response = client.post(
                "/api/chat",
                json={"user_id": "test_user", "message": "Check balance"},
                headers={"Authorization": "Bearer mock_token"}
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            assert response.status_code == 200
            assert "Found 1 records" in response.json()["response"]
            assert "Test User" in response.json()["response"]

def test_chat_text_response():
    """Test that Text responses from RAG are passed through."""
    print("\n--- Testing Text Response ---")
    
    with patch("fastapi_server.query_rag") as mock_query:
        mock_query.return_value = {
            "result": "This is a general policy answer.",
            "is_sql": False,
            "source_documents": []
        }
        
        app.state.rag_chain = MagicMock()
        
        with patch("fastapi_server.get_user_email", new_callable=AsyncMock) as mock_email:
            mock_email.return_value = "test@example.com"
        
            response = client.post(
                "/api/chat",
                json={"user_id": "test_user", "message": "What is the policy?"},
                headers={"Authorization": "Bearer mock_token"}
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            assert response.status_code == 200
            assert "This is a general policy answer" in response.json()["response"]

# AsyncMock helper
from unittest.mock import Mock

class AsyncMock(Mock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


# AsyncMock helper
from unittest.mock import Mock

class AsyncMock(Mock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

if __name__ == "__main__":
    try:
        test_chat_sql_response()
        test_chat_text_response()
        print("\n✅ Verification Passed!")
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        import traceback
        traceback.print_exc()
