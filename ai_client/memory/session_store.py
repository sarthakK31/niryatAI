from collections import defaultdict

sessions = defaultdict(list)


def add_message(user_id, role, content):
    sessions[user_id].append({
        "role": role,
        "content": content
    })


def get_history(user_id):
    return sessions[user_id][-10:]