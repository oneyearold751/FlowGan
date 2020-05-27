# Imports
import csv 
import sys
from datetime import datetime
import time
from random import randint
import math 
import numpy as np 
import math 


# Path to data
inputFileGen = sys.argv[1]
inputFileOrg = sys.argv[2]


# Structure of input attributes 
id_time  = 0
id_day   = 1
id_dur   = 2
id_proto = 3
id_srcIP = 4 
id_srcPt = 5
id_dstIP = 6
id_dstPt = 7
id_packets=8
id_bytzes= 9 
id_flags = 10 
id_clazz = 11
id_attacktype = 12 

length_attributes = 12

gen_flows = [] 
num_gen_flows = -1.0
for i in range(0,length_attributes): 
    gen_flows.append(dict())

org_flows = [] 
num_org_flows = -1.0
for i in range(0,length_attributes): 
    org_flows.append(dict()) 



counter = 0 
# Open the file of generated flows 
with open(inputFileGen, 'r') as fl: 
    reader = csv.reader(fl, delimiter=',')
    # Iterate through each line 
    for row in reader:
        # Read the values
        counter += 1 
        if counter % 100000 == 0: 
            print("Reading generated Flows: ", str(counter))

        for id in range(0,length_attributes): 
            val = row[id].strip() 
            # Duration 
            if id == 2: 
                if "." in val: 
                    l = len( val.split(".")[1] ) 
                    for r in range(l,3): 
                        val = val + "0"
                else: 
                    val = val + ".000"
            if val in gen_flows[id]: 
                count = gen_flows[id][val]
                count += 1 
                gen_flows[id][val] = count
            else: 
                gen_flows[id][val] = 1 
num_gen_flows = float(counter)


counter = 0
# Open the file of original flows 
with open(inputFileOrg, 'r') as fl2: 
    reader2 = csv.reader(fl2, delimiter=',')
    firstLine = True
    # Iterate through each line 
    for row in reader2:
        # Handle header
        if firstLine == True : 
            firstLine = False
            continue
        # Read the values
        counter += 1 
        if counter % 100000 == 0: 
            print("Reading original Flows: ", str(counter))

        for id in range(0,length_attributes): 
            val = row[id].strip() 
            if val in org_flows[id]: 
                count = org_flows[id][val]
                count += 1 
                org_flows[id][val] = count
            else: 
                org_flows[id][val] = 1 
num_org_flows = float(counter)


print("Finished Reading!")    
print("Start calculating distances") 
for i in range(0,length_attributes): 
    gen_dict = gen_flows[i]
    org_dict = org_flows[i]

    dist = 0 
    for key in org_dict: 
        v1 = org_dict[key]
        v1 /= num_org_flows
        v2 = 0
        if key in gen_dict: 
            v2 = gen_dict[key]
            v2 /= num_gen_flows
        d = v1 - v2 
        dist = dist + (d*d)
    
    for key in gen_dict: 
        if key not in org_dict: 
            v2 = gen_dict[key]
            v2 /= num_gen_flows
            dist = dist + (v2*v2)

    print("Distance in Attribute ", i, ":", math.sqrt(dist) )