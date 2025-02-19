from flask import Flask, jsonify, request
import logging
import os


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

    for field in ["device", "date", "time", "meter"]:
        if field not in req_data:
            return jsonify({"message": f"Missing field: {field}"}), 400

    device = req_data["device"]
    date = req_data["date"]
    time_slot = req_data["time"]
    meter = req_data["meter"]

    # Check whether the device exists
    existing_meter = next((m for m in meter_database if m.device_id == device), None)

    if existing_meter is None: # Add new device and data
        new_meter = Meter(device)
        new_meter.add_reading(date, time_slot, meter)
        meter_database.append(new_meter)
    else:
        existing_meter.add_reading(date, time_slot, meter) # update data for existing device

    for m in meter_database:
        print(m)

    return jsonify({m.device_id: m.get_readings() for m in meter_database}), 200


# ----------------------------------- Stop Server ---------------------------------------------
@app.route('/stopServer',methods=['GET'])
def stop_server():
    global acceptAPI
    global user_database
    acceptAPI=False
    userDataBackUp(user_database)
    user_database=[]

    acceptAPI=True
    return "Server Shutting Down"

# meter backup test
@app.route('/backup', methods=['GET', 'POST'])
def stopserver():
    if not meter_database:
        return jsonify({"message": "Nothing needs to backup！"}), 400  # deal with empty data
    meterDataBackup(meter_database)
    return jsonify({"message": "Backup Completed!"}), 200


# --------------------------------- Backup Define ---------------------------------------------

# User Data Backup
def userDataBackUp(user_database):
    with open('userdatabase.txt', 'w', encoding='utf-8') as f:
        for user in user_database:
            userstr=user.userID+','+",".join(user.get_device_id())+'\n'
            f.write(userstr)
    print("Backup completed!") 

# Meter Readings Backup
def meterDataBackup(meter_database):
    file_name = 'meterdatabase.txt'

    if not os.path.exists(file_name) or os.path.getsize(file_name) == 0:
        mode = 'w'
    else:
        mode = 'a'

    with open(file_name, mode, encoding='utf-8') as f:
        if mode == 'w':
            f.write("DeviceID, Date, Final_Daily_Readings, Daily_Consumption\n")
        
        for meter in meter_database:
            readings = meter.readings
            sorted_dates = sorted(readings.keys())
            
            if len(sorted_dates) < 2:
                continue  # if the device data < 2, cannot calculate the consumption

            for i in range(len(sorted_dates) - 1):
                current_date = sorted_dates[i]
                next_date = sorted_dates[i + 1]

                # ensure current and next date both have '00:00' readings
                if "00:00" not in readings[current_date] or "00:00" not in readings[next_date]:
                    continue
                
                final_reading = readings[next_date]["00:00"]  # current final reading = next date 00:00 reading
                daily_consumption = round(final_reading - readings[current_date]["00:00"],1)
                
                f.write(f"{meter.device_id}, {current_date}, {final_reading}, {daily_consumption}\n")
    print("Backup completed!")


# --------------------------------- Recover Define ---------------------------------------------
def userDataRecover(user_database):
    with open('userdatabase.txt', 'r', encoding='utf-8') as f: 
        for line in f:
            data=line.split(',')
            user=User(data[0])
            data.pop(0)
            for i in data:
                user.add_device(i)
            user_database.append(user)
def eleDataRecover(meter_database):
    with open('electricity.txt','r',encoding='utf-8') as f:
        

userDataRecover(user_database)


# ----------------------------------- Run ---------------------------------------------
if __name__ == '__main__':
    app.run(debug=False)