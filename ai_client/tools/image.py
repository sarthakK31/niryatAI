import requests

def vision_tool(image_base64: str, prompt="Describe the image"):
    """
    Tool to process an image and return a description of it. The image is provided as a base64 string, and the prompt can be customized to specify what kind of description is desired.
    """

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

    print("[DEBUG] Response:", r.json())

    return r.json()["message"]["content"]