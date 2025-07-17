from mem0 import MemoryClient
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import Command
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage
from mem0 import MemoryClient
from langchain_core.messages import HumanMessage
from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState


mem0 = MemoryClient(api_key="m0-rpn5Y0pv2TehopJVH8V7fX4DieymDBfgb4MmaqQr")


def make_pre_model_hook(system_prompt: str, mem0_user_id: str):
    def premodel_hook(state):
        # get last user message
        last_message = state['messages'][-1]
        context=""
        if(type(last_message) == HumanMessage):
            memories = mem0.search(last_message.content, user_id=mem0_user_id)
            context = "\n".join(f"- {m['memory']}" for m in memories)

        system_message = SystemMessage(content=f"{system_prompt}\nContext memories:\n{context}") 
        # Return new llm_input_messages to use as input to LLM
        return {
            "llm_input_messages": [system_message]+state['messages']
        }
    return premodel_hook


def create_handoff_tool(*, agent_name: str, description: str | None = None):
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
            update={**state, "messages": state["messages"] + [tool_message]},  
            graph=Command.PARENT,  
        )

    return handoff_tool

