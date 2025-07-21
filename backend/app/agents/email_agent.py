from app.tools import tools
from app.tools import fetch_email, mark_email_as_read
from langgraph.prebuilt import create_react_agent
from app.services import get_gemini_model, openrouter_deepseek_model
from app.services import make_pre_model_hook, make_post_model_hook
from app.services import email_fetch_agent_prompt, email_summarizer_agent_prompt, email_mark_as_read_agent_prompt
from langgraph.graph import MessagesState
from mem0 import MemoryClient
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_postgres import PostgresChatMessageHistory


def create_email_fetch_agent(chat_history: PostgresChatMessageHistory):
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


def create_email_categorizer_agent(chat_history: PostgresChatMessageHistory, mem0: MemoryClient, prompt: str, mem0_user_id: str = ""):

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
            # chat_history.add_message(state['messages'][-1])

            return {"messages": [response]}
        except Exception as e:
            print("email_categorizer_agent: ", e)
            return e

    return email_categorizer_agent


def create_email_summarizer_agent(chat_history: PostgresChatMessageHistory):
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


def create_email_mark_as_read_agent(chat_history: PostgresChatMessageHistory):

    email_mark_as_read_agent_premodel_hook = make_pre_model_hook(email_mark_as_read_agent_prompt)
    email_mark_as_read_agent_postmodel_hook = make_post_model_hook(chat_history=chat_history)

    email_mark_as_read_agent = create_react_agent(
        model=get_gemini_model("gemini-2.0-flash-lite-001"),
        prompt=email_mark_as_read_agent_prompt,
        pre_model_hook=email_mark_as_read_agent_premodel_hook,
        post_model_hook=email_mark_as_read_agent_postmodel_hook,
        tools=[mark_email_as_read],
        name="email_mark_as_read_agent"
    )

    return email_mark_as_read_agent