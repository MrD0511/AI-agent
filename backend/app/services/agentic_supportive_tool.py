from mem0 import MemoryClient
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.types import Command
from langgraph.graph import MessagesState
from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
import threading
from config import settings
from langchain_postgres import PostgresChatMessageHistory


# Initialize Mem0 client with environment variable
mem0_api_key = settings.mem0_api_key

if not mem0_api_key:
    raise ValueError("MEM0_API_KEY not found in environment variables")

mem0 = MemoryClient(api_key=mem0_api_key)


def make_pre_model_hook(system_prompt: str, mem0_user_id: str = ""):
    def premodel_hook(state):
        # get last user message
        last_message = state['messages'][-1]
        context=""
        if mem0_user_id != "":
            if(type(last_message) == HumanMessage):
                memories = mem0.search(last_message.content, user_id=mem0_user_id)
                context = "\n".join(f"- {m['memory']}" for m in memories)
                mem0.add([
                    {"role": "user", "content": last_message.content}
                    ], user_id=mem0_user_id)

        system_message = SystemMessage(content=f"{system_prompt}\nContext memories:\n{context}") 

        return {
            "llm_input_messages": [system_message]+state['messages']
        }
    return premodel_hook


def create_handoff_tool(*, agent_name: str, description: str | None = None, task: str = ""):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        state: Annotated[MessagesState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }

        return Command(
            goto=agent_name,  
            update={**state, "messages": state["messages"] + [tool_message], "task": task},  
            graph=Command.PARENT,  
        )

    return handoff_tool


def make_post_model_hook(chat_history: PostgresChatMessageHistory, mem0_user_id: str = ""):
    def post_model_hook(state: MessagesState):
        last_message = state['messages'][-1]

        if len(last_message.additional_kwargs) == 0:
            if mem0_user_id != "" and type(last_message) == AIMessage and last_message.content != "":
                threading.Thread(
                    target=mem0.add,
                    args=([{"role": "assistant", "content": last_message.content}],),
                    kwargs={"user_id": mem0_user_id},
                    daemon=True
                ).start()
        # chat_history.add_message(state['messages'][-1])

        return state

    return post_model_hook