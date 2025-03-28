from openai import OpenAI
from mem0 import Memory
import os

openai_client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1",
)

os.environ["GEMINI_API_KEY"] = "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"

config = {
    "llm": {
        "provider": "litellm",
        "config": {
            "model": "google/gemini-2.0-flash-lite-001",
            "temperature": 0.2,
            "max_tokens": 1500,
        }
    }
}
m = Memory.from_config(config)

def chat_with_memories(message: str, user_id: str = "default_user") -> str:
    # Retrieve relevant memories
    relevant_memories = memory.search(query=message, user_id=user_id, limit=3)
    memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])
    
    # Generate Assistant response
    system_prompt = f"You are a helpful AI. Answer the question based on query and memories.\nUser Memories:\n{memories_str}"
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]
    response = openai_client.chat.completions.create(model="google/gemini-2.0-flash-lite-001", messages=messages)
    assistant_response = response.choices[0].message.content

    # Create new memories from the conversation
    messages.append({"role": "assistant", "content": assistant_response})
    memory.add(messages, user_id=user_id)

    return assistant_response

def main():
    print("Chat with AI (type 'exit' to quit)")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        print(f"AI: {chat_with_memories(user_input)}")

if __name__ == "__main__":
    main()