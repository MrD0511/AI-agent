from langgraph.graph import StateGraph, MessagesState, START, END
from .email_agent import create_email_fetch_agent, create_email_categorizer_agent, create_email_summarizer_agent, create_email_mark_as_read_agent
from .notification_agent import create_notification_agent
from .event_schedular_agent import create_event_schedular_agent 
from ..services.agentic_supportive_tool import mem0
from ..services.prompts import email_categorizer_agent_prompt
from langgraph.checkpoint.memory import MemorySaver
from langchain_postgres import PostgresChatMessageHistory


def create_background_email_agent(chat_history: PostgresChatMessageHistory):

    memory = MemorySaver()

    email_fetch_agent = create_email_fetch_agent(chat_history=chat_history)
    email_categorizer_agent = create_email_categorizer_agent(chat_history=chat_history, mem0=mem0, prompt=email_categorizer_agent_prompt, mem0_user_id="dhruv")
    email_summarizer_agent = create_email_summarizer_agent(chat_history=chat_history)
    notification_agent = create_notification_agent(chat_history=chat_history)
    event_schedular_agent = create_event_schedular_agent(chat_history)
    email_mark_as_read_agent = create_email_mark_as_read_agent(chat_history)

    background_agent_graph = StateGraph(MessagesState)

    background_agent_graph.add_node("email_fetch_agent", email_fetch_agent)
    background_agent_graph.add_node("email_categorizer_agent", email_categorizer_agent)
    background_agent_graph.add_node("email_summarizer_agent", email_summarizer_agent)
    background_agent_graph.add_node("notification_agent", notification_agent)
    background_agent_graph.add_node("event_schedular_agent", event_schedular_agent)
    background_agent_graph.add_node("email_mark_as_read_agent", email_mark_as_read_agent)

    background_agent_graph.add_edge(START, "email_fetch_agent")
    background_agent_graph.add_edge("email_fetch_agent", "email_categorizer_agent")
    background_agent_graph.add_edge("email_categorizer_agent", "email_summarizer_agent")
    background_agent_graph.add_edge("email_summarizer_agent", "notification_agent")
    background_agent_graph.add_edge("email_summarizer_agent", "event_schedular_agent")
    background_agent_graph.add_edge("notification_agent", "email_mark_as_read_agent")
    background_agent_graph.add_edge("event_schedular_agent", "email_mark_as_read_agent")
    background_agent_graph.add_edge("email_mark_as_read_agent", END)
    
    background_agent = background_agent_graph.compile(checkpointer=memory)

    return background_agent
