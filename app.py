from flask import Flask, jsonify, request
import logging
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


app = Flask(__name__)
user_database_file='userdatabase.txt'

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
    with open(user_database_file,'a') as userdatabase :
        userdatabase.write(f"{username},{password},{device_id}\n")
    print(user_database)
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
    
