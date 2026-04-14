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
from RAG_system_Grocery_Openrouter import setup_grocery_rag_system, query_grocery_rag

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
        "Are there any deals on apples in iga?"
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
        df.to_csv("ragas_evaluation_results.csv", index=False)
        print("\nDetailed results saved to 'ragas_evaluation_results.csv'")
        
    except Exception as e:
        print(f"\nError during ragas evaluation: {e}")

if __name__ == "__main__":
    main()
