import requests
import time
import subprocess
import sys
import os

def test_api():
    print("Testing API...")
    url = "http://127.0.0.1:8000/chat"
    payload = {"message": "I have a headache."}
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            print("API Test Passed!")
            print(f"Response: {data.get('response')}")
            print(f"Steps: {len(data.get('steps', []))}")
            return True
        else:
            print(f"API Test Failed with {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"API Connection Error: {e}")
        return False

if __name__ == "__main__":
    # Start server in a separate process
    # Note: In a real CI environment we would manage this better, 
    # but for this agent execution, we'll try to rely on manual start or 
    # just assume the user might run it. 
    # Actually, let's try to hit it assuming I'll start it in background via run_command.
    if test_api():
        sys.exit(0)
    else:
        sys.exit(1)
