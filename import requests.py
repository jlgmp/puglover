import requests

def user_register():
    username=input("Pls input your username")
    password=input("Pls input your password")
    id=input("Pls input your device id")
    data = {'username': username, 'password':password,'id':id}
    response = requests.post('http://127.0.0.1:5000/register', json=data)
    data1=response.json()
    print(data1['message'])

if __name__=='__main__':
    user_register()