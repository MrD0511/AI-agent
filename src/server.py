from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import traceback
import shutil

class Server:
    def __init__(self, server_conf: dict):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.conf = server_conf

    async def initialize_connection(self):
        try:

            command = (
                shutil.which("npx")
                if self.conf["command"] == "npx"
                else self.conf["command"]
            )

            server_params = StdioServerParameters(
                command=command,
                args=self.conf['args'],
                env=self.conf['env'] if self.conf.get('env') else {}
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

    async def list_tools(self) -> list[any]:
        response = await self.session.list_tools()
        available_tools = [ tool.name for tool in response.tools ]

        return available_tools
