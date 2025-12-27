import requests
import time
import os

API_URL = "http://localhost:8090"

def test_catalog():
    print("=== Starting Catalog Verification ===")
    
    # 1. Login
    random_id = int(time.time())
    email = f"catalog_test_{random_id}@gmail.com"
    password = "password123"
    username = f"user_{random_id}"
    
    requests.post(f"{API_URL}/auth/register", json={
        "email": email, "password": password, "username": username, "full_name": "Catalog Tester"
    })
    res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    if res.status_code != 200:
        print("FAIL: Login failed")
        return
        
    token = res.json()["session"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Test Home
    print("\n[TEST] Catalog Home")
    res = requests.get(f"{API_URL}/catalog/home", headers=headers)
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        if "featured" in data and "sections" in data:
            print(f"PASS: Got featured ({len(data['featured'])}) and sections ({len(data['sections'])})")
        else:
            print("FAIL: Invalid strcuture")
    else:
        print(f"FAIL: {res.text}")

    # 3. Test Movies
    print("\n[TEST] Catalog Movies")
    res = requests.get(f"{API_URL}/catalog/movies", headers=headers)
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        if "sections" in data and len(data["sections"]) >= 1:
             print(f"PASS: Got {len(data['sections'])} movie sections")
        else:
            print("FAIL: Invalid structure")
    else:
        print(f"FAIL: {res.text}")

    # 4. Test Series
    print("\n[TEST] Catalog Series")
    res = requests.get(f"{API_URL}/catalog/series", headers=headers)
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        if "sections" in data and len(data["sections"]) >= 1:
             print(f"PASS: Got {len(data['sections'])} series sections")
        else:
            print("FAIL: Invalid structure")
    else:
        print(f"FAIL: {res.text}")

if __name__ == "__main__":
    test_catalog()
