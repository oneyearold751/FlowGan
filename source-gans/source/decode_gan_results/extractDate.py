# Imports
import csv 
import sys
from datetime import datetime
import time
from random import randint
import math 
import numpy as np 
import math 
import tensorflow as tf
import os 


# Path to data
inputFile = sys.argv[1]
outputFileData = sys.argv[2] 


perHour = dict() 
counter = 0 
with open(inputFile, 'r') as fl: 
    reader = csv.reader(fl, delimiter=',')
    first = True
    # Iterate through each line 
    for row in reader:
        if first == True: 
            first = False
            continue 
        day = int( row[0] ) 
        hour = datetime.strptime(row[1], '%H:%M:%S.%f').hour 
        h = day * 24 + hour 
        counter += 1 
        if h in perHour: 
            v = perHour[h] 
            v += 1 
            perHour[h] = v 
        else: 
            perHour[h] = 1 

with open(outputFileData, 'w') as res: 
    writer = csv.writer(res)
    for i in range(0,168): 
        if i not in perHour: 
            perHour[i] = 0
        print(i, " ", perHour[i]) 
        line = [] 
        line.append(i)
        line.append(perHour[i])
        v = float( perHour[i] ) 
        line.append( v/counter ) 
        writer.writerow(line)

   