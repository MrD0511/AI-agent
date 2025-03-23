from mcp_client import MCPClient
import sys
import asyncio

async def main():
    # if len(sys.argv) < 2:
    #     print("Usage: python script.py <path_to_server_script>")
    #     sys.exit(1)

    client = MCPClient("Boris")
    try:
        await client.load_json_and_connect_servers()
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())