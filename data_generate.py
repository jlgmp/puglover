import datetime
import random

start_date = datetime.date(2024, 11, 11)  
end_date = datetime.date(2025, 2, 19)  




with open('meterDatabase.txt','w',encoding='utf-8') as f:
    f.write("DeviceID,Date,Final_Daily_Readings,Daily_Consumption\n")
    for i in range(1,10):
        device=f"{i}{i}{i}"+'-'+f"{i}{i}{i}"+'-'+f'{i}{i}{i}'
        current_date = start_date
        read=random.uniform(100.1,1000.4)
        read=round(read,1)
        while current_date <= end_date:
        
            date = current_date.strftime('%Y-%m-%d')
            consumption=random.uniform(4.1,16.6)
            consumption=round(consumption,1)
            read+=consumption
            
            
            f.write(f"{device},{date},{read:.1f},{consumption}\n")
            current_date += datetime.timedelta(days=1)
