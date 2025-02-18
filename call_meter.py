import requests

def meter_reading():
    while True:
        device = input("\nPlease enter your DeviceID ('x' to stop): ")
        if device.lower() == 'x':
            break
        
        while True:
            date_str = input("Please enter Date (format: yyyy-mm-dd, 'b' to DeviceID, 'x' to stop): ")
            if date_str.lower() == 'x':
                return
            if date_str.lower() == 'b':
                break  # 允许用户重新选择设备 ID
            
            while True:
                time_slot = input("Please enter Time (format: hh:mm, 'b' to Date, 'x' to stop): ")
                if time_slot.lower() == 'x':
                    return
                if time_slot.lower() == 'b':
                    break  # 允许用户重新选择日期

                meter = input("Please enter meter reading: ")
                if meter.lower() == 'x':
                    return

                data = {
                    'device': device, 
                    'date': date_str,
                    'time': time_slot,
                    'meter': meter
                }

                response = requests.post('http://127.0.0.1:5001/meterreading', json=data)
                result = response.json()

                print("Successfully recorded.")
                print(result)  # 输出服务器返回的完整数据

if __name__ == '__main__':
    meter_reading()