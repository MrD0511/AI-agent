from openai import OpenAI
from contextlib import AsyncExitStack
import json
import traceback
from datetime import datetime
import chromadb
from google import genai
from mem0 import MemoryClient

user_id = "dhruv"

client = genai.Client(api_key="AIzaSyAB6po8ng-NXb651W0dkQx1tXOtf3KyN0o")


chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="assistant_memory")


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


def search_memory(query, top_k=1):
    """Search for similar questions in memory."""
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    print(results)
    # Check if results exist before accessing
    if results and "metadatas" in results and results["metadatas"] and results["metadatas"][0]:
        best_match = results["metadatas"][0][0]  # Get top match
        score = results["distances"][0][0]  # Similarity score
        if score < 0.5:  # Lower score = more similar
            return best_match["answer"]
    
    return None  # No close match found


def store_conversation(question, answer):
    """Store question-answer pairs in ChromaDB."""
    embedding = get_embedding(question)

    print(f"✅ Storing: {question} -> {answer}")  # Debugging
    if embedding:
        collection.add(
            ids=[question],  # Using question as ID
            embeddings=[embedding],
            metadatas=[{"question": question, "answer": answer}]
        )


class Chat_session:
    def __init__(self, servers):
        self.servers = servers
        self.exit_stack = AsyncExitStack()
        self.openai = OpenAI(
            api_key="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",
            base_url="https://openrouter.ai/api/v1",
        )
        self.mem = MemoryClient(api_key="m0-rpn5Y0pv2TehopJVH8V7fX4DieymDBfgb4MmaqQr")
        self.user_id = "dhruv"
        
        self.chat_history = []
        self.chat_history.append({
            "role": "system",
            "content": """
                You are Clair a funny, sarcastic AI personal manager.
                Your basic task is to manage schedules and manage my emails.

                User's information:
                Name: Dhruv Sharma
                Location: Vadodara, Gujarat
                Profession: Student and a Developer
                College: SVIT VASAD, Anand

                "After receiving a tool's response:\n"
                "1. Transform the raw data into a natural, conversational response\n"
                "2. Keep responses concise but informative\n"
                "3. Focus on the most relevant information\n"
                "4. Use appropriate context from the user's question\n"
                "5. Avoid simply repeating the raw data\n\n"
            """
        })
        
    async def process_query(self, query: str) -> str:
        try:
            memory = self.mem.search(query=query, user_id=user_id, top_k=2)
            memories = []

            for mem1 in memory:
                memories.append(mem1['memory'])

            self.chat_history.append({"role": "system", "content": ", ".join(memories)})
            self.chat_history.append({"role": "user", "content": query})

            available_tools = []
            for server in self.servers:
                response = await server.session.list_tools()
                available_tools.extend([
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                "type": tool.inputSchema['type'],
                                "properties": tool.inputSchema['properties'],
                            },
                        },
                    } for tool in response.tools
                ])


            request_1 = {
                "model": "google/gemini-2.0-flash-lite-001",
                "tools": available_tools,
                "messages": self.chat_history,
            }

            response = self.openai.chat.completions.create(**request_1)

            self.chat_history.append(response.choices[0].message)

            final_text = []
            if response.choices[0].message.content:
                final_text.append(response.choices[0].message.content)
            elif response.choices[0].message.tool_calls:
                
                tool_calls = response.choices[0].message.tool_calls
                
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    for server in self.servers:
                        tools = await server.list_tools()

                        if any(tool == tool_name for tool in tools):
                            result = await server.session.call_tool(tool_name, tool_args)
                            
                            final_text.append(f"[🔧 Calling tool {tool_name} with args {tool_args}]\n")
                    
                    final_result = []   
                    for content in result.content:
                        final_result.append(content.text)

                    self.chat_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(final_result)
                    })
                    
                request_2 = {
                    "model": "google/gemini-2.0-flash-lite-001",
                    "messages": self.chat_history,
                }
                response2 = self.openai.chat.completions.create(**request_2)
                final_text.append(response2.choices[0].message.content)


            msgs = [
                    {"role": "user", "content": query},
                    {"role": "assistant", "content": ", ".join(final_text)}
                    ]
            
            self.mem.add(msgs, user_id=user_id)

            return "\n".join(final_text)
        except Exception as e:
            print(f"\n❌ Error while processing query: {str(e)}")
            traceback.print_exc()
            return "An error occurred while processing your request."

    async def process_web_query(self, query: str):
        try:
            memory = self.mem.search(query=query, user_id=user_id, top_k=2)
            memories = []

            for mem1 in memory:
                memories.append(mem1['memory'])

            self.chat_history.append({"role": "system", "content": ", ".join(memories)})
            self.chat_history.append({"role": "user", "content": query})

            available_tools = []
            for server in self.servers:
                response = await server.session.list_tools()
                available_tools.extend([
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                "type": tool.inputSchema['type'],
                                "properties": tool.inputSchema['properties'],
                            },
                        },
                    } for tool in response.tools
                ])

            request_1 = {
                "model": "google/gemini-2.0-flash-lite-001",
                "tools": available_tools,
                "messages": self.chat_history,

            }

            response = self.openai.chat.completions.create(**request_1)

            self.chat_history.append(response.choices[0].message)
            
            final_text = []
            function_calls = []
            if response.choices[0].message.content:
                final_text.append(response.choices[0].message.content)
            elif response.choices[0].message.tool_calls:
                
                tool_calls = response.choices[0].message.tool_calls
                
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
    
                    for server in self.servers:
                        tools = await server.list_tools()

                        if any(tool == tool_name for tool in tools):
                            result = await server.session.call_tool(tool_name, tool_args)
                            
                            # final_text.append(f"[🔧 Calling tool {tool_name} with args {tool_args}]\n")
                            
                    final_result = []   
                    for content in result.content:
                        final_result.append(content.text)

                    function_calls.append({
                        "name": tool_name,
                        "arguments": tool_args,
                        "result":  final_result
                    })

                    self.chat_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(final_result)
                    })
                    
                request_2 = {
                    "model": "google/gemini-2.0-flash-lite-001",
                    "messages": self.chat_history,
                }
                response2 = self.openai.chat.completions.create(**request_2)
                final_text.append(response2.choices[0].message.content)

            # self.mem.add([{"role": "user", "content": query},
            #     {"role": "assistant", "content": "\n".join(final_text)}], user_id=user_id)
            
            return {
                "id": str(datetime.now()),
                "role": "bot",
                "content": "\n".join(final_text),
                "functionCalls": function_calls
            }
        
        except Exception as e:
            print(f"\n❌ Error while processing query: {str(e)}")
            traceback.print_exc()
            return "An error occurred while processing your request."
    
    async def chat_loop(self):
        print("\n🎤 Welcome to MCP Client Chat!")
        print("💡 Type your queries below. Type 'exit' to quit.")
        
        while True:
            try:
                query = input("\n📝 You: ").strip()
                if query.lower() in ['quit', 'exit']:
                    print("\n👋 Exiting chat. Goodbye!")
                    break
                
                response = await self.process_query(query)
                print(f"\n🤖 Bot: {response}")
            except Exception as e:
                print(f"\n❌ Error in chat loop: {str(e)}")
                traceback.print_exc()

    async def cleanup(self):
        try:
            await self.exit_stack.aclose()
        except Exception as e:
            print(f"\n❌ Error during cleanup: {str(e)}")
            traceback.print_exc()

