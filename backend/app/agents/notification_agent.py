from app.tools.tools import send_notification, create_reminder_tool, get_upcoming_reminders_tool
from langgraph.prebuilt import create_react_agent
from ..services.agentic_supportive_tool import make_pre_model_hook, make_post_model_hook
from ..services.llm_models import get_gemini_model
from ..services.prompts import notification_agent_prompt
from langchain_postgres import PostgresChatMessageHistory


def create_notification_agent(chat_history: PostgresChatMessageHistory):
    notification_agent_premodel_hook = make_pre_model_hook(notification_agent_prompt)
    notification_agent_postmodel_hook = make_post_model_hook(chat_history)

    notification_agent = create_react_agent(
        model=get_gemini_model("gemini-2.0-flash-001"),
        prompt=notification_agent_prompt,
        tools=[send_notification, create_reminder_tool, get_upcoming_reminders_tool],
        pre_model_hook=notification_agent_premodel_hook,
        name="notification_agent",
        post_model_hook=notification_agent_postmodel_hook
    )

    return notification_agent