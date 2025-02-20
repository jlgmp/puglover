import requests

device_id = "398-446-958"
url = f"http://127.0.0.1:5000/meterdata?device={device_id}"

response = requests.get(url)

if response.status_code == 200:
    print(response.json())
else:
    print(f"Query failed: {response.status_code}, {response.text}")