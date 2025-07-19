from src import tools
from src.tools.tools import fetch_email
from langgraph.prebuilt import create_react_agent
from ..services.llm_models import get_gemini_model, get_openrouter_model, openrouter_deepseek_model
from ..services.agentic_supportive_tool import make_pre_model_hook, make_post_model_hook
from ..services.prompts import email_categorizer_agent_prompt, email_fetch_agent_prompt, email_summarizer_agent_prompt
from langgraph.graph import MessagesState
from mem0 import MemoryClient
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


def create_email_fetch_agent(chat_history: list):
    email_fetch_agent_premodel_hook = make_pre_model_hook(email_fetch_agent_prompt)
    email_fetch_agent_postmodel_hook = make_post_model_hook(chat_history)
    #Email fetcher Agent
    email_fetch_agent = create_react_agent(
        model=get_gemini_model("gemini-2.0-flash-lite-001"),
        prompt=email_fetch_agent_prompt,
        tools=tools,
        pre_model_hook=email_fetch_agent_premodel_hook,
        name="email_fetcher_agent",
        post_model_hook=email_fetch_agent_postmodel_hook
    )

    return email_fetch_agent


def create_email_categorizer_agent(chat_history: list, mem0: MemoryClient, prompt: str, mem0_user_id: str = ""):

    def email_categorizer_agent(state: MessagesState):
        try:
            last_message = state["messages"][-1]
            context=""
            if mem0_user_id != "":
                if(type(last_message) == HumanMessage):
                    memories = mem0.search(last_message.content, user_id=mem0_user_id)
                    context = "\n".join(f"- {m['memory']}" for m in memories)
                    mem0.add([
                        {"role": "user", "content": last_message.content}
                        ], user_id=mem0_user_id)

            system_message = SystemMessage(content=f"{prompt}\nContext memories:\n{context}") 
            full_message = [system_message]+state['messages']

            response = openrouter_deepseek_model.invoke(full_message)

            if len(response.additional_kwargs) == 0:
                if mem0_user_id != "" and type(response) == AIMessage and response.content != "":
                    mem0.add([
                        {"role": "assistant", "content": response.content}
                        ], user_id=mem0_user_id)
                # chat_history.append(state['messages'][-1])

            return {"messages": [response]}
        except Exception as e:
            print("email_categorizer_agent: ", e)
            return e


    return email_categorizer_agent


def create_email_summarizer_agent(chat_history: list):
    email_summarizer_agent_premodel_hook = make_pre_model_hook(email_summarizer_agent_prompt)
    email_summarizer_agent_postmodel_hook = make_post_model_hook(chat_history, "dhurv")

    email_summarizer_agent = create_react_agent(
        model=get_gemini_model("gemini-2.0-flash-001"),
        prompt=email_summarizer_agent_prompt,
        tools=[fetch_email],
        pre_model_hook=email_summarizer_agent_premodel_hook,
        name="email_summarizer_agent",
        post_model_hook=email_summarizer_agent_postmodel_hook
    )

    return email_summarizer_agent

