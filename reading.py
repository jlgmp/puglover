import datetime
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)
acceptAPI=True

global meter_database
meter_database = {}

class Meter:
    def __init__(self, device_id):
        self.device_id = device_id
        self.readings = {}
    def add_reading(self, time, meter):
        self.readings[time] = round(float(meter),1)
    def get_readings(self):
        return self.readings
    def __str__(self):
        return f"Device: {self.device_id}, Readings: {self.readings}"

@app.route('/meterin', methods=['POST'])
def meter_in():
    global meter_database
    data = request.json

    device = data["device"]
    time = data["time"]
    meter = data["meter"]

    if device not in meter_database:
        meter_database[device] = Meter(device)

    meter_database[device].add_reading(time, meter)
    return jsonify({device: meter_database[device].get_readings()}), 200

@app.route('/meterdata', methods=['GET'])
def meter_data():
    global meter_database
    device_id = request.args.get("device")

    return jsonify({device_id: meter_database[device_id].get_readings()}), 200

def meterDataBackup(meter_database):
    df = pd.read_csv('meterDatabase.txt', sep=',', encoding='utf-8')
    df_sorted = df.sort_values('Date', ascending=True)
    last_readings = df_sorted.groupby('DeviceID').tail(1).set_index('DeviceID')['Final_Daily_Readings'].to_dict()

    new_data = []
    today = datetime.date.today().strftime('%Y-%m-%d')

    for device_id, meter in meter_database.items():
        readings = meter.readings
        # final_reading_today = readings["24:00"]
        final_reading_today = readings[max(readings.keys())]
        previous_final = last_readings.get(device_id, 0)
        daily_consumption = final_reading_today - previous_final

        new_data.append([device_id, today, f"{final_reading_today:.1f}", f"{daily_consumption:.1f}"])

    with open('meterDatabase.txt', 'a', encoding='utf-8') as f:
        for entry in new_data:
            f.write(",".join(entry) + "\n")
    
    print("Backup completed!")


@app.route('/stopServer',methods=['GET', 'POST'])
def stop_server():
    global acceptAPI, meter_database
    acceptAPI=False
    meterDataBackup(meter_database)
    acceptAPI = True
    return "Server Shutting Down"

if __name__ == '__main__':
    app.run(debug=False, port=5001)