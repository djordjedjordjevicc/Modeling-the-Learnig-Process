import pandas as pd
import datetime
import time

column_names = ['brind','startT','endT','stayDuration','commDuration']
dataset = pd.read_csv('Sensor1_data.csv', sep=',',header=None,names=column_names)

refined = dataset[['brind','commDuration']].dropna()

comm_time = refined['commDuration'].tolist()

def time_to_sec(duration):
    if '.' in duration:
        x = datetime.datetime.strptime(duration,'%H:%M:%S.%f')
        a_timedelta = x - datetime.datetime(1900, 1, 1)
        return a_timedelta.total_seconds()
    else:
        x = time.strptime(duration,'%H:%M:%S')

        return datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()

comm_time_to_sec = list(map(time_to_sec, comm_time[1:]))
comm_time_to_sec = list(filter(lambda x : x > 0, comm_time_to_sec))

with open('commDurationS1.txt', 'w') as fp:
    fp.write("\n".join(str(item) for item in comm_time_to_sec))