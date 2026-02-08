import requests
import time

# Use the running server URL
API_URL = "http://localhost:8090"

def test_watchlist():
    print("=== Starting Watchlist Verification ===")
    
    # 1. Register/Login to get Token
    random_id = int(time.time())
    email = f"watchlist_test_{random_id}@gmail.com"
    password = "password123"
    username = f"user_{random_id}"
    
    # Register
    requests.post(f"{API_URL}/auth/register", json={
        "email": email, "password": password, "username": username, "full_name": "Watchlist Tester"
    })
    
    # Login
    res = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
        
    token = res.json()["session"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful, token acquired.")
    
    # 2. Add Item
    print("\n[TEST] Add to Watchlist")
    media_id = "tt_inception"
    res = requests.post(f"{API_URL}/watchlist", json={
        "media_id": media_id,
        "media_type": "movie"
    }, headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    
    # 3. Get Watchlist
    print("\n[TEST] Get Watchlist")
    res = requests.get(f"{API_URL}/watchlist", headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    data = res.json()
    if any(item.get('tmdb_id') == media_id for item in data['watchlist']):
        print("PASS: Item found in watchlist.")
    else:
        print("FAIL: Item NOT found in watchlist.")
        
    # 4. Remove Item
    print("\n[TEST] Remove from Watchlist")
    res = requests.delete(f"{API_URL}/watchlist/{media_id}", headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text}")
    
    # 5. Verify Empty
    print("\n[TEST] Verify Removal")
    res = requests.get(f"{API_URL}/watchlist", headers=headers)
    data = res.json()
    if not any(item.get('tmdb_id') == media_id for item in data['watchlist']):
        print("PASS: Watchlist does not contain item.")
    else:
        print("FAIL: Item still in watchlist.")

if __name__ == "__main__":
    test_watchlist()
