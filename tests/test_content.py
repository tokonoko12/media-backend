import requests
import time

API_URL = "http://localhost:8090"

def test_content():
    print("=== Starting Content Verification ===")
    
    # 1. Test Health (Public)
    print("\n[TEST] Health Check")
    res = requests.get(f"{API_URL}/health/ping")
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    if res.status_code == 200 and res.text == "pong":
        print("PASS: Health check passed")
    else:
        print("FAIL: Health check failed")

    # 2. Login to get Token
    random_id = int(time.time())
    email = f"content_test_{random_id}@gmail.com"
    password = "password123"
    username = f"user_{random_id}"
    
    # Register & Login
    requests.post(f"{API_URL}/auth/register", json={
        "email": email, "password": password, "username": username, "full_name": "Content Tester"
    })
    res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    if res.status_code != 200:
        print("FAIL: Login failed, cannot proceed with content tests")
        return
        
    token = res.json()["session"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Test Movies (tt26443597)
    print("\n[TEST] Get Movie Streams (tt26443597)")
    # Note: This might be slow if it actually scrapes/fetches, so we just check it doesn't 500
    try:
        res = requests.get(f"{API_URL}/movies/tt26443597", headers=headers, timeout=30)
        print(f"Status: {res.status_code}")
        # Response might be empty list or actual streams depending on external providers
        # We assume 200 OK is success provided auth works
        if res.status_code == 200:
            print("PASS: Movie endpoint returned 200 OK")
        else:
            print(f"FAIL: Movie endpoint returned {res.status_code}")
            print(res.text[:200]) # Print first 200 chars
    except Exception as e:
        print(f"FAIL: Movie request failed: {e}")

    # 4. Test Series (tt4574334)
    print("\n[TEST] Get Series Streams (tt4574334 S1 E1)")
    try:
        res = requests.get(f"{API_URL}/series/tt4574334/1/1", headers=headers, timeout=30)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("PASS: Series endpoint returned 200 OK")
        else:
            print(f"FAIL: Series endpoint returned {res.status_code}")
            print(res.text[:200])
    except Exception as e:
        print(f"FAIL: Series request failed: {e}")

if __name__ == "__main__":
    test_content()
