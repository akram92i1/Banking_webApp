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
    from langchain_ollama import ChatOllama
except ImportError:
    from langchain_community.chat_models import ChatOllama

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
    print("Setting up evaluator LLM (Llama 3.1 via local Ollama) and Embeddings (Nomic)...")
    evaluator_llm = ChatOllama(
        model="llama3.1",
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
        "Create a $50 grocery list focusing on fresh produce at Super C.",
        "What is the cheapest coffee available at Maxi?",
        "Find deals on frozen pizza at IGA.",
        "How much does a dozen eggs cost at Super C?",
        "Are there discounts on Greek yogurt at Metro?",
        "Can you suggest a healthy breakfast plan for $20 at Provigo?",
        "What's the price of a watermelon at Maxi?",
        "Where can I find the best deal on ground turkey?",
        "Does Walmart have specials on dog food?",
        "What are the promotions on paper towels at Super C?",
        "Build a $30 snack list for a party from IGA.",
        "Is there a sale on orange juice at Metro?",
        "Compare the price of bananas at Maxi and Provigo.",
        "Find a cheap brand of almond milk at Walmart.",
        "What is the current discount on pork chops at Super C?",
        "Create a pescatarian dinner menu for 2 under $25 at IGA.",
        "Are apples on sale at Maxi this week?",
        "What's the best price for a bag of rice in Montreal?",
        "How much is canned tuna at Provigo?",
        "Are there any deals on ice cream at Metro?",
        "Can you find gluten-free bread specials at Walmart?",
        "What's the cheapest price for broccoli at Super C?",
        "Is there a discount on peanut butter at IGA?",
        "Where can I buy the most affordable chicken thighs?",
        "Create a low-carb grocery list for $50 at Maxi.",
        "Are there promotions on dish soap at Provigo?",
        "What's the cost of a bag of potatoes at Metro?",
        "Compare the price of tomatoes at Super C and Walmart.",
        "Find deals on frozen berries at IGA.",
        "What is the best special on cheese slices at Maxi?",
        "Can you make a budget-friendly kids lunch list for $20?",
        "Are there discounts on cereal at Super C?",
        "Where is the cheapest place to buy bacon?",
        "What's the price of a lettuce head at Provigo?",
        "Does Metro have any deals on bottled water?",
        "Find the best price for black beans at Walmart.",
        "Create a $40 grocery list for baking essentials at IGA.",
        "Are there any specials on chips at Maxi?",
        "What is the current price of cucumber at Super C?",
        "Compare the cost of a jar of mayonnaise across stores.",
        "What is the cheapest store to buy body wash right now?",
        "Find me deals on fresh spinach at Provigo.",
        "Is there a sale on frozen vegetables at Metro?",
        "Can you help me find cheap protein bars at Walmart?",
        "What are the top discounts on pork ribs at IGA?",
        "Where can I find the most affordable shrimp?",
        "Create a $15 movie night snack list at Maxi.",
        "Are there promotions on cat litter at Super C?",
        "What is the price of a whole pineapple at Provigo?",
        "Does Metro have any specials on bakery items?",
        "Find the best deal for a gallon of milk."
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
