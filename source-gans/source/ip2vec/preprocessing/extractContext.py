# Imports
import csv 
import sys
import pandas as pd 
from datetime import datetime

# Path to data
inputFile = sys.argv[1]
outputFileData = sys.argv[2]  

# Open the result file 
with open(outputFileData, 'w') as res: 
    writer = csv.writer(res)
    
    # Open the file with the unlabelled flows 
    with open(inputFile, 'r') as fl: 
        reader = csv.reader(fl, delimiter=',')
        firstLine = True
        # Iterate through each line 
        for row in reader:
            # Handle header
            if firstLine == True : 
                writer.writerow(["srcIP","srcPt","dstIP","dstPt","proto","packets","bytes","duration"])
                firstLine = False
                continue
            # Read the values
            try: 
                proto = row[3].strip()

                srcIP = row[4].strip()
                srcPt = row[5].strip()+"_p"
                
                dstIP = row[6].strip()
                dstPt = row[7].strip()+"_p"

                bytez = row[9].strip() + "_b" 
                packets = row[8].strip() + "_k"
                duration = row[2].strip() + "_d"

                writer.writerow([srcIP,srcPt,dstIP,dstPt,proto,packets,bytez,duration])
                
            except Exception as inst: 
                print(len(row))
                
