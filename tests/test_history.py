import requests
import time

API_URL = "http://localhost:8090"

def test_history():
    print("=== Starting History Verification ===")
    
    # 1. Login
    random_id = int(time.time())
    email = f"history_test_{random_id}@gmail.com"
    password = "password123"
    username = f"user_{random_id}"
    
    requests.post(f"{API_URL}/auth/register", json={
        "email": email, "password": password, "username": username, "full_name": "History Tester"
    })
    res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    if res.status_code != 200:
        print("FAIL: Login failed")
        return
    token = res.json()["session"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Add History (Movie)
    print("\n[TEST] Add Movie History")
    res = requests.post(f"{API_URL}/history", json={
        "media_id": "tt_movie_1",
        "media_type": "movie",
        "progress": 120,
        "duration": 5000
    }, headers=headers)
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print("PASS: Added movie history")
    else:
        print(f"FAIL: {res.text}")

    # 3. Add History (Series)
    print("\n[TEST] Add Series History")
    res = requests.post(f"{API_URL}/history", json={
        "media_id": "tt_series_1",
        "media_type": "series",
        "season": 1,
        "episode": 1,
        "progress": 500,
        "duration": 2400
    }, headers=headers)
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print("PASS: Added series history")
    else:
        print(f"FAIL: {res.text}")

    # 4. Get History
    print("\n[TEST] Get History")
    res = requests.get(f"{API_URL}/history", headers=headers)
    print(f"Status: {res.status_code}")
    data = res.json()
    if len(data.get("history", [])) >= 2:
        print("PASS: History retrieved")
    else:
        print("FAIL: History empty or incomplete")

if __name__ == "__main__":
    test_history()
