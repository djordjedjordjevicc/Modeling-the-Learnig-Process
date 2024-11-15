import pandas as pd
import datetime

column_names = ['brind','startT','endT','stayDuration','commDuration']
dataset = pd.read_csv('Sensor1_data.csv', sep=',',header=None,names=column_names)

stayDurations = dataset[['brind','startT','endT','stayDuration']].dropna().reset_index(drop=True)
commDurations = dataset[['brind','startT','endT','commDuration']].dropna().reset_index(drop=True)

def getStudentDays(index):
    student_stay = stayDurations.where(stayDurations['brind'] == index).dropna()
    days = [(x.split(' ')[0]) for x in student_stay['startT'].tolist()]

    duplicates = list(set([day for day in days if days.count(day) > 1]))

    daysData = []
    for day in duplicates:
        dayData = stayDurations[stayDurations['startT'].str.contains(day) & stayDurations['brind'].str.contains(index)]
        daysData.append(dayData)

    return daysData

def replaceInput(stayDurationsTemp, indexes):
    originalData = stayDurationsTemp.loc[indexes]

    global stayDurations
    for index in indexes:
        stayDurations.drop([index], axis=0, inplace=True)

    startTimes = list(map(lambda x: datetime.datetime.strptime(x,'%Y-%m-%d %H:%M:%S.%f'), originalData['startT']))
    minStart = min(startTimes)

    endTimes = list(map(lambda x: datetime.datetime.strptime(x,'%Y-%m-%d %H:%M:%S.%f'), originalData['endT']))
    maxEnd = max(endTimes)

    stayDuration = str(maxEnd - minStart)

    
    minStart = minStart.strftime('%Y-%m-%d %H:%M:%S.%f')
    maxEnd = maxEnd.strftime('%Y-%m-%d %H:%M:%S.%f')
    new_row = pd.DataFrame({'brind':[originalData['brind'].values[0]], 'startT':[minStart], 'endT':[maxEnd], 'stayDuration':[stayDuration]})
   
    stayDurations = pd.concat([stayDurations, new_row]).reset_index(drop=True)

def placeDurationsToCsv():
    for x in stayDurations['brind']:
        multipleStays = getStudentDays(x)
        if not multipleStays:
            continue
        for stay in multipleStays:
            replaceInput(stayDurations, list(stay.index.values))

    stayDurations.to_csv('stayDurationsS1.csv', index=False)

column_names = ['brind','startT','endT','stayDuration']
durations = pd.read_csv('expandedStayDurationsS1.csv', sep=',',header=None,names=column_names)


def expandStayDurations():
    for index in durations.index:
        brind = str(durations['brind'][index])
        startT = str(durations['startT'][index])
        endT = str(durations['endT'][index])
        stayDuration = str(durations['stayDuration'][index])

        startTDay = startT.split(' ')[0]

        comm_moments = commDurations[commDurations['brind'].str.contains(brind) & commDurations['startT'].str.contains(startTDay)]

        for comm_moment in comm_moments['startT']:

            if '.' in comm_moment:
                commStartTime = datetime.datetime.strptime(comm_moment,'%Y-%m-%d %H:%M:%S.%f')
            else:
                commStartTime = datetime.datetime.strptime(comm_moment,'%Y-%m-%d %H:%M:%S')

            if '.' in startT:
                arrivalTime = datetime.datetime.strptime(str(durations.loc[index, 'startT']),'%Y-%m-%d %H:%M:%S.%f')
            else:
                arrivalTime = datetime.datetime.strptime(str(durations.loc[index, 'startT']),'%Y-%m-%d %H:%M:%S')

            commTimeSec = (commStartTime - arrivalTime).total_seconds()
            
            if (commTimeSec <= 0):
                durations.loc[index, 'startT'] = commStartTime

        for comm_moment in comm_moments['endT']:

            commEndTime = datetime.datetime.strptime(comm_moment,'%Y-%m-%d %H:%M:%S.%f')

            if '.' in endT:
                leaveTime = datetime.datetime.strptime(endT,'%Y-%m-%d %H:%M:%S.%f')
            else:
                leaveTime = datetime.datetime.strptime(endT,'%Y-%m-%d %H:%M:%S')

            commTimeSec = (leaveTime - commEndTime).total_seconds()

            if (commTimeSec <= 0):
                durations.loc[index, 'endT'] = commEndTime

        #print(durations['endT'][index])

        startT = str(durations['startT'][index])
        endT = str(durations['endT'][index])

        if '.' in startT:
            newStartTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S.%f')
        else:
            newStartTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S')

        if '.' in endT:
            newEndTime = datetime.datetime.strptime(endT,'%Y-%m-%d %H:%M:%S.%f')
        else:    
            newEndTime = datetime.datetime.strptime(endT,'%Y-%m-%d %H:%M:%S')

        newStayDuration = str(newEndTime - newStartTime)#.strftime('%H:%M:%S.%f')
        durations['stayDuration'] = durations['stayDuration'].replace([stayDuration], newStayDuration)
    
    durations.to_csv('expandedStayDurationsS1.csv', index=False)


def getAbsoluteTime():
    time_list = []
    for index in durations.index:
        brind = str(durations['brind'][index])
        startT = str(durations['startT'][index])

        startTDay = startT.split(' ')[0]

        comm_moments = commDurations[commDurations['brind'].str.contains(brind) & commDurations['startT'].str.contains(startTDay)]

        for comm_moment in comm_moments['startT']:

            if '.' in comm_moment:
                commStartTime = datetime.datetime.strptime(comm_moment,'%Y-%m-%d %H:%M:%S.%f')
            else:
                commStartTime = datetime.datetime.strptime(comm_moment,'%Y-%m-%d %H:%M:%S')

            if '.' in startT:
                arrivalTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S.%f')
            else:
                arrivalTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S')

            commTimeSec = (commStartTime - arrivalTime).total_seconds()

            if (commTimeSec <= 0):
                commTimeSec = 0.1

            time_list.append(commTimeSec)

    return time_list

def getRelativeTime():
    time_list = []
    for index in durations.index:
        brind = str(durations['brind'][index])
        startT = str(durations['startT'][index])
        endT = str(durations['endT'][index])

        if '.' in startT:
            newStartTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S.%f')
        else:
            newStartTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S')

        if '.' in endT:
            newEndTime = datetime.datetime.strptime(endT,'%Y-%m-%d %H:%M:%S.%f')
        else:    
            newEndTime = datetime.datetime.strptime(endT,'%Y-%m-%d %H:%M:%S')

        staySec = (newEndTime - newStartTime).total_seconds()

        startTDay = startT.split(' ')[0]

        comm_moments = commDurations[commDurations['brind'].str.contains(brind) & commDurations['startT'].str.contains(startTDay)]

        for comm_moment in comm_moments['startT']:

            commStartTime = datetime.datetime.strptime(comm_moment,'%Y-%m-%d %H:%M:%S.%f')

            if '.' in startT:
                arrivalTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S.%f')
            else:
                arrivalTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S')

            commTimeSec = (commStartTime - arrivalTime).total_seconds()

            if (commTimeSec <= 0):
                commTimeSec = 0.1

            commPercent = commTimeSec*100/staySec

            if (commPercent > 100):
                print(brind)
                print(commPercent)
                print(commTimeSec)

            time_list.append(commPercent)

    return time_list



#expandStayDurations()

# time_list = getAbsoluteTime()

# with open('commStartAbsS1.txt', 'w') as fp:
#     fp.write("\n".join(str(item) for item in time_list))

time_list = getRelativeTime()

with open('commStartRelS1.txt', 'w') as fp:
    fp.write("\n".join(str(item) for item in time_list))

#placeDurationsToCsv()