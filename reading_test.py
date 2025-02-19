import requests

def meter_reading():
    while True:
        device = input("\nPlease enter your DeviceID ('x' to stop): ")
        if device.lower() == 'x':
            break
        
        while True:
            date_str = input("Please enter Date (format: yyyy-mm-dd, 'b' to DeviceID, 'x' to stop): ")
            if date_str.lower() == 'x':
                return # exit
            if date_str.lower() == 'b':
                break  # back to enter DeviceID
            
            while True:
                time_slot = input("Please enter Time (format: hh:mm, 'b' to Date, 'x' to stop): ")
                if time_slot.lower() == 'x':
                    return # exit
                if time_slot.lower() == 'b':
                    break  # back to enter Date

                meter = input("Please enter meter reading: ")
                if meter.lower() == 'x':
                    return # exit

                data = {
                    'device': device, 
                    'date': date_str,
                    'time': time_slot,
                    'meter': meter
                }

                response = requests.post('http://127.0.0.1:5000/meterreading', json=data)
                result = response.json()

                print("Successfully recorded.")
                print(result)

if __name__ == '__main__':
    meter_reading()