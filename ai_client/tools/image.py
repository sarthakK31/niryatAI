import requests

def vision_tool(image_base64: str, prompt="Describe the image"):
    """
    Tool to process an image and return a description of it. The image is provided as a base64 string, and the prompt can be customized to specify what kind of description is desired.
    """

    r = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "qwen2.5vl:7b",
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                }
            ]
        }
    )

    print("[DEBUG] Response:", r.text)
    data = r.json()
    print("[DEBUG] JSON Response:", data)

    return data["message"]["content"]