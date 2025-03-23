import asyncio
import sys
from openai import OpenAI
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
import traceback

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )
        self.chat_history = []

    async def connect_with_server(self, server_script_path: str):
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")

        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
        
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        self.chat_history.append({
                "role": "user",
                "content": query  # Fix: Pass actual query here
            })
        
        response = await self.session.list_tools()
        available_tools = [{
            "type" : "function",
            "function" : {
                "name": tool.name,
                "description" : tool.description,
                "parameters": {
                    "type" : tool.inputSchema['type'],
                    "properties" : tool.inputSchema['properties'],
                    # "required" : tool.inputSchema['required']
                },
            }
        } for tool in response.tools]


        request_1 = {
            "model": "google/gemini-2.0-flash-lite-001",
            "tools": available_tools,
            "messages": self.chat_history
        }

        response = self.openai.chat.completions.create(**request_1)  # Fix: Use await

        self.chat_history.append(response.choices[0].message)

        final_text = []
        if response.choices[0].message.content:
            final_text.append(response.choices[0].message.content)
        elif response.choices[0].message.tool_calls:
            
            tool_calls = response.choices[0].message.tool_calls

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)  # Parse arguments

                # Call the tool asynchronously
                result = await self.session.call_tool(tool_name, tool_args)

                # Append tool call log
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # Update chat_history for next interaction
                
                self.chat_history.append({
                    "role" : "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": { "type":"text", "text" : str(result.content[0].text) },
                })
                
            # Send updated chat_history to Claude for final response
            request_2 = {
                "model": "google/gemini-2.0-flash-lite-001",
                "messages": self.chat_history
            }

            response2 = self.openai.chat.completions.create(**request_2)  # Fix: Use await

            final_text.append(response2.choices[0].message.content)


        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")
                traceback.print_exc()

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_with_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
