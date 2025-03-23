from openai import OpenAI
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
import traceback
import shutil

class MCPClient:
    def __init__(self, name: str):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )
        
        self.chat_history = []
        self.chat_history.append({
            "role": "system",
            "content": f"""
                You are {name}. A personal general manager.

            """
        })

    async def load_json_and_connect_servers(self):
        try:
            data = ""
            with open("./mcp_servers.json", "r") as f:
                data = json.load(f)

            print(type(data))
            
            for server in data['mcpServers'].values():

                command = (
                    shutil.which("npx")
                    if server["command"] == "npx"
                    else server["command"]
                )

                server_params = StdioServerParameters(
                    command=command,
                    args=server['args'],
                    env=server['env'] if server.get('env') else {}
                )
                
                stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
                self.stdio, self.write = stdio_transport
                self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

                await self.session.initialize()

                response = await self.session.list_tools()
                tools = response.tools
                print("\n✅ Connected to server! Available tools:")
                for tool in tools:
                    print(f" - {tool.name}: {tool.description}")

        except Exception as e:
            print(f"\n❌ Error while connecting to server: {str(e)}")
            traceback.print_exc()
            

    async def connect_with_server(self, server_script_path: str):
        try:
            is_python = server_script_path.endswith(".py")
            is_js = server_script_path.endswith(".js")
            is_ts = server_script_path.endswith(".ts")

            if not (is_python or is_js or is_ts):
                raise ValueError("Server script must be a .py or .js file")
            
            command = "python" if is_python else "node" if is_js else "npx"
            server_params = StdioServerParameters(
                command=command,
                args=[server_script_path],
                env={"MEMORY_FILE_PATH": "C:/Users/DELL/Documents/Projects/mcp_test/servers/src/memory/memory.json"}
            )

            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

            await self.session.initialize()

            response = await self.session.list_tools()
            tools = response.tools

            print("\n✅ Connected to server! Available tools:")
            for tool in tools:
                print(f" - {tool.name}: {tool.description}")
                
        except Exception as e:
            print(f"\n❌ Error while connecting to server: {str(e)}")
            traceback.print_exc()

    async def connect_with_server_using_details(self, command : str, args: list):
        try:
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=None
            )

            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

            await self.session.initialize()

            response = await self.session.list_tools()
            tools = response.tools
            print("\n✅ Connected to server! Available tools:")
            for tool in tools:
                print(f" - {tool.name}: {tool.description}")
        except Exception as e:
            print(f"\n❌ Error while connecting to server using details: {str(e)}")
            traceback.print_exc()


    async def process_query(self, query: str) -> str:
        try:
            self.chat_history.append({"role": "user", "content": query})
            
            response = await self.session.list_tools()
            available_tools = [
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
            ]

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
                    result = await self.session.call_tool(tool_name, tool_args)
                    final_text.append(f"[🔧 Calling tool {tool_name} with args {tool_args}]\n")
                    
                    print(result)

                    self.chat_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        # "content": {"type": "text", "text": str(result.content[0].text)},
                        # "content": {"status": "success", "result": str(result.content[0].text)}
                        "content": str(result.content[0].text)
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
