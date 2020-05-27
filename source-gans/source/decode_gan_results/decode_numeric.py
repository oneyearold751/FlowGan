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

os.environ["CUDA_VISIBLE_DEVICES"]="3"

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
        bytzes = row[9].strip() 
        if "M" in bytzes: 
            bytzes = bytzes.split(" ")[0]
            bytzes = float(bytzes) * 1024 * 1024
        else: 
            bytzes = float( bytzes )
        bytzes = float( bytzes )  
        packets = float( row[8].strip() )

        if duration > 10000: 
            continue

        if duration > maxs[0]: 
            maxs[0] = duration
        if duration < mins[0]: 
            mins[0] = duration 

        if bytzes > maxs[1]: 
            maxs[1] = bytzes
        if bytzes < mins[1]:   
            mins[1] = bytzes 

        if packets > maxs[2]: 
            maxs[2] = packets
        if packets < mins[2]: 
            mins[2] = packets 

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
            

                # IPs and Pts 
                sip0 = round( float(row[12].strip()) * 255.0 ) 
                sip1 = round( float(row[13].strip()) * 255.0 )
                sip2 = round( float(row[14].strip()) * 255.0 ) 
                sip3 = round( float(row[15].strip()) * 255.0 )
                sip = str(sip0) + "." + str(sip1) + "." + str(sip2) + "." + str(sip3)
                rl.append(sip)
                
                sp = round( float(row[16].strip()) * 65535.0 ) 
                rl.append(sp)

                dip0 = round( float(row[17].strip()) * 255.0 ) 
                dip1 = round( float(row[18].strip()) * 255.0 )
                dip2 = round( float(row[19].strip()) * 255.0 ) 
                dip3 = round( float(row[20].strip()) * 255.0 )
                dip = str(dip0) + "." + str(dip1) + "." + str(dip2) + "." + str(dip3)
                rl.append(dip)
                
                dp = round( float(row[21].strip()) * 65535.0 ) 
                rl.append(dp)

                # packets 
                pk = float( row[22] ) 
                pk = round( pk * (maxs[2]-mins[2]) + mins[2] )
                rl.append(pk)

                # bytes 
                by = float( row[23] ) 
                by = round( by * (maxs[1]-mins[1]) + mins[1] )
                rl.append(by)
                    
                # Read the flags 
                synFlag     = ( float( row[24].strip() ) )
                ackFlag     = ( float( row[25].strip() ) )
                finFlag     = ( float( row[26].strip() ) )
                urgentFlag  = ( float( row[27].strip() ) )
                pushFlag    = ( float( row[28].strip() ) )
                resetFlag   = ( float( row[29].strip() ) )  

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
                c_id = np.array(row[30:33],dtype=np.float32).argmax() 
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
                print(row)
              