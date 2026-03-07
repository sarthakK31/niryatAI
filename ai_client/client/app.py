# app.py
from strands import Agent
from strands.models.ollama import OllamaModel
from strands_tools import shell
from ai_client.tools.s3_tools import (
    list_buckets,
    browse_bucket,
    search_files,
    read_file,
    upload_file,
    generate_download_url
)
from ai_client.tools.postgres_tools import (
    list_tables,
    describe_table,
    preview_table,
    run_query,
    get_schema
)
from ai_client.tools.image import vision_tool
#from strands_tools import mem0_memory

import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """
You are an AI trade intelligence analyst.

You have access to two systems:

1. AWS S3 tools
   - list_buckets
   - browse_bucket
   - search_files
   - read_file
   - upload_file
   - generate_download_url

2. PostgreSQL trade database tools
   - list_tables
   - describe_table
   - preview_table
   - run_query

The PostgreSQL database contains international trade intelligence including:

• Countries
• HS product codes
• Import/export volumes
• Growth metrics
• Market opportunity indicators


Rules:
• Only SELECT queries are allowed
• Never modify database data
• Provide analytical insights, not just raw data
• Do not directly search the web for the asked info. First look for relevant info in the database.
• Do not get market intelligence from internet. Only use data from postgres database

Database Schema:
TABLE market_intelligence (
    id SERIAL PRIMARY KEY,
    country TEXT,
    hs_code TEXT,
    avg_growth_5y NUMERIC,
    volatility NUMERIC,
    total_import NUMERIC,
    opportunity_score NUMERIC,
    ai_summary TEXT
);

TABLE country_risk (
    country TEXT PRIMARY KEY,
    stability_index NUMERIC,
    risk_score NUMERIC
);
"""

# Create an Ollama model instance
ollama_model = OllamaModel(
    host="http://localhost:11434",  # Ollama server address
    model_id="llama3.1:8b-instruct-fp16"         # Specify the model
    # model_id="qwen2.5vl:7b",
)

# Create an agent using the Ollama model
agent = Agent(
    model=ollama_model, 
    tools=[
        list_buckets, 
        browse_bucket, 
        search_files, 
        read_file, 
        upload_file, 
        generate_download_url,
        list_tables,
        describe_table,
        preview_table,
        run_query,
        get_schema,
        vision_tool
    ], 
    system_prompt=SYSTEM_PROMPT
    )

# response = agent(messages=[
#     {
#         "role": "user",
#         "content": [{"text": "What are the Buckets accessible to you?"}]
#     }
# ])

# print("Response:", str(response))

# response = agent("What buckets are accessible to you?")
# print(response)

# response = agent("Give me the top 10 countries with best opportunities to export frozen shrimps and prawns")
# print(response)



# def run_agent(message: str, mem0_user_id: str, mem0_agent_id: str) -> str:
#     response = agent(message, user_id=mem0_user_id, agent_id=mem0_agent_id)
#     return str(response)

# run_agent("I am a dealer dealing in frozen shrimps and prawns. They have an HS Code=30617. Can you please find me the top 2 countries where it would be beneficial for me to expand my business", mem0_user_id="dummy_user", mem0_agent_id="session_1")

def run_agent(message: list[dict]) -> str: 
    response = agent(message) 
    return str(response)