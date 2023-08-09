import pandas as pd
import numpy as np

def checkHeader(line):
    headers = ['NCAA Division I Championship Meet','2023 NCAA Division I Women\'s', 'Swimming & Diving Championships',
              'Results', '(Event ', ' Team', 'Yr Name','2023 NCAA Division I Men\'s']
    for header in headers:
        if header in line:
            return True
    return False

def getRecords(lines, relay):
    newRows = []
    eventName = lines[0]
    lineCount = 1
    while lineCount < len(lines):
        x = lines[lineCount].split(':',1)
        category = x[0]
        if category not in ['NCAA','Meet','American','US Open','Pool', 'U. S. Open']:
            dfResults = pd.DataFrame(newRows)
            return lineCount, dfResults
        else:
            x = x[1].strip().split(' ')
            time = x[0]
            date = x[1][1:]
            if relay:
                team = x[2]
                swimmer = lines[lineCount+1]
            else:
                if len(x) == 5:
                    team = x[2]
                    swimmer = x[3] + ' ' + x[4]
                else:
                    swimmer = x[-1] + ' ' + x[-2]
                    team = ' '.join(x[:-2])
            dic = {'Event': eventName, 'Category': category, 'Date': date, 'Team': team, 
                   'Swimmer': swimmer, 'Time': time}
            newRows.append(dic)
        if relay:
            lineCount += 2
        else:
            lineCount += 1
    return -1, -1

def extractRelay(lines):
    if 'Event' not in lines[0]:
        print('Bad event data passed to extractRelay: '+lines[0])
        return -1
    newResults = []
    eventName = lines[0]
    lineCount = 0
    itr, newRecords = getRecords(lines, True)
    if itr == -1:
        print('Error: ', lines[0])
        return -1, -1, -1
    lineCount += itr
    lineCount += 1
    while lineCount+2 < len(lines):
        if checkHeader(lines[lineCount]):
            lineCount += 1
            continue
 
        x = lines[lineCount].strip()
        if x[:5] == 'Event' or x[:6] == 'Scores':
            dfResults = pd.DataFrame(newResults)
            dfRecords = pd.DataFrame(newRecords)
            return lineCount, dfResults, dfRecords
        x = x.split()
        place = x[-1]
        if place[0] == '*':
            place = place[1:]
        if place == '---':
            seed = x[-2]
            time = x[-3]
            j = -3
            lineCount += 1
        else:
            seed = x[-2]
            if int(place) > 16:
                points = 0
                j = -3
            else:
                points = x[-3]
                j = -4
            if x[j][-1].isnumeric():
                time = x[j]
            else:
                time = x[j][:-1]
        school = ' '.join(x[:j])
        x = lines[lineCount+1].split(') ')
        n1 = ' '.join(x[1].split()[:-2])
        yr1 = x[1].split()[-2]
        n2 = ' '.join(x[2].split()[1:-2])
        yr2 = x[2].split()[-2]
        n3 = ' '.join(x[3].split()[1:-2])
        yr3 = x[3].split()[-2]
        n4 = ' '.join(x[4].split()[1:-1])
        yr4 = x[4].split()[-1]
        dic = {'Event': eventName, 'Category': 'Timed Final Relay', 'Name1': n1, 'Year1': yr1, 
               'Name2': n2, 'Year2': yr2, 'Name3': n3, 'Year3': yr3, 'Name4': n4, 'Year4': yr4, 
               'School': school, 'QualifyingTime': seed, 'Time': time, 'Place': place, 'Points': points}
        newResults.append(dic)
        
        lineCount += 2
        while lines[lineCount].strip()[:2] == 'DQ' or lines[lineCount].strip()[:3] == 'DFS' \
              or lines[lineCount].strip()[0].isnumeric():
            lineCount += 1
    return -1, -1, -1

def extractIndividual(lines):
    if 'Event' not in lines[0]:
        print('Bad event data passed to extractIndividual: '+lines[0])
        return -1
    newResults = []
    eventName = lines[0]
    lineCount = 0
    itr, newRecords = getRecords(lines, False)
    if itr == -1:
        print('Error: ', lines[0])
        return -1, -1, -1
    lineCount += itr
    lineCount += 1
    if '1650 Yard Freestyle' in eventName:
        category = 'Timed Final Individual'
    else:
        category = lines[lineCount]
        lineCount += 1
    if 'Swim-off' in category:
        category = 'Swim-off'
#'California SO Alexy, Jack 40.88  41.42 1'
#'Stanford SR MacAlister, Leon 45.59  45.54 2'
    while lineCount < len(lines):
        if checkHeader(lines[lineCount]):
            lineCount += 1
            continue
        if lines[lineCount] in ['Championship Final','Consolation Final','Preliminaries']:
            category = lines[lineCount]
            lineCount += 1
            continue
        x = lines[lineCount].strip()
        if x[:5] == 'Event' or x[:6] == 'Scores':
            dfResults = pd.DataFrame(newResults)
            dfRecords = pd.DataFrame(newRecords)
            return lineCount, dfResults, dfRecords
        x = x.split()
        place = x[-1]
        if place[0] == '*':
            place = place[1:]
        if place == '---':
            seed = x[-2]
            time = x[-3]
            j = -3
            if time == 'DQ':
                lineCount += 1
        else:
            seed = x[-2]
            if int(place) > 16 or category == 'Preliminaries' or category == 'Swim-off':
                points = 0
                j = -3
            else:
                points = x[-3]
                j = -4
            if x[j][-1].isnumeric():
                time = x[j]
            else:
                time = x[j][:-1]
        k = 1
        while x[k] not in ['FR','SO','JR','SR','5Y']:
            k += 1
        yr1 = x[k]
        school = ' '.join(x[:k])
        n1 = ' '.join(x[k+1:j])
        dic = {'Event': eventName, 'Category': category, 'Name1': n1, 'Year1': yr1, 
               'School': school, 'QualifyingTime': seed, 'Time': time, 'Place': place, 'Points': points}
        newResults.append(dic)
        
        lineCount += 2
        if lines[lineCount].strip()[:2] == 'DQ' or lines[lineCount].strip()[:3] == 'DFS':
            lineCount += 1
        while lines[lineCount].strip()[0].isnumeric():
            lineCount += 1
    return -1, -1, -1

def extractDiving(lines):
    if 'Event' not in lines[0]:
        print('Bad event data passed to extractDiving: '+lines[0])
        return -1
    eventNum = lines[0].strip().split(' ',3)[1]
    nextEvt = str(int(eventNum) + 1)
    for lineCount in range(1,len(lines)):
        if lines[lineCount].strip()[:6+len(eventNum)] == 'Event '+eventNum or \
           lines[lineCount].strip()[:6+len(nextEvt)] == 'Event '+nextEvt:
            return lineCount
    return -1
