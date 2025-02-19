import datetime
import random


start_date = datetime.date(2024, 11, 11)  
end_date = datetime.date.today() - datetime.timedelta(days=1)


device_ids = set()  
while len(device_ids) < 20:
    part1 = str(random.randint(100, 999))  
    part2 = str(random.randint(100, 999))
    part3 = str(random.randint(100, 999))
    device_id = f"{part1}-{part2}-{part3}"
    device_ids.add(device_id)  

with open("userDatabase.txt", "w") as f:
    for device_id in device_ids:
        f.write(device_id + "\n")


with open('meterDatabase.txt','w') as f:
    f.write("DeviceID,Date,Final_Daily_Readings,Daily_Consumption\n")
    for device in device_ids:
        current_date = start_date
        read = round(random.uniform(100.1, 1000.4), 1)  

        while current_date <= end_date:
            date = current_date.strftime('%Y-%m-%d')
            consumption = round(random.uniform(4.1, 16.6), 1)  
            read += consumption  
            
            f.write(f"{device},{date},{read:.1f},{consumption}\n")
            current_date += datetime.timedelta(days=1)