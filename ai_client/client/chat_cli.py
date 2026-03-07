from ai_client.client.chat_agent import chat

user_id = "sarthak"

while True:

    msg = input("You: ")

    if msg == "exit":
        break

    response = chat(user_id, msg)

    print("AI:", response)