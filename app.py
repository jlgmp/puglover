from flask import Flask, jsonify, request
import logging
import pandas as pd
import datetime


app = Flask(__name__)

logging.basicConfig(filename='electricity.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

acceptAPI=True
# --------------------------------- Register ---------------------------------------------

# Define Class User
global user_database
user_database=[]

class User:
    def __init__(self,userID):
        self.userID=userID
        self.device_id_list=[]
    def add_device(self,device_id):
        self.device_id_list.append(device_id)
    def get_device_id(self):
        return self.device_id_list
    def __str__(self):
        return f"User:{self.userID} device_list:{self.device_id_list}"

# Define Register Function
@app.route('/register',methods=['POST'])
def register():
    global user_database
    data = request.get_json()
    userID = data.get('userID')
    device_id=data.get('deviceID')
    if not user_database:
        user=User(userID)
        user.add_device(device_id)
        user_database.append(user)
    if not any(user.userID==userID for user in user_database):
        user=User(userID)
        user.add_device(device_id)
        user_database.append(user)
    else:
        for user in user_database:
            if user.userID==userID and device_id not in user.get_device_id():
                user.add_device(device_id)
                break
    '''for i in user_database:
        print(i)'''
    return  jsonify({"status": "success", "message": f"device id:{device_id} registered successfully."})


# ----------------------------------- Meter Reading ---------------------------------------------

# Define Class Meter
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

# Define meterreading function
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

    existing_meter = next((m for m in meter_database if m.device_id == device), None)

    if existing_meter is None:
        new_meter = Meter(device)
        new_meter.add_reading(time_slot, meter)
        meter_database.append(new_meter)
    else:
        existing_meter.add_reading(time_slot, meter)

    #for m in meter_database:
    #    print(m)

    return jsonify({m.device_id: m.get_readings() for m in meter_database}), 200


# ----------------------------------- Stop Server ---------------------------------------------
@app.route('/stopServer',methods=['GET'])
def stop_server():
    global acceptAPI
    global user_database, meter_database
    acceptAPI=False
    userDataBackUp(user_database)
    user_database=[]
    if not user_database:
        userDataRecover(user_database)
    meterDataBackup(meter_database)
    acceptAPI=True
    return "Server Shutting Down"

# meter backup test
#@app.route('/backup', methods=['GET', 'POST'])
#def stopserver():
#    if not meter_database:
#        return jsonify({"message": "Nothing needs to backup！"}), 400  # deal with empty data
#    meterDataBackup(meter_database)
#    return jsonify({"message": "Backup Completed!"}), 200


# --------------------------------- Backup Define ---------------------------------------------

# User Data Backup
def userDataBackUp(user_database):
    with open('userDatabase.txt', 'w', encoding='utf-8') as f:
        for user in user_database:
            userstr=user.userID+','+",".join(user.get_device_id())
            f.write(userstr+'\n')
    print("Backup completed!") 

# Meter Readings Backup
def meterDataBackup(meter_database):
    file_name = 'meterDatabase.txt'
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


# --------------------------------- Recover Define ---------------------------------------------
def userDataRecover(user_database):
    with open('userDatabase.txt', 'r', encoding='utf-8') as f: 
        for line in f:
            line=line.strip()
            data=line.split(',')
            user=User(data[0])
            data.pop(0)
            for i in data:
                user.add_device(i)
            user_database.append(user)
'''def eleDataRecover(meter_database):
    with open('meterDatabase.txt','r',encoding='utf-8') as f:
        '''




# ----------------------------------- Run ---------------------------------------------
if __name__ == '__main__':
    app.run(debug=False)