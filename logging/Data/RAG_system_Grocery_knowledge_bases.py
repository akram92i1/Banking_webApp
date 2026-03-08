import os
import glob
from langchain_community.document_loaders import TextLoader
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

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
MODEL_NAME = "gemma3:4b"
EMBEDDING_MODEL_NAME = "nomic-embed-text"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLYERS_DIR = os.path.join(BASE_DIR, "flyers")
DB_DIR = os.path.join(BASE_DIR, "faiss_grocery_index")

def load_all_flyers(directory: str):
    """Load all text files from the flyers directory."""
    documents = []
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return documents
        
    for filepath in glob.glob(os.path.join(directory, "*.txt")):
        print(f"Loading flyers from {filepath}...")
        try:
            loader = TextLoader(filepath, encoding="utf-8")
            docs = loader.load()
            
            # Inject store name into content to ensure context is kept 
            store_name = os.path.basename(filepath).split('.')[0].replace('_', ' ')
            for doc in docs:
                doc.page_content = f"STORE: {store_name}\n\n" + doc.page_content
                doc.metadata["store"] = store_name.lower()
                
            documents.extend(docs)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
    return documents

def split_documents(documents):
    """Split documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=250,
        separators=["\n\n", "\n", " ", ""]
    )
    texts = text_splitter.split_documents(documents)
    print(f"Split documents into {len(texts)} chunks.")
    return texts

def get_or_create_grocery_vector_db(texts=None, force_recreate=False):
    """Create or load the vector database."""
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)
    index_file = os.path.join(DB_DIR, "index.faiss")
    
    if os.path.exists(DB_DIR) and os.path.exists(index_file) and not force_recreate and not texts:
        print(f"Loading existing Vector Store from {DB_DIR}...")
        try:
            vector_db = FAISS.load_local(DB_DIR, embeddings, allow_dangerous_deserialization=True)
            return vector_db
        except Exception as e:
             print(f"Error loading existing DB: {e}. Recreating...")
             if texts:
                 return get_or_create_grocery_vector_db(texts, force_recreate=True)
             else:
                 return None
    else:
        if not texts:
            raise ValueError("No texts provided to create vector database.")
        print("Creating new Vector Store...")
        import shutil
        if os.path.exists(DB_DIR):
             shutil.rmtree(DB_DIR)
        
        vector_db = FAISS.from_documents(documents=texts, embedding=embeddings)
        print(f"Saving Vector Store to {DB_DIR}...")
        vector_db.save_local(DB_DIR)
        return vector_db

def setup_grocery_rag_system(force_recreate_db=False):
    """Initialize the RAG system."""
    try:
        documents = load_all_flyers(FLYERS_DIR)
        if not documents and force_recreate_db:
            print("No documents found in flyers directory.")
            return None
            
        texts = split_documents(documents) if documents else None
        
        vector_db = get_or_create_grocery_vector_db(texts, force_recreate=force_recreate_db)
        if not vector_db:
            return None
            
        llm = ChatOllama(model=MODEL_NAME, temperature=0.1)
        
        template = """You are a helpful and budget-conscious AI Grocery and Meal Planning Assistant.
You have access to the latest grocery flyers and deals in the provided Context.

INSTRUCTIONS:
- You must carefully analyze the user's budget, frequency of shopping, and constraints.
- If the user asks for a meal plan, design a detailed plan and list the ingredients needed with their prices and stores.
- ALWAYS try to find the cheapest options from the provided Context.
- Explicitly mention the store name for each deal you recommend. If the user specifies a store, NEVER recommend items from other stores.
- 🧮 MATHEMATICS: You must strictly calculate the estimated total cost by adding the prices of all items together. 
- 🎯 BUDGET TARGET: You MUST ensure the final total is as close as possible to the user's target budget (e.g. within $5 of the target). If your current total is too far below the budget, ADD more items. If your total is over the budget, REMOVE items.
- Format your output nicely using markdown bullets and bold text for prices and stores.
- 🚨 MANDATORY: You MUST include at least one relevant emoji next to EVERY single food item or product you list in your response. For example: "🍎 Apples", "🍗 Chicken breast", "� Broccoli", "🥛 Milk". If you do not use emojis, the system will fail.

Context:
{context}

Question: {question}

Answer:"""
        
        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=template,
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_db.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )
        
        return qa_chain
        
    except Exception as e:
        print(f"Error setting up Grocery RAG system: {e}")
        return None

def query_grocery_rag(qa_chain, query):
    """Query the RAG system."""
    try:
        query_lower = query.lower()
        filter_dict = {}
        if "maxi" in query_lower:
            filter_dict["store"] = "maxi montreal"
        elif "iga" in query_lower:
            filter_dict["store"] = "iga montreal"
        elif "super c" in query_lower:
            filter_dict["store"] = "super c montreal"
        elif "metro" in query_lower:
            filter_dict["store"] = "metro montreal"
        elif "walmart" in query_lower:
            filter_dict["store"] = "walmart montreal"
            
        if filter_dict:
            qa_chain.retriever.search_kwargs["filter"] = filter_dict
            enhanced_query = f"[STRICT REGULATION: You must ONLY use items from {filter_dict['store']} and NO OTHER STORE for this answer.]\n{query}"
        else:
            if "filter" in qa_chain.retriever.search_kwargs:
                del qa_chain.retriever.search_kwargs["filter"]
            enhanced_query = query

        response = qa_chain.invoke({"query": enhanced_query})
        return {
            "result": response["result"],
            "source_documents": response["source_documents"]
        }
    except Exception as e:
        return {"result": f"Error querying Grocery RAG system: {e}", "source_documents": []}

if __name__ == "__main__":
    print("--- Grocery RAG System Initialization ---")
    qa_instance = setup_grocery_rag_system(force_recreate_db=True)
    if qa_instance:
        print("\nWelcome to the Grocery Meal Planner! (type 'exit' to quit)")
        while True:
            try:
                user_input = input("\nQuery (e.g., 'Make a $50 weekly meal plan'): ").strip()
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                if not user_input:
                    continue
                    
                print("Thinking...")
                output = query_grocery_rag(qa_instance, user_input)
                print("\nAnswer:")
                print(output["result"])
            except KeyboardInterrupt:
                break
