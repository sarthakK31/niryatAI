from strands import tool

@tool
def vision_tool(image_base64: str, prompt: str = "Describe the image"):
    import requests

    r = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "qwen2.5vl:3b",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "image": image_base64}
                    ]
                }
            ]
        }
    )

    return r.json()["message"]["content"]