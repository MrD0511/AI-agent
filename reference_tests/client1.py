import chromadb
import numpy as np
from google import genai

# Initialize Gemini client
client = genai.Client(api_key="AIzaSyAB6po8ng-NXb651W0dkQx1tXOtf3KyN0o")

# Initialize ChromaDB (persistent storage)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="chat_memory")

def get_embedding(text):
    """Generate an embedding for the given text using Gemini API."""
    try:
        response = client.models.embed_content(
            model="gemini-embedding-exp-03-07",
            contents=[text]
        )
        return response.embeddings[0].values  # Return embedding as a list
    except Exception as e:
        print(f"Embedding Error: {e}")
        return None

def store_conversation(question, answer):
    """Store question-answer pairs in ChromaDB."""
    embedding = get_embedding(question)
    if embedding:
        print(f"✅ Storing: {question} -> {answer}")  # Debugging
        collection.add(
            ids=[question],  # Using question as ID
            embeddings=[embedding],
            metadatas=[{"question": question, "answer": answer}]
        )

def search_memory(query, top_k=1):
    """Search for similar questions in memory."""
    query_embedding = get_embedding(query)
    if query_embedding:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        if results.get("metadatas") and results.get("distances"):
            best_match = results["metadatas"][0][0]  # Get top match
            score = results["distances"][0][0]  # Similarity score

            if score < 0.3:  # Lower score = more similar
                return best_match["answer"]
    
    return None  # No close match found




def chat_with_gemini(user_input):
    """Generate a response using Gemini or retrieve from memory."""
    memory_response = search_memory(user_input)

    if memory_response:
        return f"(💾 Memory) {memory_response}"  # Return saved response

    # If no match, ask Gemini
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite-001",
            contents=[{"role": "user", "content": user_input}]
        )
        ai_response = response.candidates[0].text
    except Exception as e:
        ai_response = "Sorry, I had trouble generating a response. Please try again."
        print(f"Gemini API Error: {e}")

    store_conversation(user_input, ai_response)  # Save new Q&A
    return f"(🤖 Gemini) {ai_response}"

# Chat loop
print("💬 AI Chatbot (Type 'exit' to quit)\n")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Goodbye! 👋")
        break
    response = chat_with_gemini(user_input)
    print(f"Bot: {response}\n")
