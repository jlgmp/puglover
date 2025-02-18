import requests

'''
def query_meter():
    device = input("pls input your device")
    date = input("date")

    response = requests.get(f'http://127.0.0.1:5001/query?device={device}&date={date}')
    data = response.json()

    if response.status_code == 200:
        print(f"Meter readings for account {device}:")
        for record in data['meter_readings']:
            print(f"Meter: {record['meter']}")
    else:
        print(f"Error: {data['error']}")

if __name__ == '__main__':
    query_meter()
'''
def meter_reading():
    device = input("Pls input your device_id: ")
    date_str = input("Pls input your date (format: yyyy-mm-dd): ")
    time_slot = input("Pls input time (format: hh:mm): ")
    meter = input("Pls input meter readings: ")

    data = {
        'device': device, 
        'date': date_str,
        'time': time_slot,
        'meter': meter
    }

    response = requests.post('http://127.0.0.1:5001/meterreading', json=data)
    result = response.json()

    # 直接打印原始的简化数据
    print(result)

if __name__ == '__main__':
    meter_reading()