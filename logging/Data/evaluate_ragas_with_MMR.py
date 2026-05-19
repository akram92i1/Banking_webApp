import os
import sys

# Ensure correct path so imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.chat_models import ChatOpenAI

try:
    from langchain_ollama import OllamaEmbeddings
except ImportError:
    from langchain_community.embeddings import OllamaEmbeddings

# Import custom OpenRouter RAG functions
from RAG_system_Grocery_Openrouter_MMR import setup_grocery_rag_system, query_grocery_rag

# Replace with the actual key from the file or environment
OPENROUTER_API_KEY = "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"

def main():
    print("=== Ragas Evaluation Configuration ===")
    
    # Ragas needs its own wrapper of Langchain LLMs and embeddings
    print("Setting up evaluator LLM (Llama 3.1 8b via OpenRouter) and Embeddings (Nomic)...")
    evaluator_llm = ChatOpenAI(
        model="meta-llama/llama-3.1-8b-instruct", 
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.0
    )
    
    evaluator_embeddings = OllamaEmbeddings(model="nomic-embed-text")

    print("\nInitializing Grocery RAG system...")
    qa_chains = setup_grocery_rag_system(force_recreate_db=False)
    if not qa_chains:
        print("Failed to initialize QA chains. Exiting.")
        return

    # Define test questions to measure Faithfulness and Answer Relevancy
    test_questions = [
        "What is the price of chicken breasts at maxi?",
        "Make a $50 weekly meal plan at super_c.",
        "Are there any deals on apples in iga?",
        "Where can I find the cheapest eggs this week?",
        "Is there a sale on milk at Metro?",
        "Can you suggest a vegetarian meal plan for $60 at Maxi?",
        "Which store has the best discount on ground beef right now?",
        "How much is a 10kg bag of flour at Walmart?",
        "Are there any promotions on toilet paper at Super C?",
        "Build a high-protein grocery list for $80 at IGA.",
        "What's the current price of butter at Provigo?",
        "Find me the best deals on fresh salmon in Montreal.",
        "Is there a flyer discount for pasta at Maxi?",
        "Can you compare the price of avocados at IGA and Super C?",
        "Create a gluten-free meal plan for a family of 4 under $100.",
        "Are strawberries on sale this week anywhere?",
        "What are the top 5 specials at Metro this week?",
        "How much are organic carrots at Maxi?",
        "Where is the cheapest place to buy a whole frozen turkey?",
        "Can you make a budget-friendly vegan grocery list for $40?",
        "Are there any BOGO deals at IGA?",
        "What's the price of a block of cheddar cheese at Super C?",
        "Does Walmart have any discounts on laundry detergent?",
        "Find me the best price for olive oil.",
        "Can you help me plan a keto diet menu for $75 at Maxi?",
        "Where can I find cheap bell peppers this week?",
        "Are there any deals on oat milk at Provigo?",
        "Compare the cost of a 12-pack of Coca-Cola across different stores.",
        "What is the cheapest store to buy baby diapers right now?",
        "Create a $50 grocery list focusing on fresh produce at Super C."
    ]

    ragas_data = {
        "question": [],
        "answer": [],
        "contexts": []
    }

    print("\n=== Generating RAG Responses ===")
    for question in test_questions:
        print(f"\nQ: {question}")
        output = query_grocery_rag(qa_chains, question)
        
        answer = output.get("result", "")
        print(f"A: {answer[:100]}...") # Print a snippet
        
        # Ragas expects a list of text context strings for each question
        contexts = [doc.page_content for doc in output.get("source_documents", [])]

        ragas_data["question"].append(question)
        ragas_data["answer"].append(answer)
        ragas_data["contexts"].append(contexts)

    # Note: wait before evaluating to respect possible rate limits (optional)
    
    print("\n=== Preparing Ragas Dataset ===")
    dataset = Dataset.from_dict(ragas_data)

    print("\nRunning metrics: faithfulness, answer_relevancy...")
    metrics = [faithfulness, answer_relevancy]

    try:
        # Evaluate using the provided HuggingFace dataset
        eval_result = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=evaluator_llm,
            embeddings=evaluator_embeddings
        )
        print("\n=== Evaluation Results ===")
        print(eval_result)
        
        # Export to CSV for further review
        df = eval_result.to_pandas()
        df.to_csv("ragas_evaluation_results_mmr.csv", index=False)
        print("\nDetailed results saved to 'ragas_evaluation_results_mmr.csv'")
        
    except Exception as e:
        print(f"\nError during ragas evaluation: {e}")

if __name__ == "__main__":
    main()
