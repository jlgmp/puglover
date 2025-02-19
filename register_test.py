import requests

def user_register():
    data = {'userID': '7771', 'deviceID':'224-333-662'}
    response = requests.post('http://127.0.0.1:5000/register', json=data)
    

if __name__=='__main__':
    #user_register()
    response=requests.get('http://127.0.0.1:5000/stopServer')
