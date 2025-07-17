from langgraph.graph import StateGraph, MessagesState, START, END
from src import tools
from langgraph.prebuilt import create_react_agent
from .email_agent import email_fetch_agent, email_categorizer_agent, email_summarizer_agent
from .notification_agent import notification_agent
from ..services.agentic_supportive_tool import create_handoff_tool, make_pre_model_hook
from ..services.prompts import supervisor_system_prompt
from ..services.llm_models import gemini_flash_llm

assign_to_email_agent = create_handoff_tool(
    agent_name="email_fetch_agent",
    description="Assign task to a specialized email agent. email agent can fetch, categorize and summarize emails."
)

assign_to_notification_agent = create_handoff_tool(
    agent_name="notification_agent",
    description="Assign task to notification agent. Notification agent can send notifications to user."
)

supervisor_agent_premodel_hook = make_pre_model_hook(supervisor_system_prompt, "dhurv")

supervisor_agent = create_react_agent(
    model=gemini_flash_llm,
    prompt="You're an ai personal manager with the ability to decide wich agent to call. Your name is clair.",
    tools=[assign_to_email_agent, assign_to_notification_agent]+tools,
    name="supervisor",
    pre_model_hook=supervisor_agent_premodel_hook,
)

supervisor_graph = StateGraph(MessagesState)
supervisor_graph.add_node(supervisor_agent, destinations=["email_fetch_agent", "notification_agent", END])
supervisor_graph.add_node("email_fetch_agent", email_fetch_agent)
supervisor_graph.add_node("email_categorizer_agent", email_categorizer_agent)
supervisor_graph.add_node("email_summarizer_agent", email_summarizer_agent)
supervisor_graph.add_node("notification_agent", notification_agent)
supervisor_graph.add_edge(START, "supervisor")
supervisor_graph.add_edge("email_fetch_agent", "email_categorizer_agent")
supervisor_graph.add_edge("email_categorizer_agent", "email_summarizer_agent")
supervisor_graph.add_edge("email_summarizer_agent", "notification_agent")
supervisor_graph.add_edge("notification_agent", "supervisor")
supervisor = supervisor_graph.compile()
