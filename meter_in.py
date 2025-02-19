import random
import requests
import pandas as pd
from datetime import datetime

USER_DB_FILE = 'userDatabase.txt'
METER_DB_FILE = 'meterDatabase.txt'
API_URL = 'http://127.0.0.1:5001/meterin'

def generate_half_hour_times():
    """生成从 01:00 到当前时间最近的半小时整点时间列表"""
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute

    # 计算最近的半小时整点
    if current_minute < 30:
        latest_time = f"{current_hour:02d}:00"
    else:
        latest_time = f"{current_hour:02d}:30"

    # 生成时间列表，从 01:00 到 latest_time
    time_list = [f"{hour:02d}:{minute:02d}" for hour in range(1, current_hour + 1) for minute in [0, 30]]
    if latest_time not in time_list:
        time_list.append(latest_time)  # 添加当前时间的最近整点

    return time_list

def load_user_devices():
    """读取 userDatabase.txt, 获取所有 device_id"""
    with open(USER_DB_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def load_last_meter_readings():
    """从 meterDatabase.txt 读取每个设备的最后一个 24:00 读数"""
    try:
        df = pd.read_csv(METER_DB_FILE, sep=',', encoding='utf-8', header=None,
                         names=["DeviceID", "Date", "Final_Daily_Readings", "Daily_Consumption"])
        
        df["Final_Daily_Readings"] = pd.to_numeric(df["Final_Daily_Readings"], errors='coerce')
        last_readings = df.groupby("DeviceID")["Final_Daily_Readings"].last().to_dict()
        return last_readings
    except Exception as e:
        print(f"⚠️ 读取 {METER_DB_FILE} 失败: {e}")
        return {}

def generate_meter_data(device_id, last_meter_reading):
    """生成当日电表读数，直到当前时间的最近半小时整点"""
    times = generate_half_hour_times()

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

        # 发送数据到 API
        data = {'device': device_id, "time": time, 'meter': meter}
        response = requests.post(API_URL, json=data)
        if response.status_code != 200:
            print(f"❌ 设备 {device_id} 在 {time} 发送失败: {response.text}")

    return readings

if __name__ == "__main__":
    devices = load_user_devices()
    last_readings = load_last_meter_readings()
    all_readings = {}

    for device in devices:
        last_meter = last_readings.get(device, None)
        readings = generate_meter_data(device, last_meter)
        all_readings[device] = readings

    for device, readings in all_readings.items():
        print(f"Device: {device}, Readings: {readings}")
    
    print("✅ 所有设备数据已成功生成并发送！")