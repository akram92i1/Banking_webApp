import os
import sys
import json
import psycopg2
from typing import Dict, Any, List
from decimal import Decimal

# Ensure we can import from parent directories if needed, though mostly using installed packages
# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(current_dir)

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
# Try importing from new libraries first, fall back to community
try:
    from langchain_ollama import OllamaEmbeddings, ChatOllama
except ImportError:
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_community.chat_models import ChatOllama

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Configuration
MODEL_NAME = "gemma3:4b"  # For generation
EMBEDDING_MODEL_NAME = "nomic-embed-text" # For embeddings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Pointing to logging/Data/banking_ai_scenarios.txt
# BASE_DIR is logging/Data/
# So we just use the file text in the current directory
KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "banking_ai_scenarios.txt")
DB_DIR = os.path.join(BASE_DIR, "faiss_index")

# Database Configuration
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "my_finance_db"
DB_USER = "bank_database_admin"
DB_PASS = "admin123"

# Banking Schema
BANKING_SCHEMA = """
## 🧑‍💼 `users` (user_id, username, email, phone, role...)
## 💰 `accounts` (account_id, user_id, account_number, balance, available_balance, account_type...)
## 🔄 `transactions` (transaction_id, from_account_id, to_account_id, amount, description, transaction_status, processed_at...)
## 💳 `cards` (card_id, account_id, card_number_hash, daily_limit, monthly_limit...)
## 🧾 `beneficiaries` (beneficiary_id, user_id, account_number, bank_name...)
"""

def load_documents(file_path):
    """Load the knowledge base document."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Knowledge base file not found at: {file_path}")
    
    print(f"Loading documents from {file_path}...")
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()
    return documents

def split_documents(documents):
    """Split documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    texts = text_splitter.split_documents(documents)
    print(f"Split documents into {len(texts)} chunks.")
    
    # Print chunks as requested
    print("\n--- Generated Chunks ---")
    for i, chunk in enumerate(texts):
        print(f"\nChunk {i+1}:")
        print(chunk.page_content)
        print("-" * 40)
    print("------------------------\n")
    
    return texts

def get_or_create_vector_db(texts=None, force_recreate=False):
    """Create or load the vector database."""
    # Use a dedicated embedding model
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)
    
    # Check if FAISS index exists
    index_file = os.path.join(DB_DIR, "index.faiss")
    
    if os.path.exists(DB_DIR) and os.path.exists(index_file) and not force_recreate and not texts:
        print(f"Loading existing Vector Store from {DB_DIR}...")
        try:
            vector_db = FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
             print(f"Error loading existing DB: {e}. Recreating...")
             return get_or_create_vector_db(texts, force_recreate=True)
        return vector_db
    else:
        if not texts:
            raise ValueError("No texts provided to create vector database.")
        print("Creating new Vector Store...")
        if os.path.exists(DB_DIR):
             import shutil
             shutil.rmtree(DB_DIR)
        
        vector_db = FAISS.from_documents(documents=texts, embedding=embeddings)
        print(f"Saving Vector Store to {DB_DIR}...")
        vector_db.save_local(DB_DIR)
    
    return vector_db

def execute_sql_query(sql_query):
    """Execute SQL query against the database and return JSON."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()
        cursor.execute(sql_query)
        
        # Get column names
        colnames = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        # Convert to list of dicts
        data = []
        for row in results:
            row_dict = {}
            for i, val in enumerate(row):
                # Handle datetime serialization
                if hasattr(val, 'isoformat'):
                    row_dict[colnames[i]] = val.isoformat()
                elif isinstance(val, Decimal):
                     row_dict[colnames[i]] = float(val)
                else:
                    row_dict[colnames[i]] = val
            data.append(row_dict)
            
        return json.dumps(data, indent=2)
        
    except Exception as e:
        print(f"❌ [DB ERROR] {e}") # Log for admin/debugging
        return json.dumps({"error": "Internal Database Error. Please contact support."})
    finally:
        if conn:
            conn.close()

def setup_rag_system(force_recreate_db=True):
    """Initialize the RAG system."""
    try:
        # 1. Load Documents
        documents = load_documents(KNOWLEDGE_BASE_PATH)
        
        # 2. Split
        texts = split_documents(documents)
        
        # 3. Vector DB
        vector_db = get_or_create_vector_db(texts, force_recreate=force_recreate_db)
        
        # 4. LLM
        llm = ChatOllama(model=MODEL_NAME)
        
        # 5. Prompt
        template = """You are an AI Banking Assistant. 
You have two sources of information:
1. The provided RAG Context (Banking Policies).
2. The Database Schema (User Data).

Database Schema:
""" + BANKING_SCHEMA + """

INSTRUCTIONS:
- If the user asks about general banking info (policies, fees, how-to), use the **Context**.
- If the user asks for PERSONAL data (balance, transactions, profile), generate a **SQL QUERY**.
- For SQL queries:
  - Return ONLY a JSON object with the key "sql".
  - Use the placeholder 'USER_EMAIL_PLACEHOLDER' for the user's email.
  - **IMPORTANT**: Use PostgreSQL syntax (e.g., `date_trunc`, `ILIKE`, `CURRENT_DATE`, `NOW()`). Do NOT use MySQL syntax like `DATE_SUB` or `CURDATE()`.
  - Example: {{ "sql": "SELECT * FROM users WHERE email = 'USER_EMAIL_PLACEHOLDER'" }}

Context:
{context}

Question: {question}

Answer:"""
        
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=template,
        )
        
        # 6. Chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_db.as_retriever(search_kwargs={"k": 3}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
        
        return qa_chain
        
    except Exception as e:
        print(f"Error setting up RAG system: {e}")
        return None

def query_rag(qa_chain, query, user_email=None):
    """Query the RAG system."""
    try:
        response = qa_chain.invoke({"query": query})
        result_text = response["result"]
        
        # Check if result looks like JSON SQL
        if "sql" in result_text or "USER_EMAIL_PLACEHOLDER" in result_text:
            try:
                # Try validation/extraction of JSON
                clean_json = result_text.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].strip()
                
                 # If simple text is just the JSON
                if clean_json.startswith("{") and clean_json.endswith("}"):
                    data = json.loads(clean_json)
                    if "sql" in data:
                        sql_query = data["sql"]
                        if user_email:
                            # Replace the placeholder with the actual email
                            sql_query = sql_query.replace("USER_EMAIL_PLACEHOLDER", user_email)
                            print(f"\n[Executing SQL]: {sql_query}")
                            db_result = execute_sql_query(sql_query)
                            return {
                                "result": db_result,
                                "source_documents": [],
                                "is_sql": True
                            }
                        else:
                            return {"result": "Error: User email required for this query.", "source_documents": []}
            except Exception as e:
                print(f"Failed to parse SQL JSON: {e}")
        
        return {
            "result": result_text,
            "source_documents": response["source_documents"],
            "is_sql": False
        }
    except Exception as e:
        return {"result": f"Error querying system: {e}", "source_documents": []}

def summarize_results(llm, results, user_query):
    """
    Summarize database results into natural language using the LLM.
    
    Args:
        llm: The ChatOllama instance (can be retrieved from qa_chain.combine_documents_chain.llm_chain.llm)
        results: The JSON string or list/dict from the database.
        user_query: The original question from the user.
    """
    try:
        if not results or results == "[]" or results == "null":
            return "I searched the database but found no matching records."

        prompt = f"""You are a helpful Banking Assistant.
        The user asked: "{user_query}"
        
        The database returned this RAW JSON data:
        {results}
        
        INSTRUCTIONS:
        1.  **Analyze the User's Query**: Understand what they are looking for (e.g., specific amount, date, person).
        2.  **Filter the Data**: Ignore technical fields like UUIDs (`703ad4...`), `created_at` timestamps (unless date is asked), or internal codes.
        3.  **Answer Directly**: Start with a direct answer to the question.
        4.  **Be Concise**: Do not repeat the same info. Do not say "Here are the details" if you just gave them.
        5.  **Format**: 
            - Use bolding for key values (e.g., **$2.50**).
            - Use natural language sentences.
            - Only use bullet points if there are MULTIPLE distinct transactions/items.

        Example 1:
        Query: "Did I get paid $500?"
        Data: [{{ "amount": 500.00, "type": "DEPOSIT", "sender": "Work Inc", "date": "2023-10-01" }}]
        Answer: "Yes, you received a deposit of **$500.00** from **Work Inc** on October 1st, 2023."

        Example 2 (Complex):
        Query: "Show my last 3 transactions"
        Data: [...]
        Answer: "Here are your last 3 transactions:
        *   **$50.00** at Metro (Grocery) on Oct 10
        *   **$12.50** at Uber on Oct 09
        *   **$100.00** Transfer to Savings on Oct 08"

        Context:
        User Query: "{user_query}"
        Data:
        {results}

        Answer:"""
        
        response = llm.invoke(prompt)
        
        # Handle different response types from invoke (String vs AIMessage)
        if hasattr(response, 'content'):
            return response.content
        return str(response)
        
    except Exception as e:
        print(f"Error summarising results: {e}")
        return f"I found some data: {results}"

if __name__ == "__main__":
    print("--- Banking RAG System Initialization ---")
    
    # Debug: Test DB Connection
    print("Testing Database Connection...")
    try:
        test_conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        test_conn.close()
        print(f"✅ SUCCESS: Connected to PostgreSQL database '{DB_NAME}' on {DB_HOST}:{DB_PORT}")
    except Exception as e:
        print(f"❌ ERROR: Could not connect to database: {e}")
        print("Continuing with RAG-only mode (SQL features will fail)...")

    qa_instance = setup_rag_system(force_recreate_db=True) # Force recreate to load correct data
    
    if qa_instance:
        # Ask for user email
        print("\nPlease enter your email address for account access:")
        user_email = input("Email: ").strip()
        print(f"\nWelcome, {user_email}. System Ready! Enter your questions below (type 'exit' to quit).")
        
        while True:
            try:
                user_input = input("\nQuery: ").strip()
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("Exiting...")
                    break
                
                if not user_input:
                    continue
                
                print("Thinking...")
                output = query_rag(qa_instance, user_input, user_email)
                print("\nAnswer:")
                print(output["result"])
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")