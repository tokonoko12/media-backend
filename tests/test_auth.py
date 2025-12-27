import requests
import time

API_URL = "http://localhost:8090"

def test_auth():
    print("Testing Registration...")
    
    random_id = int(time.time())
    email = f"mediahub_test_{random_id}@gmail.com"
    password = "password123"
    username = f"user_{random_id}"
    full_name = "Test User"
    
    # 1. Register
    res = requests.post(f"{API_URL}/auth/register", json={
        "email": email, "password": password, "username": username, "full_name": full_name
    })
    
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    
    if res.status_code != 201:
        print("FAIL: Registration failed")
        return
        
    print(f"User ID: {res.json()['user']['id']}")
    
    # 1.5 Duplicate Registration (New Test)
    print("\nTesting Duplicate Registration...")
    res_dup = requests.post(f"{API_URL}/auth/register", json={
        "email": email, "password": password, "username": username, "full_name": full_name
    })
    print(f"Status: {res_dup.status_code}")
    print(f"Response: {res_dup.text}")
    if res_dup.status_code == 400 and "already exists" in res_dup.text:
       print("PASS: Duplicate Registration handled")
    else:
       print("FAIL: Duplicate Registration not handled correctly")
       
    # 2. Login
    print("\nTesting Login...")
    res = requests.post(f"{API_URL}/auth/login", json={
        "email": email, "password": password
    })
    
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    
    if res.status_code == 200:
        print("PASS: Login successful")
    else:
        print("FAIL: Login failed")
        return

    token = res.json()["session"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Get Current User
    print("\nTesting Get Current User...")
    res = requests.get(f"{API_URL}/auth/me", headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    if res.status_code == 200:
        print("PASS: Get Current User")
    else:
        print("FAIL: Get Current User")

    # 4. Logout
    print("\nTesting Logout...")
    res = requests.post(f"{API_URL}/auth/logout", headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    
    if res.status_code == 200:
        print("PASS: Logout successful")
    else:
        print("FAIL: Logout failed")

if __name__ == "__main__":
    test_auth()
