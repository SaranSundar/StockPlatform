"""Criteria: Total Area %, Number of days up or down."""
"""
Ascending or descending overall and head
"""
import pandas as pd


def apply_search_criteria(data_stocks: list, criteria: str):
    global currentStock
    print(criteria)
    output = dict()
    keys = list(data_stocks.keys())
    for k in keys:
        #print(data_stocks[k][0]['symbol'])
        currentStock = data_stocks[k]
        if(eval(criteria)):
            #print("pass")
            output[k] = data_stocks[k]
    return output

"""
These functions are designed to be terminals
"""

def window(start: str, stop: str, field: str):
    startNum = date_to_int(start)
    stopNum = date_to_int(stop)
    includedKeys = list()
    for k in currentStock[2].keys():
        thisdate = date_to_int(k)
        if(thisdate >= startNum and thisdate <= stopNum):
            includedKeys.append((thisdate, k))
    #sort the list of keys
    includedKeys = sorted(includedKeys, key=lambda x: x[0])
    valueList = list()
    for k in includedKeys:
        valueList.append(currentStock[2][k[1]][field])
    return valueList
    
def getTrend(valueList):
    if len(valueList) == 0:
         return 0
    def fitness(m, b, l):
        res = 0
        for x in range(0, len(l)-1):
            res+=((m*x+b)-l[x])**2
        return res
    def test(s):
        return fitness(s, avg-s*len(valueList)/2, valueList)
    avg = 0
    for x in valueList:
        avg+=x
    avg/=len(valueList)
    low = -1
    high = 1
    while test(low*2) < test(low):
        low*=2
    while test(high*2) < test(high):
        high*=2
    #print("high: " + str(high))
    #print("low: " + str(low))
    slope = high+low/2
    diff = high+low/4
    for x in range(0, 15): #iterate
        up = test(slope+diff)
        down = test(slope-diff)
        if(up < down):
            slope+=diff
        else:
            slope-=diff
        diff/=2
    #print(slope)
    return slope

def getSector():
    return currentStock[1]['sector']

"""
These functions are internal to the search
"""

def date_to_int(date: str):
    return int("".join(date.split("-")))
    

def get_average(data):
    count = data.size
    total = 0
    for val in data:
        total += val
    total /= count
    return total

def get_delta(data):
    deltas = list()
    prev = 0
    for val in data:
        deltas.append(val-prev)
        prev = val
    deltas.pop(0)
    return pd.Series(deltas)

#print(getTrend([0, -0.1, -0.2, -0.3, -0.4, -0.5, -0.6]))

