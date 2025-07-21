from app.tools.tools import  create_event_tool, create_reminder_tool, get_upcoming_reminders, get_upcoming_events_tool, get_ongoing_events_tool
from langgraph.prebuilt import create_react_agent
from app.services import make_pre_model_hook, make_post_model_hook
from app.services import get_gemini_model
from app.services import event_schedular_agent_prompt
from langchain_postgres import PostgresChatMessageHistory


def create_event_schedular_agent(chat_history: PostgresChatMessageHistory):
    """Creates an event schedular agent.
    """
    event_schedular_agent_premodel_hook = make_pre_model_hook(event_schedular_agent_prompt, "dhruv")
    event_schedular_agent_postmodel_hook = make_post_model_hook(chat_history)

    event_schedular_agent = create_react_agent(
        model=get_gemini_model("gemini-2.0-flash-001"),
        prompt=event_schedular_agent_prompt,
        tools=[create_event_tool, create_reminder_tool, get_upcoming_reminders, get_upcoming_events_tool, get_ongoing_events_tool],
        pre_model_hook=event_schedular_agent_premodel_hook,
        post_model_hook=event_schedular_agent_postmodel_hook,
        name="event_schedular_agent"
    )

    return event_schedular_agent