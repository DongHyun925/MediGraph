import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from src.api import chat_endpoint, ChatRequest
from langchain_core.messages import HumanMessage
import uuid
import traceback

async def debug_chat():
    print("Starting debug_chat...")
    try:
        # Simulate a request
        request = ChatRequest(message="headache", thread_id=str(uuid.uuid4()))
        print(f"Sending request: {request}")
        
        response = await chat_endpoint(request)
        print("Response received:")
        print(response)
        
    except Exception:
        print("Caught exception during chat_endpoint execution:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_chat())
