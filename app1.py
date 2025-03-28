from src import Server, Chat_session
import asyncio
import json

chat_session = None

async def main():

    global chat_session

    with open("./mcp_servers.json", "r") as f:
        server_config = json.load(f)
    
    servers = []
    for name, srv_config in server_config["mcpServers"].items():
        new_server =  Server(srv_config)
        servers.append(new_server)
        await new_server.initialize_connection()
    
    chat_session = Chat_session(servers)
    
    await chat_session.chat_loop()
    
if __name__ == "__main__":
    asyncio.run(main())