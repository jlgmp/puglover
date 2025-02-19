import requests

response = requests.post("http://127.0.0.1:5000/stopServer")

if response.status_code == 200:
    print("Backup successfully! ")
else:
    print(f"Backup failed：{response.status_code}")