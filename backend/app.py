from langchain_core.messages import HumanMessage
from src.pretty_printing import pretty_print_messages
from src.agents import create_agentic_workflow
from src.services.agentic_supportive_tool import mem0
from src.db import engine
from src.db.models import Base

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created!")

def run_chat():
    chat_history = []

    agent = create_agentic_workflow(chat_history)
    config = {"configurable": {"thread_id": "1"}}

    try:
        with open('graph_new.png', 'wb') as f:
            f.write(agent.get_graph().draw_mermaid_png())
        print("Image saved as graph.png")
    except Exception as e:
        # This requires some extra dependencies and is optional
        print("execprtion display", e.with_traceback(None))
        pass

    # 🗣 CLI loop

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print(chat_history)
            chat = []

            
            break
        chat_history.append(HumanMessage(content=user_input))

        for chunk in agent.stream({"messages": chat_history}, config):
            pretty_print_messages(chunk)

if __name__ == "__main__":
    init_db()
    run_chat()
