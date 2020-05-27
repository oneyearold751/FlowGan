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


# Open the file with the unlabelled flows 
mins = [99999.9,99999.9,99999.9] 
maxs = [-1.0,-1.0,-1.0] 
counter = 0 
print("Read file for normaliziation")
with open(inputFile, 'r') as fl: 
    reader = csv.reader(fl, delimiter=',')
    firstLine = True
    # Iterate through each line 
    for row in reader:
        # Handle header
        if firstLine == True : 
            firstLine = False
            continue

        if counter % 100000 == 0: 
            print(str(counter)," flows gelesen.")
        counter += 1

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
counter = 0
print("Write flows to disk")
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
                firstLine = False
                continue

            if counter % 100000 == 0: 
                print(str(counter)," flows geschrieben.")
            counter += 1
            # Read the values
            try: 
                day   = row[0].strip() 
                time  = row[1].strip() 
                dur   = row[2].strip() 
                proto = row[3].strip()
                srcIP = row[4].strip()
                srcPt = row[5].strip() 
                dstIP = row[6].strip()
                dstPt = row[7].strip()
                packets=row[8].strip() 
                bytzes= row[9].strip() 
                flags = row[10].strip() 
                clazz = row[11].strip() 
                
                if "M" in bytzes: 
                    bytzes = bytzes.split(" ")[0]
                    bytzes = float(bytzes) * 1024 * 1024
                else: 
                    bytzes = float(bytzes)

                if float(duration) > 5000: 
                    continue 

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
                dur = float(duration)
                tmp_dur = float( (dur-mins[0])/(maxs[0]-mins[0])) 
                rl.append(tmp_dur) 

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

                rl.append(float(icmp))
                rl.append(float(udp))
                rl.append(float(tcp))

                # IP Addresses and Ports 
                sIP = srcIP.split(".") 
                for part in sIP: 
                    p = format(int(part),'08b')
                    for c in p: 
                        rl.append(float(c))

                sp = int(float(srcPt))  
                sp_t = format(int(sp),'016b')
                for c in sp_t: 
                    rl.append(float(c))
                
                dIP = dstIP.split(".") 
                for part in dIP: 
                    p = format(int(part),'08b')
                    for c in p: 
                        rl.append(float(c))

                dp = int(float(dstPt))  
                dp_t = format(int(dp),'016b')
                for c in dp_t: 
                    rl.append(float(c))


                # Packets 
                packets = int(float(packets))  
                pk_t = format(int(packets),'032b')
                for c in pk_t: 
                    rl.append(float(c))

                # Bytes 
                bytezz = int(float(bytzes))  
                by_t = format(int(bytezz),'032b')
                for c in by_t: 
                    rl.append(float(c))
               
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
            
