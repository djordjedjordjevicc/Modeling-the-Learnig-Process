import pandas as pd
import datetime
import time

column_names = ['brind','startT','endT','commTime','commStart','commEnd']
dataset = pd.read_csv('Sensor2_data.csv', sep=',',header=None,names=column_names)


stayDurations = dataset[['brind','startT','endT']].dropna().reset_index(drop=True)
commDurations = dataset[['brind','commStart','commEnd']].dropna().reset_index(drop=True)
commMoments = dataset[['brind','commTime']].dropna().reset_index(drop=True)

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

    startTimes = list(map(lambda x: datetime.datetime.strptime(x,'%Y-%m-%d %H:%M:%S'), originalData['startT']))
    minStart = min(startTimes)

    endTimes = list(map(lambda x: datetime.datetime.strptime(x,'%Y-%m-%d %H:%M:%S'), originalData['endT']))
    maxEnd = max(endTimes)

    
    minStart = minStart.strftime('%Y-%m-%d %H:%M:%S')
    maxEnd = maxEnd.strftime('%Y-%m-%d %H:%M:%S')
    new_row = pd.DataFrame({'brind':[originalData['brind'].values[0]], 'startT':[minStart], 'endT':[maxEnd]})
   
    stayDurations = pd.concat([stayDurations, new_row]).reset_index(drop=True)

def placeDurationsToCsv():
    for x in stayDurations['brind']:
        multipleStays = getStudentDays(x)
        if not multipleStays:
            continue
        for stay in multipleStays:
            replaceInput(stayDurations, list(stay.index.values))

    stayDurations.to_csv('stayDurationsS2.csv', index=False)

column_names = ['brind','startT','endT']
durations = pd.read_csv('stayDurationsS2.csv', sep=',',header=None,names=column_names)

def expandStayDurations():
    for index in durations.index:
        brind = str(durations['brind'][index])
        startT = str(durations['startT'][index])
        endT = str(durations['endT'][index])

        startTDay = startT.split(' ')[0]

        comm_moments = commDurations[commDurations['brind'].str.contains(brind) & commDurations['commStart'].str.contains(startTDay)]

        for comm_moment in comm_moments['commStart']:

            commStartTime = datetime.datetime.strptime(comm_moment,'%Y-%m-%d %H:%M:%S')
            arrivalTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S')

            commTimeSec = (commStartTime - arrivalTime).total_seconds()
            
            if (commTimeSec <= 0):
                durations.loc[index, 'startT'] = commStartTime

        for comm_moment in comm_moments['commEnd']:

            commEndTime = datetime.datetime.strptime(comm_moment,'%Y-%m-%d %H:%M:%S')
            leaveTime = datetime.datetime.strptime(endT,'%Y-%m-%d %H:%M:%S')

            commTimeSec = (leaveTime - commEndTime).total_seconds()

            if (commTimeSec <= 0):
                durations.loc[index, 'endT'] = commEndTime

    durations.to_csv('expandedStayDurationsS2.csv', index=False)

def getAbsoluteTime():
    time_list = []
    for index in durations.index:
        brind = str(durations['brind'][index])
        startT = str(durations['startT'][index])

        startTDay = startT.split(' ')[0]

        comm_moments = commDurations[commDurations['brind'].str.contains(brind) & commDurations['commStart'].str.contains(startTDay)]

        for comm_moment in comm_moments['commStart']:

            commStartTime = datetime.datetime.strptime(comm_moment,'%Y-%m-%d %H:%M:%S')
            arrivalTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S')

            commTimeSec = (commStartTime - arrivalTime).total_seconds()

            if (commTimeSec <= 0):
                commTimeSec = 0.1

            time_list.append(commTimeSec)

        #-----Trenuci uzeti za start-----#
        comm_occurrence = commMoments[commMoments['brind'].str.contains(brind) & commMoments['commTime'].str.contains(startTDay)]
        for comm_moment in comm_occurrence['commTime']:

            commStartTime = datetime.datetime.strptime(comm_moment,'%Y-%m-%d %H:%M:%S')
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

        newStartTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S')
        newEndTime = datetime.datetime.strptime(endT,'%Y-%m-%d %H:%M:%S')

        staySec = (newEndTime - newStartTime).total_seconds()
        if staySec <= 0:
            continue

        startTDay = startT.split(' ')[0]

        comm_moments = commDurations[commDurations['brind'].str.contains(brind) & commDurations['commStart'].str.contains(startTDay)]

        for comm_moment in comm_moments['commStart']:

            commStartTime = datetime.datetime.strptime(comm_moment,'%Y-%m-%d %H:%M:%S')
            arrivalTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S')

            commTimeSec = (commStartTime - arrivalTime).total_seconds()


            if (commTimeSec <= 0):
                commTimeSec = 0.1

            commPercent = commTimeSec*100/staySec

            #time_list.append(brind)
            time_list.append(commPercent)

        #-----Trenuci uzeti za start-----#
        comm_occurrence = commMoments[commMoments['brind'].str.contains(brind) & commMoments['commTime'].str.contains(startTDay)]
        for comm_moment in comm_occurrence['commTime']:

            commStartTime = datetime.datetime.strptime(comm_moment,'%Y-%m-%d %H:%M:%S')
            arrivalTime = datetime.datetime.strptime(startT,'%Y-%m-%d %H:%M:%S')

            commTimeSec = (commStartTime - arrivalTime).total_seconds()

            if (commTimeSec <= 0):
                commTimeSec = 0.1

            commPercent = commTimeSec*100/staySec

            #time_list.append(brind)
            time_list.append(commPercent)

    return time_list


#time_list = getAbsoluteTime()

# with open('commStartAbsS2.txt', 'w') as fp:
#     fp.write("\n".join(str(item) for item in time_list))

# with open('commStartAbsMomSTS2.txt', 'w') as fp:
#     fp.write("\n".join(str(item) for item in time_list))


time_list = getRelativeTime()

# with open('commStartRelS2.txt', 'w') as fp:
#     fp.write("\n".join(str(item) for item in time_list))

with open('commStartRelMomSTS2.txt', 'w') as fp:
    fp.write("\n".join(str(item) for item in time_list))