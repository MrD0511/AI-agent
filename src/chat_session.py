from openai import OpenAI
from contextlib import AsyncExitStack
import json
import traceback


class Chat_session:
    def __init__(self, servers):
        self.servers = servers
        self.exit_stack = AsyncExitStack()
        self.openai = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )
        
        self.chat_history = []
        self.chat_history.append({
            "role": "system",
            "content": """
                You are Clair. You are a personalised AI assistent.

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

            return "\n".join(final_text)
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

