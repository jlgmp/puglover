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

@app.route('/meterin', methods=['POST'])
def meter_reading_endpoint():
    global meter_database
    req_data = request.json

    for field in ["device","time", "meter"]:
        if field not in req_data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    device = req_data["device"]
    time_slot = req_data["time"]
    meter = req_data["meter"]

    existing_meter = next((m for m in meter_database if m.device_id == device), None)

    if existing_meter is None:
        new_meter = Meter(device)
        new_meter.add_reading(time_slot, meter)
        meter_database.append(new_meter)
    else:
        existing_meter.add_reading(time_slot, meter)

    return jsonify({m.device_id: m.get_readings() for m in meter_database}), 200

@app.route('/meterdata', methods=['GET'])
def get_meter_data():
    global meter_database
    device_id = request.args.get("device")  # 从请求参数获取 device_id

    if not device_id:
        return jsonify({"message": "请提供 device 参数"}), 400

    # 查找指定设备的 meter 数据
    existing_meter = next((m for m in meter_database if m.device_id == device_id), None)

    if existing_meter is None:
        return jsonify({"message": f"设备 {device_id} 未找到"}), 404

    return jsonify({device_id: existing_meter.get_readings()}), 200


def meterDataBackup(meter_database):
    file_name = 'meter_database.txt'
    df = pd.read_csv(file_name, sep=',', encoding='utf-8')
    df_sorted = df.sort_values('Date', ascending=True)
    last_readings = df_sorted.groupby('DeviceID').tail(1).set_index('DeviceID')['Final_Daily_Readings'].to_dict()

    new_data = []
    today = datetime.date.today().strftime('%Y-%m-%d')
    for meter in meter_database:
        device_id = meter.device_id
        readings = meter.readings
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