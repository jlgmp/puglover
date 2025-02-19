import random
import requests
import pandas as pd

USER_DB_FILE = 'userDatabase.txt'
METER_DB_FILE = 'meterDatabase.txt'
API_URL = 'http://127.0.0.1:5000/meterreading'

def generate_half_hour_times():
    """生成半小时间隔的时间列表"""
    time_list = [f"{hour:02d}:{minute:02d}" for hour in range(1, 24) for minute in [0, 30]]
    time_list.append("24:00")  # 添加 24:00
    return time_list

def load_user_devices():
    """读取 userdatabase.txt，获取所有 device_id"""
    with open(USER_DB_FILE, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def load_last_meter_readings():
    """从 meter_database.txt 读取每个设备的最后一个 24:00 读数"""
    try:
        df = pd.read_csv(METER_DB_FILE, sep=',', encoding='utf-8', header=None,
                         names=["DeviceID", "Date", "Final_Daily_Readings", "Daily_Consumption"])
        
        # 转换数据类型，确保数值正确
        df["Final_Daily_Readings"] = pd.to_numeric(df["Final_Daily_Readings"], errors='coerce')
        
        # 选择每个设备的最新日期的 `Final_Daily_Readings`
        last_readings = df.groupby("DeviceID")["Final_Daily_Readings"].last().to_dict()

        return last_readings
    except Exception as e:
        print(f"⚠️ 读取 {METER_DB_FILE} 失败: {e}")
        return {}

def generate_meter_data(device_id, last_meter_reading):
    """生成当日电表读数，确保 01:00 读数比前一天 24:00 读数大"""
    times = generate_half_hour_times()
    
    # 确保 01:00 读数大于 24:00 读数
    if last_meter_reading is not None:
        initial_meter = round(last_meter_reading + random.uniform(1.0, 5.0), 1)
    else:
        initial_meter = round(random.uniform(10.1, 30.1), 1)  # 若无前一天数据，随机初始化
    
    meter = initial_meter
    readings = {}

    for time in times:
        hour_con = round(random.uniform(0.3, 0.45), 1)
        meter = round(meter + hour_con, 1)  # 读数递增
        readings[time] = meter

        # 发送数据到 API
        data = {'device': device_id, "time": time, 'meter': meter}
        response = requests.post(API_URL, json=data)
        if response.status_code != 200:
            print(f"❌ 设备 {device_id} 在 {time} 发送失败: {response.text}")

    return readings

if __name__ == "__main__":
    devices = load_user_devices()  # 读取用户设备
    last_readings = load_last_meter_readings()  # 读取最后的 24:00 读数

    all_readings = {}

    for device in devices:
        last_meter = last_readings.get(device, None)  # 获取 device_id 的 24:00 读数
        readings = generate_meter_data(device, last_meter)
        all_readings[device] = readings

    # 打印检查
    for device, readings in all_readings.items():
        print(f"Device: {device}, Readings: {readings}")
    
    print("✅ 所有设备数据已成功生成并发送！")
