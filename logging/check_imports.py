
try:
    from langchain.chains import RetrievalQA
    print("langchain.chains OK")
except ImportError as e:
    print(f"langchain.chains FAIL: {e}")

try:
    from langchain_classic.chains.retrieval_qa.base import RetrievalQA
    print("langchain_classic OK")
except ImportError as e:
    print(f"langchain_classic FAIL: {e}")

try:
    from langchain.prompts import PromptTemplate
    print("langchain.prompts OK")
except ImportError as e:
    print(f"langchain.prompts FAIL: {e}")

try:
    from langchain_core.prompts import PromptTemplate
    print("langchain_core.prompts OK")
except ImportError as e:
    print(f"langchain_core.prompts FAIL: {e}")
