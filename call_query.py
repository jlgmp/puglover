import requests

def query_meter():
    account = input("Please input your account: ")

    response = requests.get(f'http://127.0.0.1:5001/query?account={account}')
    data = response.json()

    if response.status_code == 200:
        print(f"Meter readings for account {account}:")
        for record in data['meter_readings']:
            print(f"Meter: {record['meter']}")
    else:
        print(f"Error: {data['error']}")

if __name__ == '__main__':
    query_meter()