import random
import requests


def generate_half_hour_times():
    time_list = []
    for hour in range(1, 24):
        for minute in [0, 30]:
            time_list.append(f"{hour:02d}:{minute:02d}")
    
    # 额外补上 24:00（因为 24:30 并不常用，也不算一天的合法时间）
    time_list.append("24:00")
    
    return time_list

if __name__ == "__main__":
    times = generate_half_hour_times()
    for i in range(1,3):
        device=f"{i}{i}{i}"+'-'+f"{i}{i}{i}"+'-'+f'{i}{i}{i}'
        meter=random.uniform(10.1,30.1)
        meter=round(meter,1)
        for t in times:
            time=t
            hour_con=random.uniform(0.3,0.45)
            hour_con=round(hour_con,1)
            meter+=hour_con

            data = {'device':f"{device}", "time":f"{time}",'meter':f"{meter}"}
            response = requests.post('http://127.0.0.1:5000/meterreading', json=data)

                