import requests

response = requests.post("http://127.0.0.1:5000/backup")

if response.status_code == 200:
    print("Backup Completed！")
else:
    print(f"Backup Failed, response: {response.status_code}")
    print("API: ", response.text)