import requests
import json

MINER_IP = "192.168.1.97"

def test_endpoint(endpoint, method="GET", data=None):
    url = f"http://{MINER_IP}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, json=data, timeout=10)
        
        print(f"{method} {endpoint}: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"{method} {endpoint}: ERROR - {e}")
        return False

# Test different endpoints
print("Testing API endpoints...")
test_endpoint("/api/system/info")  # Should work
test_endpoint("/api/system")       # Test base endpoint
test_endpoint("/api/system", "POST", {"frequency": 650})  # Test POST
test_endpoint("/api/system", "PATCH", {"frequency": 650}) # Test PATCH