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

default = ""

# Open the result file 
with open(outputFileData, 'w') as res: 
    writer = csv.writer(res)
    counter = 0 
    
    # Open the file with the unlabelled flows 
    with open(inputFile, 'r') as fl: 
        reader = csv.reader(fl, delimiter=',')
        firstLine = True
        counter += 1 
        # Iterate through each line 
        for row in reader:
            # Handle header
            if firstLine == True : 
                firstLine = False
                res = []
                res.append("Day")
                res.append("Time")
                for j in range(1,14): 
                    if j == 9 or j == 11: 
                        continue 
                    res.append(row[j].strip())
                writer.writerow(res)
                continue
            # Read the values
            try: 
                date  = row[0].strip() 
                # Handle timestamp 
                datetime_object = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                # extract weekday 
                week_day = datetime_object.weekday()
                time  = row[0].strip().split(" ")[1] 
                res = [] 
                res.append(week_day)
                res.append(time) 
                for j in range(1,14): 
                    if j == 9 or j == 11: 
                        continue 
                    if j == 8: # Bytes 
                        bytzes = row[j].strip() 
                        if "M" in bytzes: 
                            bytzes = float( bytzes.split(" ")[0] )
                            bytzes = int( bytzes * 1024 * 1024 )# Conv to Bytes 
                        res.append(bytzes)
                    else: 
                        res.append(row[j].strip())
                # Write row 
                writer.writerow(res)
                
            except Exception as inst: 
                print("AUSNAHME: ", inst)
                print(row)
            
