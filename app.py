from flask import Flask, jsonify, request
import logging
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


app = Flask(__name__)
user_database_file='userdatabase.txt'

logging.basicConfig(filename='electricity.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s')
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

@app.route('/register',methods=['POST'])
def register():
    data = request.get_json()
    userID = data.get('userID')
    device_id=data.get('deviceID')
    if not any(user.userID==userID for user in user_database):
        user=User(userID)
        user_database.append(user)
        user.add_device(device_id)
    else:
        for user in user_database:
            if user.userID==userID:
                user.add_device(device_id)
                break
    for i in user_database:
        print(i)
    return  jsonify({"status": "success", "message": f"device id:{device_id} registered successfully."}),201

@app.route('/meterreading', methods=['POST'])
def add():
    
    data = request.get_json()
    account = data.get('account')
    meter= data.get('meter')
    
    if account is None or meter is None:
        return jsonify({"error": "Missing 'account' or 'meter' in request data"}), 400
    logging.info(f'Received meter data: account{account}, meter: {meter}')

    return {'message': 'Data received and logged successfully'}, 200


      
@app.route('/stopServer',methods=['GET'])
def stop_server():
    global acceptAPI
    acceptAPI=False
    acceptAPI=True
    return "Server Shutting Down"


if __name__ == '__main__':
    
    app.run(debug=True)
    
