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
        self.readings[date][time_slot] = round(float(meter),1)

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
    file_name = 'meter_database.txt'

    # 读取已有数据（如果文件存在）
    existing_data = []
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 跳过表头
            for line in lines[1:]:
                parts = line.strip().split(", ")
                if len(parts) == 4:
                    existing_data.append(parts)  # [DeviceID, Date, Final_Reading, Daily_Consumption]

    # 处理新的数据
    new_data = []
    # 处理新的数据
    new_data = []
    for meter in meter_database:
        readings = meter.readings  # 获取设备的所有读数
        sorted_dates = sorted(readings.keys())  # 日期按升序排列

        if len(sorted_dates) < 2:
            continue  # 如果设备数据少于 2 天，则无法计算用电量，跳过

        # 遍历日期，计算每日最终读数和用电量
        for i in range(len(sorted_dates) - 1):  # 只到倒数第二天
            current_date = sorted_dates[i]
            next_date = sorted_dates[i + 1]

            # 确保当前天和第二天都有 "00:00" 读数
            if "00:00" not in readings[current_date] or "00:00" not in readings[next_date]:
                continue

            final_reading = readings[next_date]["00:00"]  # 当天的最终读数取自第二天的 "00:00"
            daily_consumption = final_reading - readings[current_date]["00:00"]

            new_data.append([meter.device_id, current_date, f"{final_reading:.1f}", f"{daily_consumption:.1f}"])

    # 合并已有数据和新数据
    all_data = existing_data + new_data

    # **按 DeviceID 和 Date 排序**
    all_data.sort(key=lambda x: (x[0], x[1]))

    # 重新写入文件
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write("DeviceID, Date, Final_Daily_Readings, Daily_Consumption\n")
        for entry in all_data:
            f.write(", ".join(entry) + "\n")
    
    print("Backup completed!")

@app.route('/backup', methods=['GET', 'POST'])
def stopserver():
    if not meter_database:
        return jsonify({"message": "⚠️ 没有数据需要备份！"}), 400  # ✅ 这里处理空数据
    meterDataBackup(meter_database)  # 执行备份
    return jsonify({"message": "✅ 数据备份完成！"}), 200  # ✅ 返回 HTTP 响应


if __name__ == '__main__':
    app.run(debug=False, port=5001)