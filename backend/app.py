from langchain_core.messages import HumanMessage
from src import pretty_print_messages
from src.agents import supervisor

try:
    with open('graph_new.png', 'wb') as f:
        f.write(supervisor.get_graph().draw_mermaid_png())
    print("Image saved as graph.png")
except Exception as e:
    # This requires some extra dependencies and is optional
    print("execprtion display", e.with_traceback(None))
    pass

# 🗣 CLI loop

chat_history = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        break
    chat_history.append(HumanMessage(content=user_input))

    for chunk in supervisor.stream({"messages": chat_history}):
        pretty_print_messages(chunk)