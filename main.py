from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from retriever import get_retriever, check_ollama_alive
from config import LLM_MODEL, DEFAULT_TOP_K, configure_windows_encoding

# Set UTF-8 encoding for Windows terminals
configure_windows_encoding()

def build_qa_chain(model_name: str = LLM_MODEL):
    """Builds and returns the LCEL prompt | model chain."""
    model = OllamaLLM(model=model_name)
    template = """
You are an expert answering questions based strictly on the provided context.

Context:
{reviews}

Question:
{question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    return prompt | model

def run_cli():
    """Runs the interactive command-line question-answering loop."""
    print("=" * 60)
    print("🤖 Local AI Knowledge Assistant (CLI)")
    print(f"Active Model: {LLM_MODEL}")
    print("=" * 60)

    # Health check
    if not check_ollama_alive():
        print("\n⚠️  WARNING: Could not connect to Ollama at http://localhost:11434")
        print("Please ensure the Ollama service is running (`ollama serve`).\n")

    retriever = get_retriever(k=DEFAULT_TOP_K)
    chain = build_qa_chain()

    while True:
        print("\n" + "-" * 60)
        try:
            question = input("Please enter your question ('q' to quit): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Goodbye!")
            break

        print("-" * 60 + "\n")

        if question.lower() == "q":
            print("Exiting application. Goodbye!")
            break
        if not question:
            continue

        try:
            # 1. Retrieve relevant chunks
            reviews = retriever.invoke(question)

            # 2. Stream answer in real-time
            print("Assistant: ", end="", flush=True)
            for chunk in chain.stream({"reviews": reviews, "question": question}):
                print(chunk, end="", flush=True)
            print("\n")

            # 3. Display source citations
            print("--- Sources Cited ---")
            for i, doc in enumerate(reviews, start=1):
                source = doc.metadata.get("source", "Unknown source")
                preview = doc.page_content[:120].replace("\n", " ").strip()
                print(f"[{i}] {source}: \"{preview}...\"")
            print("---------------------")

        except Exception as e:
            print(f"\n❌ Error during generation: {e}")
            print("Tip: Make sure the Ollama service is running and the model is downloaded.")

if __name__ == "__main__":
    run_cli()