import pandas as pd
import datetime

column_names = ['brind','startT','endT','commTime','commStart','commEnd']
dataset = pd.read_csv('Sensor2_data.csv', sep=',',header=None,names=column_names)

commDurations = dataset[['brind','commStart','commEnd']].dropna().reset_index(drop=True)

durationTimes = []

for index in commDurations.index[1:]:
    startT = datetime.datetime.strptime(commDurations['commStart'][index],'%Y-%m-%d %H:%M:%S')
    endT = datetime.datetime.strptime(commDurations['commEnd'][index],'%Y-%m-%d %H:%M:%S')

    commTime = (endT - startT).total_seconds()
    durationTimes.append(commTime)

with open('commDurationS2.txt', 'w') as fp:
    fp.write("\n".join(str(item) for item in durationTimes))