# Imports
import csv 
import sys
import random
from datetime import datetime
import time
from random import randint
        

# Path to data
inputFile = sys.argv[1]
outputFileData = sys.argv[2] 
numExamples = int( sys.argv[3] ) 

values = []  
length1 = -1 
length2 = 0

# Open the file with the unlabelled flows 
with open(inputFile, 'r') as fl: 
    reader = csv.reader(fl, delimiter=',')
    firstLine = True
    # Iterate through each line 
    for row in reader:
        # Handle header
        if firstLine == True : 
            firstLine = False
            length1 = len(row) 
            for r in row:
                lst = []  
                values.append(lst) 
            continue

        for i in range(0,length1):  
            v = row[i].strip() 
            values[i].append(v) 
        length2 += 1 


# Generate new data 
with open(outputFileData, 'w') as res: 
    writer = csv.writer(res)

    for i in range(0,numExamples): 
        res = [] 
        for j in range(0,length1): 
            index = random.randint(0,length2-1)
            val = values[j][index] 
            res.append(val) 
        writer.writerow(res)

    






    