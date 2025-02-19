import datetime
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

global meter_database
meter_database = []

class Meter:
    def __init__(self, device_id):
        self.device_id = device_id
        self.readings = {}
    def add_reading(self, time_slot, meter):
        self.readings[time_slot] = round(float(meter),1)
    def get_readings(self):
        return self.readings
    def __str__(self):
        return f"Device: {self.device_id}, Readings: {self.readings}"

@app.route('/meterreading', methods=['POST'])
def meter_reading_endpoint():
    global meter_database
    req_data = request.json

    for field in ["device","time", "meter"]:
        if field not in req_data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    device = req_data["device"]
    time_slot = req_data["time"]
    meter = req_data["meter"]

    # 检查是否已有该设备
    existing_meter = next((m for m in meter_database if m.device_id == device), None)

    if existing_meter is None:
        # 新建设备并添加数据
        new_meter = Meter(device)
        new_meter.add_reading(time_slot, meter)
        meter_database.append(new_meter)
    else:
        # 设备已存在，直接更新数据
        existing_meter.add_reading(time_slot, meter)

    # 打印当前数据库（调试用）
    #for m in meter_database:
    #    print(m)

    # 返回所有设备的数据
    return jsonify({m.device_id: m.get_readings() for m in meter_database}), 200


def meterDataBackup(meter_database):
    file_name = 'meter_database.txt'
    df = pd.read_csv(file_name, sep=',', encoding='utf-8')
    df_sorted = df.sort_values('Date', ascending=True)
    last_readings = df_sorted.groupby('DeviceID').tail(1).set_index('DeviceID')['Final_Daily_Readings'].to_dict()
    
    # 处理新的数据
    new_data = []
    today = datetime.date.today().strftime('%Y-%m-%d')
    for meter in meter_database:
        device_id = meter.device_id
        readings = meter.readings  # {时间: 读数}
        final_reading_today = readings["24:00"]

        previous_final = last_readings.get(device_id, None)
        daily_consumption = final_reading_today - previous_final
        
        new_data.append([device_id, today, f"{final_reading_today:.1f}", f"{daily_consumption:.1f}"])

    with open(file_name, 'a', encoding='utf-8') as f:
        for entry in new_data:
            f.write(",".join(entry) + "\n")
    
    print("Backup completed!")

@app.route('/backup', methods=['GET', 'POST'])
def stopserver():
    global meter_database
    meterDataBackup(meter_database)
    return jsonify({"message": "数据备份完成！"}), 200 


if __name__ == '__main__':
    app.run(debug=False, port=5001)