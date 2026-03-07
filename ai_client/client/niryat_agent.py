# from strands.tools.mcp import MCPClient
# from mcp.client.stdio import stdio_client, StdioServerParameters
# from strands import Agent
# from strands.models.ollama import OllamaModel
# from strands.hooks import AfterToolCallEvent

# class NiryatAgent(Agent):

#     # def after_tool_call_hook(self, event):
#     #     print("After tool call hook triggered for tool:", event.get("tool_name"))
#     #     if event.get("data"):
#     #         print("Tool call data before reset:", event["data"])
#     #         event["data"].eval_count = 0
#     #         event["data"].prompt_eval_count = 0

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # self.hooks.add_callback(AfterToolCallEvent, self.after_tool_call_hook)

# class SafeOllamaModel(OllamaModel):

#     async def stream(self, *args, **kwargs):
#         async for event in super().stream(*args, **kwargs):

#             # # Only patch metadata chunks
#             # if isinstance(event, dict) and event.get("chunk_type") == "metadata":
#             #     data = event.get("data")

#             #     if hasattr(data, "eval_count"):
#             #         if data.eval_count is None:
#             #             data.eval_count = 0

#             #     if hasattr(data, "prompt_eval_count"):
#             #         if data.prompt_eval_count is None:
#             #             data.prompt_eval_count = 0

#             # yield event
#          # Patch ANY event that has a data object
#             if isinstance(event, dict) and "data" in event:
#                 data = event["data"]

#                 if hasattr(data, "eval_count") and data.eval_count is None:
#                     data.eval_count = 0

#                 if hasattr(data, "prompt_eval_count") and data.prompt_eval_count is None:
#                     data.prompt_eval_count = 0

#             yield event

# postgres_mcp_client = MCPClient(lambda: stdio_client(
#     StdioServerParameters(
#         command="docker",
#         args=[
#             "run",
#             "--rm",
#             "-i",
#             "--log-driver", "none",
#             "--network", "niryatai_default",
#             "-e", "DATABASE_URI=postgresql://postgres:password@pg-db:5432/testdb",
#             "crystaldba/postgres-mcp",
#             "--access-mode=unrestricted"
#         ]
#     )
# ))

# s3_mcp_client = MCPClient(lambda: stdio_client(
#     StdioServerParameters(
#         command="docker",
#         args=[
#             "run",
#             "--rm",
#             "-i",
#             "-e", "AWS_ACCESS_KEY_ID=AKIATQ2SH6FTVZ5OKAFL",
#             "-e", "AWS_SECRET_ACCESS_KEY=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",
#             "-e", "AWS_REGION=us-east-1",
#             "aws-s3-mcp"
#         ]
#     )
# ))

# # Create an Ollama model instance
# ollama_model = SafeOllamaModel(
#     host="http://localhost:11434",  # Ollama server address
#     model_id="llama3.1:8b-instruct-fp16"             # Specify which model to use
# )

# agent = NiryatAgent(
#     model=ollama_model,
#     tools=[postgres_mcp_client, s3_mcp_client],
#     agent_id="niryat_agent"
# )

# response = agent(messages=[
#     {
#         "role": "user",
#         "content": [{"text": "What are the Buckets accessible to you ?"}]
#     }
# ])

# print("Response:", str(response))


import json
from strands.tools.mcp import MCPClient
from mcp.client.stdio import stdio_client, StdioServerParameters
from strands import Agent
#from strands.models.ollama import OllamaModel


import requests
# from strands.models.base import BaseModel
from strands.agent.model import Model

    
class SimpleOllamaModel(Model):
    def __init__(self, host: str, model_id: str):
        self.host = host
        self.model_id = model_id

    async def invoke_async(self, messages, **kwargs):
        # Convert Strands message format → Ollama format
        formatted_messages = []

        for msg in messages:
            role = msg["role"]
            text = ""

            for part in msg.get("content", []):
                if "text" in part:
                    text += part["text"]

            formatted_messages.append({
                "role": role,
                "content": text
            })

        # Call Ollama chat API (non-streaming)
        response = requests.post(
            f"{self.host}/api/chat",
            json={
                "model": self.model_id,
                "messages": formatted_messages,
                "stream": False
            }
        )

        response.raise_for_status()
        data = response.json()

        # Return in Strands expected format
        return {
            "role": "assistant",
            "content": [
                {"text": data["message"]["content"]}
            ]
        }


# MCP: Postgres
postgres_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="docker",
        args=[
            "run",
            "--rm",
            "-i",
            "--log-driver", "none",
            "--network", "niryatai_default",
            "-e", "DATABASE_URI=postgresql://postgres:password@pg-db:5432/testdb",
            "crystaldba/postgres-mcp",
            "--access-mode=unrestricted"
        ]
    )
))


# MCP: S3
s3_mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="docker",
        args=[
            "run",
            "--rm",
            "-i",
            # "--env-file", ".env"
            "-e", "AWS_ACCESS_KEY_ID=AKIATQ2SH6FTVZ5OKAFL",
            "-e", "AWS_SECRET_ACCESS_KEY=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",
            "-e", "AWS_REGION=us-east-1",
            "-e", "ALLOW_WRITE=true",  # enable presigned PUT
            "aws-s3-mcp:latest"
        ]
    )
))



# -------------------------------
# Helper Functions for S3
# -------------------------------
def list_buckets():
    with s3_mcp_client as client:
        resp = client.call_tool_sync(
            tool_use_id="s3-tool-1",
            name="s3_list_buckets",
            arguments={}
        )
        text = resp["content"][0]["text"]
        buckets = json.loads(text)
        print("Buckets:", buckets)
        return buckets

def list_objects(bucket_name):
    with s3_mcp_client as client:
        resp = client.call_tool_sync(
            tool_use_id="s3-tool-1",
            name="s3_list_objects",
            arguments={"bucket": bucket_name}
        )
        text = resp["content"][0]["text"]
        objects = json.loads(text)
        print(f"Objects in {bucket_name}:", objects)
        return objects

def presign_get(bucket_name, key):
    with s3_mcp_client as client:
        resp = client.call_tool_sync(
            tool_use_id="s3-tool-1",
            name="s3_presign_get",
            arguments={"bucket": bucket_name, "key": key, "expiresIn": 3600}
        )
        text = resp["content"][0]["text"]
        url = json.loads(text)["url"]
        print(f"Presigned GET URL for {key}:", url)
        return url

def presign_put(bucket_name, key):
    with s3_mcp_client as client:
        resp = client.call_tool_sync(
            tool_use_id="s3-tool-1",
            name="s3_presign_put",
            arguments={"bucket": bucket_name, "key": key, "expiresIn": 3600}
        )
        text = resp["content"][0]["text"]
        url = json.loads(text)["url"]
        print(f"Presigned PUT URL for {key}:", url)
        return url



# ollama_model = PatchedOllamaModel(
#     host="http://localhost:11434",
#     model_id="llama3.1:8b-instruct-fp16"
# )
ollama_model = SimpleOllamaModel(
    host="http://localhost:11434",
    model_id="llama3.1:8b-instruct-fp16"
)


# response = agent(messages=[
#     {
#         "role": "user",
#         "content": [{"text": "What are the Buckets accessible to you?"}]
#     }
# ])

# print("Response:", str(response))



# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    # Example: S3 MCP usage
    buckets = list_buckets()
    if buckets:
        bucket_name = buckets[0]["name"]
        list_objects(bucket_name)

        # Optional presigned URLs
        presign_get(bucket_name, "example.txt")
        presign_put(bucket_name, "upload.txt")

    # Ask Ollama about buckets

    agent = Agent(
        model=ollama_model,
        tools=[postgres_mcp_client, s3_mcp_client],
        agent_id="niryat_agent"
    )
    # response = agent(messages=[
    #     {
    #         "role": "user",
    #         "content": [{"text": "What are the Buckets accessible to you?"}]
    #     }
    # ])
    # # print("Agent Response:", str(response))
    # print("RAW RESPONSE OBJECT:")
    # print(response)
    # print("Type:", type(response))
    # print("Dir:", dir(response))
    # print("\nTEXT OUTPUT:")
    # print(response.message)


    # print("Stop reason:", response.stop_reason)
    # print("Metrics:", response.metrics)
    # print("State:", response.state)


    # agent = Agent(model=ollama_model)

    response = agent(messages=[
        {"role": "user", "content": [{"text": "Say hello"}]}
    ])

    print(response.message)
    print(response.metrics)



    # response = ollama_model(
    #     messages=[
    #         {"role": "user", "content": [{"text": "Say hello"}]}
    #     ]
    # )

    # print(response)


    # if client.is_running():
    # client.stop()