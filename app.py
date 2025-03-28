from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
import uvicorn
from src import Server, Chat_session
import asyncio
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains. Replace with specific domains if needed.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


chat_session = []

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

class QueryModel(BaseModel):
    query: str

# API to process user queries via ChatSession
@app.post("/chat")
async def process_chat(query_data: QueryModel):
    
    if chat_session is None:
        return {"error": "Chat session not initialized yet"}
    
    response = await chat_session.process_web_query(query_data.query)
    return response

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

    config = uvicorn.Config(app, host="127.0.0.1", port=8000)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())