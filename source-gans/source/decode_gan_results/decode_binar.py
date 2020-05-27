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

os.environ["CUDA_VISIBLE_DEVICES"]="1"

# Path to data
inputFile = sys.argv[1]
inputFileOrig = sys.argv[2]
outputFileData = sys.argv[3] 


# Open the file with the unlabelled flows 
mins = [99999.9,99999.9,99999.9] 
maxs = [-1.0,-1.0,-1.0] 
with open(inputFileOrig, 'r') as fl: 
    reader = csv.reader(fl, delimiter=',')
    firstLine = True
    # Iterate through each line 
    for row in reader:
        # Handle header
        if firstLine == True : 
            firstLine = False
            continue

        # Read the values
        duration = float( row[2].strip() )

        if duration > 10000: 
            continue

        if duration > maxs[0]: 
            maxs[0] = duration
        if duration < mins[0]: 
            mins[0] = duration 


# Open the result file 
with open(outputFileData, 'w') as res: 
    writer = csv.writer(res)
    
    # Open the file with the generated flows 
    with open(inputFile, 'r') as fl: 
        reader = csv.reader(fl, delimiter=',')
        for row in reader:
            # Read the values
            try: 
                rl = [] 

                # Read the day 
                d_id = np.array(row[0:7],dtype=np.float32).argmax() 
                rl.append(d_id)

                # daytime 
                seconds = float(row[7].strip()) * 86400 
                if seconds < 0: 
                    seconds += 86400 
                if seconds > 86399: 
                    seconds = seconds % 86400
                h = int( seconds / 3600 ) 
                m = int( (seconds-(h*3600)) / 60 ) 
                s = int( (seconds-(h*3600)-(m*60)) ) 
                rl.append(str(h)+":"+str(m)+":"+str(s))

                # duration 
                duration = ( ((float(row[8].strip())))*(maxs[0]-mins[0])-mins[0] ) 
                rl.append(format(duration,".3f"))  

                # proto 
                p_id = np.array(row[9:12],dtype=np.float32).argmax() 

                if p_id == 0: 
                    rl.append("ICMP")
                if p_id == 1: 
                    rl.append("UDP")
                if p_id == 2: 
                    rl.append("TCP")

                # Source IP 
                sip = "" 
                tmp = "" 
                for i in range(12,44): 
                    f = float(row[i])
                    r = 1
                    if f < 0.5: 
                        r = 0 
                    tmp += str(r) 
                    if i==19 or i==27 or i==35 or i==43: 
                        val = int(tmp,2) 
                        if i < 40:
                            sip += str(val) + "."
                        else: 
                            sip += str(val)
                        tmp = ""
                rl.append(sip)

                # Source Port 
                tmp = ""
                for i in range(44,60): 
                    f = float(row[i])
                    r = 1
                    if f < 0.5: 
                        r = 0 
                    tmp += str(r) 
                spt = int(tmp,2) 
                rl.append(spt)


                # Dest IP 
                dip = "" 
                tmp = "" 
                for i in range(60,92): 
                    f = float(row[i])
                    r = 1
                    if f < 0.5: 
                        r = 0 
                    tmp += str(r) 
                    if i==67 or i==75 or i==83 or i==91: 
                        val = int(tmp,2) 
                        if i < 90:
                            dip += str(val) + "."
                        else: 
                            dip += str(val)
                        tmp = ""
                rl.append(dip)


                # Dest Port 
                tmp = ""
                for i in range(92,108): 
                    f = float(row[i])
                    r = 1
                    if f < 0.5: 
                        r = 0 
                    tmp += str(r) 
                dpt = int(tmp,2) 
                rl.append(dpt)


                # packets 
                tmp = "" 
                for i in range(108,140): 
                    f = float(row[i])
                    r = 1
                    if f < 0.5: 
                        r = 0 
                    tmp += str(r) 
                pck = int(tmp,2) 
                rl.append(pck)


                # bytes 
                tmp = "" 
                for i in range(140,172): 
                    f = float(row[i])
                    r = 1
                    if f < 0.5: 
                        r = 0 
                    tmp += str(r) 
                byt = int(tmp,2) 
                rl.append(byt)
                    

                # Read the flags 
                synFlag     = ( float( row[172].strip() ) )
                ackFlag     = ( float( row[173].strip() ) )
                finFlag     = ( float( row[174].strip() ) )
                urgentFlag  = ( float( row[175].strip() ) )
                pushFlag    = ( float( row[176].strip() ) )
                resetFlag   = ( float( row[177].strip() ) )  

                flags = "" 
                if urgentFlag > 0.5:  
                    flags += "U" 
                else: 
                    flags += "." 
                
                if ackFlag > 0.5: 
                    flags += "A" 
                else: 
                    flags += "." 

                if pushFlag > 0.5:  
                    flags += "P" 
                else: 
                    flags += "." 
                
                if resetFlag > 0.5:  
                    flags += "R" 
                else: 
                    flags += "." 

                if synFlag > 0.5: 
                    flags += "S" 
                else: 
                    flags += "."
                
                if finFlag > 0.5:  
                    flags += "F" 
                else: 
                    flags += "."
                         
                rl.append(flags)

                # clazz 
                c_id = np.array(row[178:181],dtype=np.float32).argmax() 
                if c_id == 0: 
                    rl.append("normal")
                elif c_id == 1: 
                    rl.append("attacker")
                else: 
                    rl.append("victim")
                

                writer.writerow(rl)
                #print(rl)
                

            except Exception as inst: 
                print("expt", inst)
              