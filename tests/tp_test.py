#-*- coding=utf-8 -*-
import datetime
import sys
sys.path.insert(0, "../")
def convert_values(value):
    if str(value).endswith('k'):
        return str(int(str(value)[0:-1])*1000)
    elif str(value).endswith('M'):
        return str(int(str(value)[0:-1])*1000*1000)
    else:
        return str(value)
                
def get_decimals_speeds(params):
    #print "before", params
    i = 0
    for param in params:
        #values = map(convert_values, str(params[param]).split('/'))
        values = map(convert_values, str(param).split('/'))
        #print values
        params[i] ='/'.join(values)
        i += 1
    #print 'after', params
    return params

def split_speed(speed):
    return speed.split("/")

def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).
    """

    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(int(el))
    return result

def check_speed(speed):
    speed = flatten(map(split_speed,get_decimals_speeds(speed)))
    return speed[0]>speed[9] and speed[1]>speed[10] and \
    speed[2]>speed[0] and speed[3]>speed[1] and \
    speed[4]>speed[9] and speed[5]>speed[10] and speed[4]<speed[2] and speed[5]<speed[3] and speed[4]<speed[0] and speed[5]<speed[1]



from period_utilities import in_period
from period_utilities import in_period_info

data = []
#1 Каждый день
data.append((datetime.datetime(2008, 01, 01, 0,0,0), 86400, 'DAY',  [[datetime.datetime(2009, 01, 01, 2,0,1), True],
                                                                               [datetime.datetime(2009, 12, 31, 0,0,1), True],
                                                                               [datetime.datetime(2009, 02, 28, 0,0,1), True],
                                                                               [datetime.datetime(2012, 02, 29, 0,0,1), True],
                                                                               ]))
#2 Каждый понедельник
data.append((datetime.datetime(2008, 01, 07, 0,0,0), 86400, 'WEEK', [[datetime.datetime(2009, 02, 01, 10,0,12), False],
                                                                               [datetime.datetime(2009, 02, 02, 0,0,1), True],
                                                                               [datetime.datetime(2012, 02, 27, 0,0,1), True],
                                                                               [datetime.datetime(2009, 03, 16, 0,0,1), True],
                                                                               ]))
#3 Первое число каждого месяца
data.append((datetime.datetime(2008, 01, 01, 0,0,1), 86400, 'MONTH', [[datetime.datetime(2010, 01, 01, 0,0,1), True],
                                                                               [datetime.datetime(2009, 01, 02, 0,0,2), False],
                                                                               [datetime.datetime(2012, 02, 27, 0,0,1), False],
                                                                               [datetime.datetime(2009, 03, 16, 0,0,1), False],
                                                                               ]))

#4 Каждый новый год
data.append((datetime.datetime(2008, 12, 31, 0,0,0), 86400*2, 'YEAR', [[datetime.datetime(2009, 01, 01, 0,0,1), True],
                                                                               [datetime.datetime(2010, 12, 31, 01,01,01), True],
                                                                               [datetime.datetime(2010, 12, 28, 01,01,01), False],
                                                                               ]))



#print in_period_info(start, 86400,'YEAR',now)
import time

a=time.clock()

print "========testing in_period================="
for x in xrange(100000):
    for d in data:
        for n in d[3]:
            in_period(d[0], d[1], d[2], n[0])==n[1]
print time.clock()-a

print "testing in_period_info"
for d in data:
    for n in d[3]:
        print in_period_info(d[0], d[1], d[2], n[0])
        
