from src import tools
from langgraph.prebuilt import create_react_agent
from ..services.llm_models import gemini_flash_llm, openrouter_llm
from ..services.agentic_supportive_tool import make_pre_model_hook
from ..services.prompts import email_categorizer_agent_prompt, email_fetch_agent_prompt, email_summarizer_agent_prompt

email_fetch_agent_premodel_hook = make_pre_model_hook(email_fetch_agent_prompt, "dhurv")

#Email fetcher Agent
email_fetch_agent = create_react_agent(
    model=gemini_flash_llm,
    prompt=email_fetch_agent_prompt,
    tools=tools,
    pre_model_hook=email_fetch_agent_premodel_hook,
    name="email_fetcher_agent"
)


email_categorizer_agent_premodel_hook = make_pre_model_hook(email_categorizer_agent_prompt, "dhruv")

email_categorizer_agent = create_react_agent(
    model=openrouter_llm,
    prompt=email_categorizer_agent_prompt,
    pre_model_hook=email_categorizer_agent_premodel_hook,
    name="email_categorizer_agent",
    tools=[]
)

email_summarizer_agent_premodel_hook = make_pre_model_hook(email_summarizer_agent_prompt, "dhruv")


email_summarizer_agent = create_react_agent(
    model=gemini_flash_llm,
    prompt=email_summarizer_agent_prompt,
    tools=tools,
    pre_model_hook=email_summarizer_agent_premodel_hook,
    name="email_summarizer_agent"
)

