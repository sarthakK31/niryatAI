from mem0 import MemoryClient
import os
from dotenv import load_dotenv

load_dotenv()

MEM0_API_KEY = os.getenv("MEM0_API_KEY")
memory_client = MemoryClient(api_key=MEM0_API_KEY)