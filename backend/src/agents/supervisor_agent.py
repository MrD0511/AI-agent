from langgraph.graph import StateGraph, MessagesState, START, END
from ..tools.tools import tools
from langgraph.prebuilt import create_react_agent
from .email_agent import create_email_fetch_agent, create_email_categorizer_agent, create_email_summarizer_agent
from .notification_agent import create_notification_agent
from .event_schedular_agent import create_event_schedular_agent
from ..services.agentic_supportive_tool import create_handoff_tool, make_pre_model_hook, make_post_model_hook, mem0
from ..services.prompts import supervisor_system_prompt, email_categorizer_agent_prompt
from ..services.llm_models import get_gemini_model
from langgraph.checkpoint.memory import MemorySaver


def create_agentic_workflow(chat_history: list):

    memory = MemorySaver()
    
    assign_to_email_agent = create_handoff_tool(
        agent_name="email_fetch_agent",
        description="Assign task to a specialized email agent. email agent can fetch, categorize and summarize emails."
    )

    assign_to_notification_agent = create_handoff_tool(
        agent_name="notification_agent",
        description="Assign task to notification agent. Notification agent can send notifications to user."
    )

    assign_to_event_schedular_agent = create_handoff_tool(
        agent_name="event_schedular_agent",
        description="Assign task to event_schedular_agent. Event schedular agent can schedule user's events."
    )

    supervisor_agent_premodel_hook = make_pre_model_hook(supervisor_system_prompt, "dhruv")
    supervisor_agent_postmodel_hook = make_post_model_hook(chat_history=chat_history, mem0_user_id="dhruv")

    supervisor_agent = create_react_agent(
        model=get_gemini_model("gemini-2.0-flash-001"),
        prompt=supervisor_system_prompt,
        tools=[assign_to_email_agent, assign_to_notification_agent, assign_to_event_schedular_agent]+tools,
        name="supervisor",
        pre_model_hook=supervisor_agent_premodel_hook,
        post_model_hook=supervisor_agent_postmodel_hook
    )

    supervisor_graph = StateGraph(MessagesState)
    supervisor_graph.add_node(supervisor_agent, destinations=["email_fetch_agent", "notification_agent", "event_schedular_agent", END])
    supervisor_graph.add_node("email_fetch_agent", create_email_fetch_agent(chat_history))
    supervisor_graph.add_node("email_categorizer_agent", create_email_categorizer_agent(chat_history, mem0=mem0, prompt=email_categorizer_agent_prompt))
    supervisor_graph.add_node("email_summarizer_agent", create_email_summarizer_agent(chat_history))
    supervisor_graph.add_node("notification_agent", create_notification_agent(chat_history))
    supervisor_graph.add_node("event_schedular_agent", create_event_schedular_agent(chat_history))
    supervisor_graph.add_edge(START, "supervisor")
    supervisor_graph.add_edge("email_fetch_agent", "email_categorizer_agent")
    supervisor_graph.add_edge("email_categorizer_agent", "email_summarizer_agent")
    supervisor_graph.add_edge("email_summarizer_agent", "notification_agent")
    supervisor_graph.add_edge("email_summarizer_agent", "event_schedular_agent")
    supervisor_graph.add_edge("notification_agent", "supervisor")
    supervisor_graph.add_edge("event_schedular_agent", "supervisor")
    supervisor = supervisor_graph.compile(checkpointer=memory)

    return supervisor
