import os
import sys
import re
import json
import psycopg2
from typing import Dict, Any, List, Tuple
from decimal import Decimal

# Ensure we can import from parent directories if needed, though mostly using installed packages
# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(current_dir)

from langchain_community.document_loaders import TextLoader
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
# Try importing from new libraries first, fall back to community
try:
    from langchain_ollama import OllamaEmbeddings, ChatOllama
except ImportError:
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_community.chat_models import ChatOllama

try:
    from langchain.chains import RetrievalQA
except ImportError:
    from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# Configuration
MODEL_NAME = "gemma3:4b"  # For generation
EMBEDDING_MODEL_NAME = "nomic-embed-text" # For embeddings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Pointing to logging/Data/banking_ai_scenarios.txt
# BASE_DIR is logging/Data/
# So we just use the file text in the current directory
KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "banking_ai_scenarios.txt")
DB_DIR = os.path.join(BASE_DIR, "faiss_index")

# Database Configuration (read-only user for AI agent - principle of least privilege)
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "my_finance_db"
DB_USER = "ai_agent_readonly"
DB_PASS = "readonly_agent_secure_2024"

# Banking Schema (only safe columns listed - sensitive columns like password_hash, ssn_hash, card_number_hash are excluded)
BANKING_SCHEMA = """
## `users` (user_id, username, email, phone, role, first_name, last_name, address, is_active, created_at, updated_at)
## `accounts` (account_id, user_id, account_number, balance, available_balance, account_type, account_status, interest_rate, credit_limit, overdraft_limit, opened_at)
## `transactions` (transaction_id, from_account_id, to_account_id, amount, description, transaction_type, transaction_status, processed_at, fee_amount, currency, reference_number)
## `cards` (card_id, account_id, card_type, card_status, daily_limit, monthly_limit, expiry_date, is_contactless, issued_at, blocked_at)
## `beneficiaries` (beneficiary_id, user_id, beneficiary_name, account_number, bank_name, routing_number, nickname, is_verified, relationship, created_at)
"""

# --- SECURITY CONSTANTS ---
BLOCKED_COLUMNS = {
    "password_hash", "ssn_hash", "card_number_hash", "cvv_hash", "pin_hash",
    "secret_question", "secret_answer", "security_answer", "token", "refresh_token"
}

DANGEROUS_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "CREATE", "GRANT", "REVOKE", "EXEC", "EXECUTE"
]

def validate_sql_query(sql_query: str) -> Tuple[bool, str]:
    """
    Validate a SQL query for security before execution.
    Returns (is_valid, error_message).
    """
    sql_upper = sql_query.upper().strip()

    # 1. Must be a SELECT statement
    if not sql_upper.startswith("SELECT"):
        return False, "Only SELECT queries are allowed."

    # 2. Block dangerous keywords (word-boundary match)
    for keyword in DANGEROUS_KEYWORDS:
        if re.search(r'\b' + keyword + r'\b', sql_upper):
            return False, f"Forbidden SQL keyword detected: {keyword}"

    # 3. No multiple statements (semicolons)
    # Remove semicolons that are inside string literals before checking
    stripped = re.sub(r"'[^']*'", "", sql_query)
    if ";" in stripped:
        return False, "Multiple SQL statements are not allowed."

    # 4. No UNION (prevents UNION-based exfiltration)
    if re.search(r'\bUNION\b', sql_upper):
        return False, "UNION queries are not allowed."

    # 5. Must contain the user email placeholder (user scoping)
    if "USER_EMAIL_PLACEHOLDER" not in sql_query:
        return False, "Query must be scoped to the authenticated user (missing USER_EMAIL_PLACEHOLDER)."

    # 6. Block SELECT * (must use explicit column names)
    if re.search(r'\bSELECT\s+\*', sql_upper):
        return False, "SELECT * is not allowed. Please specify explicit column names."

    # 7. Block sensitive columns (strip string literals first to avoid false positives)
    sql_no_strings = re.sub(r"'[^']*'", "", sql_query)
    for col in BLOCKED_COLUMNS:
        if re.search(r'\b' + col + r'\b', sql_no_strings.lower()):
            return False, f"Access to column '{col}' is forbidden."

    # 8. Enforce row limit (cap at 50 even if LLM specifies higher)
    limit_match = re.search(r'\bLIMIT\s+(\d+)', sql_upper)
    if limit_match:
        limit_val = int(limit_match.group(1))
        if limit_val > 50:
            sql_query = re.sub(r'\bLIMIT\s+\d+', 'LIMIT 50', sql_query, flags=re.IGNORECASE)
    else:
        sql_query = sql_query.rstrip().rstrip(";") + " LIMIT 50"

    return True, sql_query


def sanitize_db_results(data: List[Dict]) -> List[Dict]:
    """Strip sensitive columns from database results as a safety net."""
    for row in data:
        keys_to_remove = [k for k in row if k.lower() in BLOCKED_COLUMNS]
        for k in keys_to_remove:
            del row[k]
    return data


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

def execute_sql_query(sql_query, params=None):
    """Execute SQL query against the database and return JSON.
    Uses parameterized queries to prevent SQL injection."""
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
        cursor.execute(sql_query, params)

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

        # Layer 4: Sanitize results - strip sensitive columns
        data = sanitize_db_results(data)

        return json.dumps(data, indent=2)

    except Exception as e:
        print(f"[DB ERROR] {e}") # Log for admin/debugging
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
        
        # 5. Prompt (Security-hardened)
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
  - Example: {{ "sql": "SELECT account_type, balance, available_balance FROM accounts a JOIN users u ON a.user_id = u.user_id WHERE u.email = 'USER_EMAIL_PLACEHOLDER'" }}

SECURITY RULES (MANDATORY - NEVER VIOLATE THESE):
1. **USER SCOPING**: EVERY SQL query MUST include `WHERE u.email = 'USER_EMAIL_PLACEHOLDER'` or `WHERE email = 'USER_EMAIL_PLACEHOLDER'`. You may ONLY return data belonging to the authenticated user.
2. **FORBIDDEN COLUMNS**: NEVER include these columns in any SELECT: password_hash, ssn_hash, card_number_hash, cvv_hash, pin_hash, secret_question, secret_answer. If the user asks for any of these, politely refuse.
3. **SELECT ONLY**: ONLY generate SELECT statements. NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT, or REVOKE statements.
4. **NO UNION**: NEVER use UNION or UNION ALL.
5. **NO MULTIPLE STATEMENTS**: NEVER include semicolons or multiple SQL statements.
6. **NO OTHER USERS' DATA**: If the user asks to VIEW another user's data (e.g., "show me John's balance", "get asmith's profile"), REFUSE. Respond with: "I can only access your own account information. I cannot look up other users' data."
   - EXCEPTION: If the user asks about their OWN transactions involving another person (e.g., "show my transactions with asmith", "did I send money to bob"), this IS allowed. Always scope the outer query to USER_EMAIL_PLACEHOLDER, and use a subquery to look up the other person's account_id for filtering.
   - Example: {{ "sql": "SELECT t.amount, t.description FROM transactions t JOIN accounts a ON (t.from_account_id = a.account_id OR t.to_account_id = a.account_id) JOIN users u ON a.user_id = u.user_id WHERE u.email = 'USER_EMAIL_PLACEHOLDER' AND (t.description ILIKE '%asmith%' OR t.to_account_id IN (SELECT a2.account_id FROM accounts a2 JOIN users u2 ON a2.user_id = u2.user_id WHERE u2.username = 'asmith'))" }}
7. **NO SELECT ***: Always specify explicit column names. Never use SELECT *.

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
    """Query the RAG system with security validation."""
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

                        # --- LAYER 2: Validate the SQL query ---
                        is_valid, validation_result = validate_sql_query(sql_query)
                        if not is_valid:
                            print(f"\n[SECURITY] SQL BLOCKED: {validation_result}")
                            print(f"[SECURITY] Blocked query: {sql_query}")
                            return {
                                "result": "I'm sorry, but I cannot process that request. " + validation_result,
                                "source_documents": [],
                                "is_sql": False
                            }
                        # validation_result contains the (possibly LIMIT-appended) query
                        sql_query = validation_result

                        if user_email:
                            # --- LAYER 3: Parameterized queries ---
                            # psycopg2 uses %s for params but also interprets % as format specifiers.
                            # ILIKE '%text%' would break because %t is seen as a specifier.
                            # Fix: replace placeholder with a temp token, escape all %, then swap token for %s.
                            placeholder_count = sql_query.count("USER_EMAIL_PLACEHOLDER")
                            TEMP_TOKEN = "__PSYCOPG2_PARAM__"
                            # Step 1: Replace placeholder (with and without quotes) with temp token
                            sql_query = sql_query.replace("'USER_EMAIL_PLACEHOLDER'", TEMP_TOKEN)
                            sql_query = sql_query.replace("USER_EMAIL_PLACEHOLDER", TEMP_TOKEN)
                            # Step 2: Escape all literal % as %% (for ILIKE patterns etc.)
                            sql_query = sql_query.replace("%", "%%")
                            # Step 3: Replace temp token with %s (psycopg2 parameter)
                            sql_query = sql_query.replace(TEMP_TOKEN, "%s")
                            params = tuple([user_email] * placeholder_count)

                            print(f"\n[Executing SQL]: {sql_query} with params={params}")
                            db_result = execute_sql_query(sql_query, params)
                            return {
                                "result": db_result,
                                "source_documents": [],
                                "is_sql": True
                            }
                        else:
                            return {"result": "Error: User email required for this query.", "source_documents": []}
            except json.JSONDecodeError as e:
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
        return "I found some information but had trouble formatting it. Please try rephrasing your question."

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