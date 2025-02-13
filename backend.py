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


meter_database=[]
class Meter:
    def __init__(self,account,meter):
        self.account=account
        self.meter=meter

@app.route('/meterreading', methods=['POST'])
def add():
    
    data = request.get_json()
    account = data.get('account')
    meter= data.get('meter')
    
    if account is None or meter is None:
        return jsonify({"error": "Missing 'account' or 'meter' in request data"}), 400
    logging.info(f'Received meter data: account{account}, meter: {meter}')
    
    meter_tem=Meter(account,meter)
    meter_database.append(meter_tem)
    
    if not os.path.exists(meter_file):
        open(meter_file, 'w').close()
    
    with open(meter_file,'a') as meterdatabase :
        meterdatabase.write(f"{account},{meter}\n")
    print(meter_database)

    return {'message': 'Data received and logged successfully'}, 200


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


   
@app.route('/stopServer',methods=['GET'])
def stop_server():
    global acceptAPI
    acceptAPI=False
    acceptAPI=True
    return "Server Shutting Down"


if __name__ == '__main__':
    
    app.run(debug=True, port=5001, use_reloader=False)