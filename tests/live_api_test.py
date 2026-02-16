import requests
import uuid

def test_live_api():
    url = "http://localhost:8000/chat"
    thread_id = str(uuid.uuid4())
    
    # 1. First turn
    print("\n>>> Send: 속이 쓰려요")
    resp1 = requests.post(url, json={"message": "속이 쓰려요", "thread_id": thread_id})
    print(f"Status: {resp1.status_code}")
    print(resp1.json())
    
    # 2. Second turn
    print("\n>>> Send: 명치")
    resp2 = requests.post(url, json={"message": "명치", "thread_id": thread_id})
    print(f"Status: {resp2.status_code}")
    print(resp2.json())
    
    # 3. Third turn (The crash turn)
    print("\n>>> Send: 소화제 먹었어요")
    resp3 = requests.post(url, json={"message": "소화제 먹었어요", "thread_id": thread_id})
    print(f"Status: {resp3.status_code}")
    try:
        print(resp3.json())
    except:
        print(resp3.text)

if __name__ == "__main__":
    test_live_api()
