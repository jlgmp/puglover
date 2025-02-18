import json
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

global meter_database
meter_database = []

class Meter:
    def __init__(self, device_id):
        self.device_id = device_id
        self.readings = {}

    def add_reading(self, date, time_slot, meter):
        if date not in self.readings:
            self.readings[date] = {}
        self.readings[date][time_slot] = int(meter)

    def get_readings(self):
        return self.readings

    def __str__(self):
        return f"Device: {self.device_id}, Readings: {self.readings}"

@app.route('/meterreading', methods=['POST'])
def meter_reading_endpoint():
    global meter_database
    req_data = request.json

    for field in ["device", "date", "time", "meter"]:
        if field not in req_data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    device = req_data["device"]
    date = req_data["date"]
    time_slot = req_data["time"]
    meter = req_data["meter"]

    # 检查是否已有该设备
    existing_meter = next((m for m in meter_database if m.device_id == device), None)

    if existing_meter is None:
        # 新建设备并添加数据
        new_meter = Meter(device)
        new_meter.add_reading(date, time_slot, meter)
        meter_database.append(new_meter)
    else:
        # 设备已存在，直接更新数据
        existing_meter.add_reading(date, time_slot, meter)

    # 打印当前数据库（调试用）
    for m in meter_database:
        print(m)

    # 返回所有设备的数据
    return jsonify({m.device_id: m.get_readings() for m in meter_database}), 200


def meterDataBackup(meter_database):
    with open('meter_database.txt', 'w', encoding='utf-8') as f:
        f.write("DeviceID, Date, Final_Daily_Readings, Daily_Consumption\n")  # 写入表头
        
        for meter in meter_database:
            readings = meter.readings  # 设备的所有读数
            sorted_dates = sorted(readings.keys())  # 日期按升序排列
            
            if not sorted_dates:
                continue  # 该设备无数据，跳过
            
            # 处理 **第一天**
            first_date = sorted_dates[0]  # 取出第一天的日期
            if "00:00" in readings[first_date]:  # 确保第一天 00:00 数据存在
                first_final_reading = readings[first_date]["00:00"]
                first_daily_consumption = first_final_reading  # 假设前一天终值为 0
                f.write(f"{meter.device_id}, {first_date}, {first_final_reading}, {first_daily_consumption}\n")
            
            # 处理 **后续天**
            for i in range(1, len(sorted_dates)):  # 这里从 **1** 开始，跳过第一天，防止重复计算
                current_date = sorted_dates[i - 1]
                next_date = sorted_dates[i]
                
                current_day_readings = readings[current_date]
                next_day_readings = readings[next_date]
                
                if "00:00" not in current_day_readings or "00:00" not in next_day_readings:
                    continue  # 若缺少数据，则跳过
                
                previous_final = current_day_readings["00:00"]
                today_final = next_day_readings["00:00"]
                daily_consumption = today_final - previous_final
                
                # 记录 **current_date** 的数据
                f.write(f"{meter.device_id}, {current_date}, {today_final}, {daily_consumption}\n")

    print("Backup completed!")

@app.route('/backup', methods=['GET', 'POST'])
def stopserver():
    if not meter_database:
        return jsonify({"message": "⚠️ 没有数据需要备份！"}), 400  # ✅ 这里处理空数据
    meterDataBackup(meter_database)  # 执行备份
    return jsonify({"message": "✅ 数据备份完成！"}), 200  # ✅ 返回 HTTP 响应


if __name__ == '__main__':
    app.run(debug=False, port=5001)