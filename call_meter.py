import requests

def meter_reading():
    while True:
        device = input("\nPlease enter your DeviceID ('x' to stop): ")
        if device.lower() == 'x':
            break
        
        while True:
            time = input("Please enter Time (format: hh:mm, 'b' to DeviceID, 'x' to stop): ")
            if time.lower() == 'x':
                return
            if time.lower() == 'b':
                break

            meter = input("Please enter meter reading: ")
            if meter.lower() == 'x':
                return

            data = {'device': device, 'time': time,'meter': meter}
            response = requests.post('http://127.0.0.1:5001/meterin', json=data)
            result = response.json()

            print("Successfully recorded.")
            print(result)

if __name__ == '__main__':
    meter_reading()