#!/usr/bin/env python3
import json
import asyncio
import logging
from typing import Dict, List

from langchain_ollama import ChatOllama
try:
    from langchain.memory import ConversationBufferWindowMemory
except ImportError:
    from langchain_classic.memory import ConversationBufferWindowMemory
try:
    from langchain.agents import AgentType, initialize_agent
except ImportError:
    from langchain_classic.agents import AgentType, initialize_agent

from agent_types import UserContext
from agent_prompts import grocery_advisory_prompt
from agent_tools import GroceryDealsTool, GenerateMealPlanTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GroceryAgent")

class GroceryAgent:
    def __init__(self, ollama_model: str = "gemma3:4b"):
        logger.info("Mounting Grocery Agent to Graphic Card...")
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
        
        self.grocery_stores = self._load_grocery_store_data()
        self.failed_tools = {}
        
        self._initialize_tools()
        self._initialize_agents()
        self._preload_grocery_deals_for_rag()
        
    def _preload_grocery_deals_for_rag(self):
        print("\n" + "="*50)
        print("🔄 [GROCERY] Loading flyer data for RAG system... Please wait.")
        self.grocery_rag_chains = None
        try:
            import sys
            import os
            data_dir = os.path.join(os.path.dirname(__file__), 'Data')
            if data_dir not in sys.path:
                sys.path.append(data_dir)
            
            from RAG_system_Grocery_knowledge_bases import setup_grocery_rag_system
            # Disable force recreate to speed up switching
            self.grocery_rag_chains = setup_grocery_rag_system(force_recreate_db=False)
            if self.grocery_rag_chains:
                print(f"✅ [GROCERY] Vector Embeddings initialized successfully for: {', '.join(self.grocery_rag_chains.keys())}!")
            else:
                print("⚠️ [GROCERY] Warning: Vector Embeddings failed to initialize or no flyers found.")
                
        except Exception as e:
            print(f"❌ [GROCERY] Failed to load RAG: {e}")
            logger.error(f"Failed to preload grocery deals: {e}")
        print("="*50 + "\n")

    def _initialize_tools(self):
        self.grocery_deals_tool = GroceryDealsTool(parent=self)
        self.generate_meal_plan_tool = GenerateMealPlanTool(parent=self)
        self.tools = [self.grocery_deals_tool, self.generate_meal_plan_tool]
        
    def _initialize_agents(self):
        grocery_prefix = grocery_advisory_prompt.messages[0].prompt.template
        self.grocery_agent_chain = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            max_iterations=15,
            max_execution_time=300,
            handle_parsing_errors=True,
            agent_kwargs={'prefix': grocery_prefix}
        )
        
    def _load_grocery_store_data(self) -> Dict[str, List[Dict]]:
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
        location_key = location.lower()
        return self.grocery_stores.get(location_key, [])

    async def chat_with_agent(self, message: str, user_context: 'UserContext') -> str:
        try:
            self.user_context = user_context 
            
            if not hasattr(self, 'failed_tools'):
                self.failed_tools = {}
            if message not in self.failed_tools:
                self.failed_tools[message] = set()
            
            inputs = {
                "input": f"[User Context: Region: {user_context.location}, Auth Token Present: {bool(user_context.token)}]\nUser Question: {message}"
            }
            
            profile = getattr(user_context, "grocery_profile", None)
            if profile:
                inputs["input"] = f"[Dietary: {profile.dietary_restrictions}, Budget: {profile.weekly_budget}]\n" + inputs["input"]
                
            logger.info("Executing Grocery logic.")
            result = await asyncio.to_thread(self.grocery_agent_chain.invoke, inputs)
            return result.get("output", "Error processing request.")
            
        except Exception as e:
            logger.error(f"Grocery Chat error: {e}")
            return f"I encountered an error processing your request: {str(e)}"
