from langchain.prompts import PromptTemplate

BANKING_SCHEMA = "schema_placeholder"

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
  - Example: {{ "sql": "SELECT * FROM users WHERE email = 'USER_EMAIL_PLACEHOLDER'" }}

Context:
{context}

Question: {question}

Answer:"""

print("Attempting to create PromptTemplate...")
try:
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )
    # To trigger the validation explicitly if it hasn't already
    print(f"Input variables: {prompt.input_variables}")
    
    # Try formatting
    formatted = prompt.format(context="test_context", question="test_question")
    print("Formatting successful!")
    
except Exception as e:
    print(f"Caught expected error: {e}")
