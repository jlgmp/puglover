import random
import requests
import pandas as pd
from datetime import datetime
import pytz
singapore_tz = pytz.timezone('Asia/Singapore')

def generate_times():
    now = datetime.now(singapore_tz)
    current_hour = now.hour
    current_minute = now.minute

    if current_minute < 30:
        latest_time = f"{current_hour:02d}:00"
    else:
        latest_time = f"{current_hour:02d}:30"

    time_list = [f"{hour:02d}:{minute:02d}" for hour in range(1, current_hour) for minute in [0, 30]]
    if latest_time not in time_list:
        time_list.append(latest_time)

    return time_list

def load_devices():
    with open('userDatabase.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def load_readings():
    df = pd.read_csv('meterDatabase.txt', sep=',', encoding='utf-8', header=None,
                    names=["DeviceID", "Date", "Final_Daily_Readings", "Daily_Consumption"])
    
    df["Final_Daily_Readings"] = pd.to_numeric(df["Final_Daily_Readings"], errors='coerce')
    last_readings = df.groupby("DeviceID")["Final_Daily_Readings"].last().to_dict()
    return last_readings

def generateMeter(deviceid, last_meter_reading):
    times = generate_times()

    if last_meter_reading is not None:
        initial_meter = round(last_meter_reading + random.uniform(1.0, 5.0), 1)
    else:
        initial_meter = round(random.uniform(10.1, 30.1), 1)

    meter = initial_meter
    readings = {}

    for time in times:
        hour_con = round(random.uniform(0.3, 0.45), 1)
        meter = round(meter + hour_con, 1)
        readings[time] = meter

        data = {'device': deviceid, "time": time, 'meter': meter}
        response = requests.post('http://127.0.0.1:5001/meterin', json=data)
        if response.status_code != 200:
            print(f"DeviceID {deviceid} at {time} posting failed: {response.text}")

    return readings

if __name__ == "__main__":
    devices = load_devices()
    last_readings = load_readings()
    all_readings = {}

    for device in devices:
        last_meter = last_readings.get(device, None)
        readings = generateMeter(device, last_meter)
        all_readings[device] = readings

    for device, readings in all_readings.items():
        print(f"Device: {device}, Readings: {readings}")
    
    print("All Devices are posting successfully!")