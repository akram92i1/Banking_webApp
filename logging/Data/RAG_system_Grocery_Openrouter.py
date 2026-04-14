import os
import glob
from langchain_community.document_loaders import TextLoader
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

try:
    from langchain_ollama import OllamaEmbeddings
except ImportError:
    from langchain_community.embeddings import OllamaEmbeddings

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    # Fallback to older package location if needed
    from langchain_community.chat_models import ChatOpenAI

try:
    from langchain.chains import RetrievalQA
except ImportError:
    from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

# Configuration
MODEL_NAME = "meta-llama/llama-3.1-8b-instruct" # OpenRouter Model
OPENROUTER_API_KEY = "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"
EMBEDDING_MODEL_NAME = "nomic-embed-text"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FLYERS_DIR = os.path.join(BASE_DIR, "flyers")

try:
    from flyer_ocr_parser import load_flyers_with_ocr
except ImportError:
    load_flyers_with_ocr = None

def load_all_flyers_by_store(directory: str):
    """Load all text files from the flyers directory and group them by store, plus OCR scans."""
    documents_by_store = {}
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return documents_by_store
        
    all_docs = []
    
    # 1. Load OCR Documents if available
    if load_flyers_with_ocr:
        ocr_docs = load_flyers_with_ocr(directory)
        if ocr_docs:
            print(f"Loaded {len(ocr_docs)} documents via OCR.")
            all_docs.extend(ocr_docs)
            
    # 2. Existing text fallback loading
    for filepath in glob.glob(os.path.join(directory, "*.md")):
        print(f"Loading flyers from {filepath}...")
        try:
            loader = TextLoader(filepath, encoding="utf-8")
            all_docs.extend(loader.load())
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            
    # Group and format all documents
    for doc in all_docs:
        # Determine store name
        if "metadata" in dir(doc) and getattr(doc, "metadata", {}).get("source"):
            filepath = doc.metadata["source"]
        elif isinstance(doc.metadata, dict) and "source" in doc.metadata:
            filepath = doc.metadata["source"]
        else:
            filepath = "unknown_internal.txt"
            
        basename = os.path.basename(filepath).lower()
        if "super_c" in basename:
            store_name = "super_c"
        else:
            store_name = basename.split('_')[0]
            
        store_name_display = store_name.replace("_", " ").title()
        
        # Prepend store tag to content if not already added
        if not doc.page_content.startswith(f"STORE: {store_name_display}"):
            doc.page_content = f"STORE: {store_name_display}\n\n" + doc.page_content
            
        doc.metadata["store"] = store_name
        
        if store_name not in documents_by_store:
            documents_by_store[store_name] = []
        documents_by_store[store_name].append(doc)
        
    return documents_by_store

def split_documents(documents):
    """Split documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=250,
        separators=["\n\n", "\n", " ", ""]
    )
    texts = text_splitter.split_documents(documents)
    
    # Critical Fix: Prepend the store name to EVERY chunk after splitting!
    for chunk in texts:
        store = getattr(chunk, "metadata", {}).get("store", "Unknown").replace("_", " ").title()
        # Only inject if it's not already at the very start of the chunk
        if not chunk.page_content.startswith(f"STORE: {store}"):
            chunk.page_content = f"STORE: {store}\n\n" + chunk.page_content
            
    return texts

def get_or_create_grocery_vector_db_for_store(store_name: str, texts=None, force_recreate=False):
    """Create or load the vector database specifically for a single store."""
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL_NAME)
    db_dir = os.path.join(BASE_DIR, f"faiss_grocery_index_{store_name}")
    index_file = os.path.join(db_dir, "index.faiss")
    
    if os.path.exists(db_dir) and os.path.exists(index_file) and not force_recreate and not texts:
        print(f"Loading existing Vector Store for {store_name} from {db_dir}...")
        try:
            return FAISS.load_local(db_dir, embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
            print(f"Error loading DB for {store_name}: {e}. Recreating...")
            if texts:
                return get_or_create_grocery_vector_db_for_store(store_name, texts, force_recreate=True)
            return None
    else:
        if not texts:
            print(f"No texts provided to create vector database for {store_name}.")
            return None
        print(f"Creating new Vector Store for {store_name}...")
        import shutil
        if os.path.exists(db_dir):
             shutil.rmtree(db_dir)
        
        vector_db = FAISS.from_documents(documents=texts, embedding=embeddings)
        print(f"Saving Vector Store to {db_dir}...")
        vector_db.save_local(db_dir)
        return vector_db

def setup_grocery_rag_system(force_recreate_db=False):
    """Initialize the multiple vector databases for the RAG system."""
    try:
        documents_by_store = load_all_flyers_by_store(FLYERS_DIR)
        if not documents_by_store and force_recreate_db:
            print("No documents found in flyers directory.")
            return None
            
        qa_chains = {}
        
        # OpenRouter Chat Model
        llm = ChatOpenAI(
            model=MODEL_NAME, 
            openai_api_key=OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.1
        )
        
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
- 🚨 MANDATORY: You MUST include at least one relevant emoji next to EVERY single food item or product you list in your response. For example: "🍎 Apples", "🍗 Chicken breast", "🥦 Broccoli", "🥛 Milk". If you do not use emojis, the system will fail.

Context:
{context}

Question: {question}

Answer:"""
        prompt = PromptTemplate(input_variables=["context", "question"], template=template)

        for store_name, documents in documents_by_store.items():
            texts = split_documents(documents) if documents else None
            vector_db = get_or_create_grocery_vector_db_for_store(store_name, texts, force_recreate=force_recreate_db)
            
            if vector_db:
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    chain_type="stuff",
                    retriever=vector_db.as_retriever(search_kwargs={"k": 5}),
                    return_source_documents=True,
                    chain_type_kwargs={"prompt": prompt}
                )
                qa_chains[store_name] = qa_chain
                
        return qa_chains if qa_chains else None
        
    except Exception as e:
        print(f"Error setting up Grocery RAG system: {e}")
        return None

def query_grocery_rag(qa_chains, query):
    """Query the store-specific RAG databases."""
    try:
        query_lower = query.lower()
        target_store = None
        
        # Check if user specified a store
        for store in qa_chains.keys():
            store_display = store.replace("_", " ")
            if store_display in query_lower:
                target_store = store
                break
                
        if target_store:
            # Route to the specific store's vector db
            enhanced_query = f"[STRICT REGULATION: You must ONLY use items from {target_store.replace('_', ' ').title()} and NO OTHER STORE for this answer.]\n{query}"
            response = qa_chains[target_store].invoke({"query": enhanced_query})
            return {
                "result": response["result"],
                "source_documents": response["source_documents"]
            }
        else:
            # Query all active vector DBs independently from their retrievers
            all_docs = []
            for chain in qa_chains.values():
                docs = chain.retriever.invoke(query)
                all_docs.extend(docs)
                
            # Limit global documents to not overflow context (e.g., top 10 mixed)
            all_docs = all_docs[:10] 
            
            if not all_docs:
                return {"result": "No grocery deals found across any store databases for this query.", "source_documents": []}
                
            # Use any chain to inject the combined cross-store documents into the prompt
            first_chain = list(qa_chains.values())[0]
            response = first_chain.combine_documents_chain.invoke({
                "input_documents": all_docs,
                "question": query
            })
            
            return {
                "result": response["output_text"],
                "source_documents": all_docs
            }
            
    except Exception as e:
        return {"result": f"Error querying Grocery RAG system: {e}", "source_documents": []}

if __name__ == "__main__":
    print("--- Grocery RAG System Initialization (Multi-Store OpenRouter Version) ---")
    qa_chains = setup_grocery_rag_system(force_recreate_db=True)
    if qa_chains:
        print(f"\nWelcome to the Grocery Meal Planner! Loaded Vector DBs for: {', '.join(qa_chains.keys())} (type 'exit' to quit)")
        while True:
            try:
                user_input = input("\nQuery (e.g., 'Make a $50 weekly meal plan at maxi'): ").strip()
                if user_input.lower() in ["exit", "quit", "q"]:
                    break
                if not user_input:
                    continue
                    
                print("Thinking...")
                output = query_grocery_rag(qa_chains, user_input)
                print("\nAnswer:")
                print(output["result"])
            except KeyboardInterrupt:
                break
