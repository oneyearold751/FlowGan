# Imports
import csv 
import sys
import random
from datetime import datetime
import time
from random import randint
        

# Path to data
inputFile = sys.argv[1]
inputFileEmbedding = sys.argv[2]
outputFileData = sys.argv[3] 

ipToEmbed = dict() 
default = ""

with open(inputFileEmbedding, 'r') as fl: 
    reader = csv.reader(fl, delimiter=',')
    firstLine = True
    # Iterate through each line 
    for row in reader:
        # Handle header
        if firstLine == True : 
            firstLine = False
            continue
        # Read the values
        del row[0] # delete id
        key = row[-1].strip()
        del row[-1]
        ipToEmbed[key] = row 

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
                continue
            # Read the values
            try: 
                day   = row[0].strip() 
                time  = row[1].strip() 
                dur   = row[2].strip() + "_d"
                proto = row[3].strip()
                srcIP = row[4].strip()
                srcPt = row[5].strip() + "_p" 
                dstIP = row[6].strip()
                dstPt = row[7].strip() + "_p"
                packets=row[8].strip() + "_k"
                bytzes= row[9].strip() + "_b"
                flags = row[10].strip() 
                clazz = row[11].strip()
                type  = row[12].strip() 
                 
                rl = []

                # Add day 
                for i in range(0,7): 
                    rl.append(0.0) 
                rl[int(day)] = 1 

                # add time 
                # Handle timestamp 
                datetime_object = datetime.strptime(time, "%H:%M:%S.%f")
                seconds = float(datetime_object.hour * 3600.0 + datetime_object.minute * 60.0 + datetime_object.second) / 86400.0
                rl.append( seconds )

                # duration 
                du = ipToEmbed[dur]
                for a in du: 
                    rl.append(float(a))

                # transport protocol 
                icmp = 0.0
                udp = 0.0
                tcp = 0.0

                if proto == "ICMP": 
                    icmp = icmp + 1 
                if proto == "TCP": 
                    tcp = tcp + 1 
                if proto == "UDP": 
                    udp = udp + 1 
                if proto == "IGMP": 
                   continue
                   
                rl.append(icmp)
                rl.append(udp)
                rl.append(tcp) 

                # Replace IPs and Ports with their embedding 
                sIP = ipToEmbed[srcIP]
                for a in sIP: 
                    rl.append(float(a))

                sp = ipToEmbed[srcPt]
                for a in sp: 
                    rl.append(float(a))

                dIP = ipToEmbed[dstIP]
                for a in dIP: 
                    rl.append(float(a))

                dp = ipToEmbed[dstPt]
                for a in dp: 
                    rl.append(float(a))

                # Pakete 
                pk = ipToEmbed[packets]
                for a in pk: 
                    rl.append(float(a))

                # Bytes 
                by = ipToEmbed[bytzes]
                for a in by: 
                    rl.append(float(a))

                # binarize flags 
                syn = 0.0
                ack = 0.0
                fin = 0.0
                urg = 0.0
                psh = 0.0
                res = 0.0
                
                if "S" in flags: 
                    syn = syn + 1
                if "A" in flags: 
                    ack = ack + 1
                if "F" in flags: 
                    fin = fin + 1 
                if "U" in flags: 
                    urg = urg + 1 
                if "P" in flags: 
                    psh = psh + 1 
                if "R" in flags: 
                    res = res + 1             
                rl.extend([syn,ack,fin,urg,psh,res])

                # clazz 
                normal = 0.0
                attacker = 0.0 
                victim = 0.0

                ps = 0.0 
                bf = 0.0
                do = 0.0 

          

                if clazz == "normal": 
                    normal = normal + 1 
                if clazz == "attacker": 
                    attacker = attacker + 1 
                if clazz == "victim": 
                    victim = victim + 1
                rl.extend([normal,attacker,victim])
              
                # Write row 
                writer.writerow(rl)
                
            except Exception as inst: 
                print("AUSNAHME: ", inst)
                print(row)
            
