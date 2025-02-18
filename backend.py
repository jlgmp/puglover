from flask import Flask, jsonify, request
import logging
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


app = Flask(__name__)
user_database_file='userdatabase.txt'
meter_file='meter.txt'

logging.basicConfig(filename='electricity.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

user_database=[]
class User:
    def __init__(self,username,password,device_id):
        self.username=username
        self.password=password
        self.device_id=device_id

@app.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    device_id=data.get('id')
    user_tem=User(username,password,device_id)
    user_database.append(user_tem)
    
    if not os.path.exists(user_database_file):
        open(user_database_file, 'w').close()
    
    with open(user_database_file,'a') as userdatabase :
        userdatabase.write(f"{username},{password},{device_id}\n")
    print(user_database)
    return  jsonify({"status": "success", "message": f"device id:{device_id} registered successfully."}),201


data_store = {}
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
    req_data = request.json
    for field in ["device", "date", "time", "meter"]:
        if field not in req_data:
            return jsonify({"message": f"缺少字段: {field}"}), 400

    device = req_data["device"]
    date = req_data["date"]
    time_slot = req_data["time"]
    meter = req_data["meter"]

    # if device not exists, create a new one
    if device not in data_store:
        data_store[device] = Meter(device)

    # record meter reading
    data_store[device].add_reading(date, time_slot, meter)

    logging.info(f"DeviceID {device} Date {date} Time {time_slot} Meter_Reading: {meter}")

    # return data of all devices and delete remaining items
    simplified_data = {dev: obj.get_readings() for dev, obj in data_store.items()}

    return jsonify(simplified_data), 200


@app.route('/query', methods=['GET'])
def query():
    account = request.args.get('account')
    
    if not account:
        return jsonify({"error": "Missing 'account' in query parameters"}), 400

    if not os.path.exists(meter_file):
        return jsonify({"error": "No meter readings available"}), 404

    matching_records = []
    with open(meter_file, 'r') as meterdatabase:
        for line in meterdatabase:
            acc, meter = line.strip().split(',')
            if acc == account:
                matching_records.append({"account": acc, "meter": meter})

    if not matching_records:
        return jsonify({"error": "Account not found"}), 404

    return jsonify({"account": account, "meter_readings": matching_records}), 200
'''
def query_data():
    # 通过URL参数传递设备ID和日期，例如：/query?device=111-111-111&date=2024-01-01
    device = request.args.get("device")
    date = request.args.get("date")  # 可选参数

    if not device:
        return jsonify({"message": "请提供设备ID (device) 参数"}), 400

    # 从内存数据结构中获取指定设备的数据
    device_data = data_store.get(device)
    if device_data is None:
        return jsonify({"message": f"设备 {device} 没有记录"}), 404

    if date:
        # 如果提供了日期，则返回该日期的数据
        date_data = device_data.get(date)
        if date_data is None:
            return jsonify({"message": f"设备 {device} 在日期 {date} 没有记录"}), 404
        return jsonify({device: {date: date_data}})
    else:
        # 否则返回该设备所有的记录
        return jsonify({device: device_data})

'''




   
@app.route('/stopServer',methods=['GET'])
def stop_server():
    global acceptAPI
    acceptAPI=False
    acceptAPI=True
    return "Server Shutting Down"


if __name__ == '__main__':
    
    app.run(debug=False, port=5001, use_reloader=False)