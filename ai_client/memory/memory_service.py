from ai_client.memory.memory_client import memory_client


def store_conversation(user_id, user_message, assistant_response):
    
    messages = [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_response}
    ]

    memory_client.add(messages, user_id=user_id)


def retrieve_memory(user_id, query):

    filters = {
        "OR": [
            {"user_id": user_id}
        ]
    }

    results = memory_client.search(
        query=query,
        version="v2",
        filters=filters
    )

    return results