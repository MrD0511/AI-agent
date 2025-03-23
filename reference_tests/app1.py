import asyncio
import sys
from openai import OpenAI
from typing import Optional
from contextlib import AsyncExitStack
import json

openai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

chat_history = []

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'get_forecast',
            'description': 'Get weather forecast for a city.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'city': {
                        'title': 'City',
                        'type': 'string'
                    }
                }
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'clone_github_repo',
            'description': '',
            'parameters': {
                'type': 'object',
                'properties': {
                    'username': {
                        'title': 'Username',
                        'type': 'string'
                    },
                    'repo_name': {
                        'title': 'Repo Name',
                        'type': 'string'
                    },
                    'destination': {
                        'title': 'Destination',
                        'type': 'string'
                    }
                }
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'open_vs_code',
            'description': 'Opens Visual Studio Code in the given directory.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'dest': {
                        'title': 'Dest',
                        'type': 'string'
                    }
                }
            }
        }
    }
]

chat_history.append({
    "role": "system",
    "content": "Your name is Clair. You are a personal manager."
})

chat_history.append({
    "role": "user",
    "content": "Who are you?"
})

chat_history.append({
    "role": "assistant",
    "content": "Hi there! I'm Clair, your personal manager. I'm here to help you with a variety of tasks think of me as your go-to assistant. Tell me what you need, and I'll do my best to help!",
    "tool_calls": []
})

chat_history.append({
    "role": "user",
    "content": "What can you help me with?"
})

chat_history.append({
    "role": "assistant",
    "content": "I can assist you with a variety of tasks, including: * Providing weather forecasts for a specific city. * Cloning GitHub repositories.* Opening Visual Studio Code in a specific directory. Just let me know what you need help with!",
    "tool_calls": []
})

chat_history.append({
    "role": "user",
    "content": "Open VS Code at C:/Users/DELL/Documents/Projects."
})

chat_history.append({
    "role": "assistant",
    "content": "I will now open VS Code in the specified directory.",
    "tool_calls": [
        {
          "id": "tool_2_open_vs_code",
          "function": {
            "name": "open_vs_code",
            "arguments": '{ "dest" : "C:/Users/DELL/Documents/Projects"}'
          },
          "type": "function",
          "index": 0
        }
    ]
})

chat_history.append({
    "role": "tool",
    "tool_call_id": "tool_2_open_vs_code",
    "name": "open_vs_code",
    "content": {
        "result": "Vs code opened successfully"
    }
})

print(chat_history)

request_1 = {
    "model": "google/gemini-2.0-flash-lite-001",
    "messages": chat_history,
    "tools": tools
}

response = openai.chat.completions.create(**request_1)

print(response)
if response.choices:
    print(response.choices[0].message.content)
else:
    print(response)