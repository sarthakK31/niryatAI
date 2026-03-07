from ai_client.client.app import run_agent
from ai_client.memory.memory_service import retrieve_memory, store_conversation
from ai_client.memory.session_store import add_message, get_history
from ai_client.tools.image import vision_tool


def chat(user_id: str, message: str, media_type: str, image: str| None = None) -> str:

    # 1️⃣ retrieve session history
    history = get_history(user_id)

    # 1 retrieve memory
    memories = retrieve_memory(user_id, message)

    # 2 build context prompt
#     context_prompt = f"""
# Previous known information about this user:
# {memories}

# User message:
# {message}
# """
    context_prompt = f"""
Known long-term memory:
{memories}

Recent conversation:
{history}

User message:
{message}
"""


    if image:
        image_description = vision_tool(image)
        context_prompt = f"""
Known long-term memory:
{memories}

Recent conversation:
{history}

User message:
{message}
"""
    else:
        context_prompt = f"""
Known long-term memory:
{memories}

Recent conversation:
{history}

User message:
{message}

User Provided Image:
{image_description}
"""
    
    # messages = [{
    #         "role": "user",
    #         "content": [{"type": "text", "text": context_prompt}]
    #     }]

    # 3 run your existing agent
    response = run_agent(context_prompt)

    # 5️⃣ store session messages
    add_message(user_id, "user", message)
    add_message(user_id, "assistant", response)

    # 4 store memory
    store_conversation(user_id, message, response)

    return response