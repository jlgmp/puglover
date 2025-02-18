import requests

def meter_reading():
    device=input("Pls input your device_id")
    date_str=input("Pls input your date (format: yyyy-mm-dd)")
    time_slot = input("Pls input time (format: hh:mm)")
    meter = input("Pls input meter readings")

    data = {
        'device': device, 
        'date' : date_str,
        'time' : time_slot,
        'meter':meter
    }

    response = requests.post('http://127.0.0.1:5001/meterreading', json=data)
    result=response.json()
    
    print(result)

if __name__=='__main__':
    meter_reading()

    