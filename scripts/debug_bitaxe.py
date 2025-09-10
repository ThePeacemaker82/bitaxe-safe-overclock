import requests
import json

MINER_IP = "192.168.1.97"

def test_patch_request():
    """Test PATCH request with detailed logging"""
    url = f"http://{MINER_IP}/api/system"
    
    # Test frequency setting
    freq_data = {"frequency": 400}
    print(f"Testing PATCH to {url}")
    print(f"Data: {json.dumps(freq_data)}")
    
    try:
        response = requests.patch(url, json=freq_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: '{response.text}'")
        print(f"Response Length: {len(response.text)}")
        
        if 200 <= response.status_code < 300:
            print("✅ Request successful (2xx status)")
            if response.text.strip():
                try:
                    json_data = response.json()
                    print(f"JSON Response: {json_data}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
            else:
                print("✅ Empty response (normal for PATCH)")
        else:
            print(f"❌ HTTP error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request exception: {e}")

if __name__ == "__main__":
    test_patch_request()