import requests

def meter_reading():
    account=input("Pls input your account")
    meter=input("Pls input your meter")

    data = {'account': account, 'meter':meter}
    response = requests.post('http://127.0.0.1:5001/meterreading', json=data)
    data=response.json()
    print(data['message'])

if __name__=='__main__':
    meter_reading()