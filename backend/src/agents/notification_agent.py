from src.tools.tools import send_notification
from langgraph.prebuilt import create_react_agent
from ..services.agentic_supportive_tool import make_pre_model_hook
from ..services.llm_models import gemini_flash_llm
from ..services.prompts import notification_agent_prompt

notification_agent_premodel_hook = make_pre_model_hook(notification_agent_prompt, "dhruv")

notification_agent = create_react_agent(
    model=gemini_flash_llm,
    prompt=notification_agent_prompt,
    tools=[send_notification],
    pre_model_hook=notification_agent_premodel_hook,
    name="notification_agent"
)