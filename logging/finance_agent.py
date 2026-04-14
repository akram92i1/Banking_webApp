#!/usr/bin/env python3
import json
import asyncio
import logging
from typing import Dict, Any

from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

try:
    from langchain.memory import ConversationBufferWindowMemory
except ImportError:
    from langchain_classic.memory import ConversationBufferWindowMemory
try:
    from langchain.agents import AgentType, initialize_agent
except ImportError:
    from langchain_classic.agents import AgentType, initialize_agent

from agent_types import UserRole, UserContext, ThreatAnalysisResult, FinancialAdvice
from agent_prompts import finance_advisory_prompt
from agent_tools import LogAnalysisTool, RLAnalysisTool, GetTransactionsTool
from testRFL import ThreatDetectionSystem
from threatDetection import BankingSecurityAgent, LogProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FinanceAgent")

class TransactionRAGManager:
    """Dynamically creates an in-memory FAISS vector index for a user's transaction history."""
    def __init__(self, ollama_model: str = "nomic-embed-text"):
        self.embeddings = OllamaEmbeddings(model=ollama_model)
        self.vector_store = None

    def build_from_transactions(self, transactions):
        if not transactions:
            self.vector_store = None
            return
            
        docs = []
        for t in transactions:
            # Create a rich semantic string for the embedding
            display_text = f"Transaction on {t.get('date', 'Unknown')}: {t.get('description', 'Unknown item')} for {t.get('amount', '$0')}. Category: {t.get('category', 'Unknown')}."
            docs.append(Document(page_content=display_text, metadata=t))
            
        try:
            self.vector_store = FAISS.from_documents(docs, self.embeddings)
            logger.info(f"Built Transaction RAG with {len(docs)} records.")
        except Exception as e:
            logger.error(f"Failed to build Transaction RAG: {e}")
            self.vector_store = None

    def search_transactions(self, query: str, k: int = 3):
        if not self.vector_store:
            return "Transaction RAG is empty or uninitialized."
        docs = self.vector_store.similarity_search(query, k=k)
        return "\n".join([d.page_content for d in docs])

class FinanceAgent:
    def __init__(self, ollama_model: str = "gemma3:4b"):
        logger.info("Mounting Finance Agent to Graphic Card...")
        self.llm = ChatOllama(
            model=ollama_model,
            temperature=0.0,
            keep_alive="5m"
        )
        
        self.memory = ConversationBufferWindowMemory(
            k=10,
            memory_key="chat_history",
            return_messages=True
        )
        
        self.security_agent = BankingSecurityAgent()
        self.rl_detector = ThreatDetectionSystem()
        self.log_processor = LogProcessor(self.security_agent)
        
        self.failed_tools = {}
        self.transaction_rag = TransactionRAGManager()
        
        self._initialize_tools()
        self._initialize_agents()
        
    def _initialize_tools(self):
        self.log_analysis_tool = LogAnalysisTool(parent=self)
        self.rl_analysis_tool = RLAnalysisTool(parent=self)
        self.get_transactions_tool = GetTransactionsTool(parent=self)
        
    def _initialize_agents(self):
        # Admin / Security Agent
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
            agent_kwargs={'prefix': admin_prefix},
            max_iterations=5,
            max_execution_time=60
        )
        
        # Finance Agent
        finance_prefix = finance_advisory_prompt.messages[0].prompt.template
        self.finance_agent_chain = initialize_agent(
            tools=[self.get_transactions_tool],
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            max_iterations=10,
            max_execution_time=120,
            handle_parsing_errors=True,
            agent_kwargs={'prefix': finance_prefix}
        )

    async def chat_with_agent(self, message: str, user_context: 'UserContext') -> str:
        try:
            self.user_context = user_context # Provide context to tools
            
            if not hasattr(self, 'failed_tools'):
                self.failed_tools = {}
            if message not in self.failed_tools:
                self.failed_tools[message] = set()
            
            # Optionally build RAG context if transaction_history exists
            rag_context = ""
            if user_context.transaction_history:
                self.transaction_rag.build_from_transactions(user_context.transaction_history)
                rag_matches = self.transaction_rag.search_transactions(message)
                if rag_matches and "empty" not in rag_matches:
                    rag_context = f"\n[Transaction RAG Matches System Info: {rag_matches}]\n"

            inputs = {
                "input": f"[User Context: Region: {user_context.location}, Auth Token Present: {bool(user_context.token)}]{rag_context}\nUser Question: {message}"
            }

            if user_context.role == UserRole.ADMIN:
                logger.info("Executing Admin logic.")
                result = await asyncio.to_thread(self.security_agent_chain.invoke, inputs)
                return result.get("output", "Error processing admin request.")
            else:
                logger.info("Executing Finance logic.")
                result = await asyncio.to_thread(self.finance_agent_chain.invoke, inputs)
                return result.get("output", "Error processing request.")
                
        except Exception as e:
            logger.error(f"Finance Chat error: {e}")
            return f"I encountered an error processing your request: {str(e)}"

    async def analyze_security_threats(self, log_file_path: str = None, transaction_data: dict = None, user_context: 'UserContext' = None) -> Any:
        try:
            inputs = {"input": f"Analyze current system security state focusing on logs at {log_file_path} and transaction: {json.dumps(transaction_data)}"}
            result = await asyncio.to_thread(self.security_agent_chain.invoke, inputs)
            return ThreatAnalysisResult(
                threat_detected=True,
                threat_type="Analyzed by AI", 
                confidence_score=0.85,
                severity="Medium",
                recommendation="Review full report",
                explanation=result.get("output", "Analysis completed")
            )
        except Exception as e:
            logger.error(f"Security analysis error: {e}")
            raise e
            
    async def provide_financial_advice(self, user_context: 'UserContext', spending_data: dict, category: str, target_reduction: float) -> Any:
        try:
            prompt = f"Provide advice to reduce spending in {category} by ${target_reduction}. Data: {json.dumps(spending_data)}"
            response = await self.llm.ainvoke(prompt)
            output = response.content if hasattr(response, 'content') else str(response)
            
            return FinancialAdvice(
                analysis_summary=output[:200],
                weekly_spending=sum({k:float(v) for k,v in spending_data.items()}.values()),
                recommended_reduction=target_reduction,
                savings_suggestions=[output],
                grocery_deals=[],
                action_plan="Follow provided suggestions."
            )
        except Exception as e:
            logger.error(f"Financial advisory error: {e}")
            raise e
