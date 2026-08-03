import sys
import torch
from langchain_ollama import ChatOllama

def verify_environment():
    print("Running environment checks...")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Torch version: {torch.__version__}")
    print(f"CUDA/MPS GPU accelerator available: {torch.cuda.is_available()}")

def test_local_llm():
    print("Connecting to local Ollama[Gemma:e4b]... ")
    try:
        llm = ChatOllama(model="gemma4:e4b",
                         temperature=1.0)
        prompt ="Hey AI, tell me one cool engineering feature of the Gemma4"

        print(f"User: {prompt}")

        response = llm.invoke(prompt)
        print(f"AI response: {response}")

    except Exception as e:
        print(f"Failed to connect to local Ollama[{e}]")

if __name__ == "__main__":
    print("Starting local Ollama[Gemma:e4b]... ")
    verify_environment()
    test_local_llm()

