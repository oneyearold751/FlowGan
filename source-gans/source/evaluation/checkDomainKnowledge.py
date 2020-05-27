# Imports
import csv 
import sys
import random
from datetime import datetime
import time
from random import randint
        
# Path to data
inputFile = sys.argv[1]

# Check ids from the files
id_day   = 0
id_time  = 1
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
    

# Test functions 
# Test 1: UDP sollte keine Flags haben
succeeded_flags_and_udp = 0 
failed_flags_and_udp = 0
def checkFlagsAndUDP(flags,proto): 
    global succeeded_flags_and_udp 
    global failed_flags_and_udp
    if proto == "UDP": 
        if len(flags) == 0: 
            succeeded_flags_and_udp += 1 
        else: 
            failed_flags_and_udp += 1


# Test 2: Eine IP sollte intern sein 
succeeded_one_ip_intern = 0 
failed_one_ip_intern = 0
def checkOneIPIntern(srcIP,dstIP): 
    global succeeded_one_ip_intern 
    global failed_one_ip_intern
    if srcIP[:7] == "192.168" or dstIP[:7] == "192.168" or srcIP == "0.0.0.0" or dstIP == "255.255.255.255": 
        succeeded_one_ip_intern += 1 
    else:
        failed_one_ip_intern += 1


# Test 3: Duration of One Packet flow
succeeded_dur_one_packet = 0 
failed_dur_one_packet = 0
def checkDurationOnePacket(duration,packets): 
    global succeeded_dur_one_packet 
    global failed_dur_one_packet
    if packets == "1": 
        d = float(duration) 
        if d < 1: # duration == "0.000" or duration == "0" or d == 0: 
            succeeded_dur_one_packet += 1
        else:
            failed_dur_one_packet += 1


# Test 4: Port 80 and 443 only TCP
succeeded_tcp_80 = 0 
failed_tcp_80 = 0
def checkPort80TCP(proto,srcPt,dstPt,clazz): 
    global succeeded_tcp_80 
    global failed_tcp_80
    if srcPt == "80" or srcPt == "443" or dstPt == "80" or dstPt == "443": 
        if proto == "TCP": 
            succeeded_tcp_80 += 1
        elif clazz == "normal":
            failed_tcp_80 += 1


# Test 5: Port 53 only UDP
succeeded_udp_53 = 0 
failed_udp_53 = 0
def checkPort53UDP(proto,srcPt,dstPt,clazz): 
    global succeeded_udp_53 
    global failed_udp_53
    if srcPt == "53" or dstPt == "53": 
        if proto == "UDP": 
            succeeded_udp_53 += 1
        elif clazz == "normal": 
            failed_udp_53 += 1


# Test 6: Multi- und Broadcast Adressen only target
succeeded_multicast = 0 
failed_multicast = 0
def checkMultiBroadcast(srcIP,dstIP,row): 
    global succeeded_multicast 
    global failed_multicast
    ip1_1 = int( srcIP.split(".")[0] ) 
    ip1_4 = int( srcIP.split(".")[3] )

    ip2_1 = int( dstIP.split(".")[0] ) 
    ip2_4 = int( dstIP.split(".")[3] )

    if (ip2_1 > 223 or (ip2_1 == 192 and ip2_4 == 255)) and ip1_1 < 224 and not(ip1_4 == 192 and ip1_4 == 255):  
        succeeded_multicast += 1 
    elif ip1_1 > 223 or (ip1_4 == 192 and ip1_4 == 255):  
        failed_multicast += 1


# Test 7: Netbios only to internal broadcasts and from internal hosts
succeeded_netbios = 0 
failed_netbios = 0
def checkNetbios(srcIP,dstIP,dstPt,proto): 
    global succeeded_netbios 
    global failed_netbios
    ip1_1 = int( srcIP.split(".")[0] ) 
    ip1_2 = int( srcIP.split(".")[1] )

    ip2_1 = int( dstIP.split(".")[0] ) 
    ip2_4 = int( dstIP.split(".")[3] )

    if dstPt == "137" or dstPt == "138": 
        if ip1_1 == 192 and ip1_2 == 168 and proto == "UDP" and ip2_1 == 192 and ip2_4 == 255:  
            succeeded_netbios += 1 
        else:  
            failed_netbios += 1


# Test 8: Check Bytes 
succeeded_byte_packet = 0 
failed_byte_packet = 0
def checkRelationBytePackets(bytzes,packets,row): 
    global succeeded_byte_packet 
    global failed_byte_packet

    if bytzes >= packets * 42 and bytzes <= packets * 65536:  
        succeeded_byte_packet += 1 
    else:  
        failed_byte_packet += 1


# Test 9: Check client port 
succeeded_client_port = 0 
failed_client_port = 0
def checkClientPorts(srcIP,srcPt,dstIP,dstPt,proto): 
    global succeeded_client_port 
    global failed_client_port

    if proto != "TCP": 
        return 

    if ("192.168.200." in srcIP and "192.168.200.3" != srcIP) or ("192.168.210." in srcIP and "192.168.210.3" != srcIP) or ("192.168.220." in srcIP and "192.168.220.3" != srcIP): 
        sp = float(srcPt)
        if sp > 10000 :
            succeeded_client_port += 1 
        else:  
            failed_client_port += 1
            

    if ("192.168.200." in dstIP and "192.168.200.3" != dstIP) or ("192.168.210." in dstIP and "192.168.210.3" != dstIP) or ("192.168.220." in dstIP and "192.168.220.3" != dstIP): 
        sp = float(dstPt)
        if sp > 10000: 
            succeeded_client_port += 1 
        else:  
            failed_client_port += 1
            


# Test 10: Check server port 
succeeded_server_port = 0 
failed_server_port = 0
def checkServerPorts(srcIP,srcPt,dstIP,dstPt): 
    global succeeded_server_port 
    global failed_server_port

    if ("192.168.200.3" == srcIP) or ("192.168.210.3" == srcIP) or ("192.168.220.3" == srcIP) or \
    ( ("192.168.200." in srcIP) == False and ("192.168.210." in srcIP) == False and ("192.168.220." in srcIP) == False): 
        sp = float(srcPt)
        if sp < 10000:
            succeeded_server_port += 1 
        else:  
            failed_server_port += 1

    if ("192.168.200.3" == dstIP) or ("192.168.210.3" == dstIP) or ("192.168.220.3" == dstIP) or \
    ( ("192.168.200." in dstIP) == False and ("192.168.210." in dstIP) == False and ("192.168.220." in dstIP) == False): 
        sp = float(dstPt)
        if sp < 10000: 
            succeeded_server_port += 1 
        else:  
            failed_server_port += 1


# Test 11: Check intern extern 
succeeded_rel_internextern = 0 
failed_rel_internextern = 0
def checkRelationInternExtern(srcIP,dstIP): 
    global succeeded_rel_internextern 
    global failed_rel_internextern

    if "192.168." in srcIP and "192.168." in dstIP:  
        succeeded_rel_internextern += 1 
    else:  
        failed_rel_internextern += 1


counter = 0 
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
        # Read the values
        counter += 1 
        if counter % 100000 == 0: 
            print("Processing flows: ", str(counter))
        try: 
            day   = row[id_day].strip() 
            time  = row[id_time].strip() 
            srcIP = row[id_srcIP].strip()
            srcPt = row[id_srcPt].strip() 
            dstIP = row[id_dstIP].strip()
            dstPt = row[id_dstPt].strip()
            proto = row[id_proto].strip()
            flags = row[id_flags].strip() 
            bytzes= row[id_bytzes].strip() 
            packets=row[id_packets].strip()
            dur   = row[id_dur].strip() 
            clazz = row[id_clazz].strip() 
            
            # Do tests 
            # Test 1: UDP sollte keine Flags haben 
            if flags == "......": 
                flags = "" 
            checkFlagsAndUDP(flags,proto) 

            # Test 2: Eine IP sollte intern sein 
            checkOneIPIntern(srcIP,dstIP)

            # Test 3: Duration of One Packet flow
            checkDurationOnePacket(dur,packets)

            # Test 4: Port 80 and 443 only TCP 
            checkPort80TCP(proto,srcPt,dstPt,clazz)

            # Test 5: Port 53 only UDP
            checkPort53UDP(proto,srcPt,dstPt,clazz)

            # Test 6: Multi- and Broadcast Adresssen nur als target 
            checkMultiBroadcast(srcIP,dstIP,row)

            # Test 7: Netbios only to internal broadcasts and from internal hosts
            checkNetbios(srcIP,dstIP,dstPt,proto)

            if "M" in bytzes: 
                bytzes = float(bytzes.split(" ")[0]) * 1024 * 1024 
            else: 
                bytzes = float(bytzes)
            packets = float(packets)

            # Test 8: Check Byte/Packets Relation
            checkRelationBytePackets(bytzes,packets,row)

            # Test 9: Client Ports 
            checkClientPorts(srcIP,srcPt,dstIP,dstPt,proto)

            # Test 10: Server Ports  
            checkServerPorts(srcIP,srcPt,dstIP,dstPt)

            # Test 11: Rel int/ext 
            checkRelationInternExtern(srcIP,dstIP) 

        except Exception as inst: 
            print("AUSNAHME: ", inst)
            print(row)
        

# Print Results to conosle 
print("Test 1: UDP sollte keine Flags haben") 
test1_per = float(succeeded_flags_and_udp) 
if (succeeded_flags_and_udp+failed_flags_and_udp)  > 0:   
    test1_per /= (succeeded_flags_and_udp+failed_flags_and_udp) 
test1_per *= 100
test1_per = str(test1_per)
print("Erg: ", str(succeeded_flags_and_udp), " von ", str(succeeded_flags_and_udp+failed_flags_and_udp), " korrekt. (", test1_per, "%)")

print("Test 2: Mindestens eine IP sollte intern sein") 
test2_per = float(succeeded_one_ip_intern) 
if (succeeded_one_ip_intern+failed_one_ip_intern)  > 0: 
    test2_per /= (succeeded_one_ip_intern+failed_one_ip_intern) 
test2_per *= 100
test2_per = str(test2_per)
print("Erg: ", str(succeeded_one_ip_intern), " von ", str(succeeded_one_ip_intern+failed_one_ip_intern), " korrekt. (", test2_per, "%)")

##print("Test3: Duration of One Packet flow") 
#test3_per = float(succeeded_dur_one_packet) 
#if (succeeded_dur_one_packet+failed_dur_one_packet) > 0: 
#    test3_per /= (succeeded_dur_one_packet+failed_dur_one_packet) 
#test3_per *= 100
#test3_per = str(test3_per)
#print("Erg: ", str(succeeded_dur_one_packet), " von ", str(succeeded_dur_one_packet+failed_dur_one_packet), " korrekt. (", test3_per, "%)")

print("Test 4: Port 80 and 443 only TCP ") 
test4_per = float(succeeded_tcp_80) 
if (succeeded_tcp_80+failed_tcp_80) > 0:    
    test4_per /= (succeeded_tcp_80+failed_tcp_80) 
test4_per *= 100
test4_per = str(test4_per)
print("Erg: ", str(succeeded_tcp_80), " von ", str(succeeded_tcp_80+failed_tcp_80), " korrekt. (", test4_per, "%)")

print("Test 5: Port 53 only UDP ") 
test5_per = float(succeeded_udp_53) 
if (succeeded_udp_53+failed_udp_53) > 0: 
    test5_per /= (succeeded_udp_53+failed_udp_53) 
test5_per *= 100
test5_per = str(test5_per)
print("Erg: ", str(succeeded_udp_53), " von ", str(succeeded_udp_53+failed_udp_53), " korrekt. (", test5_per, "%)")

print("Test 6: Multi- and Broadcast Adresssen nur als target") 
test6_per = float(succeeded_multicast) 
if succeeded_multicast+failed_multicast > 0:    
    test6_per /= (succeeded_multicast+failed_multicast) 
test6_per *= 100
test6_per = str(test6_per)
print("Erg: ", str(succeeded_multicast), " von ", str(succeeded_multicast+failed_multicast), " korrekt. (", test6_per, "%)")


print("Test 7: Netbios only to internal broadcasts and from internal hosts") 
test7_per = float(succeeded_netbios) 
if succeeded_netbios+failed_netbios > 0:    
    test7_per /= (succeeded_netbios+failed_netbios) 
test7_per *= 100
test7_per = str(test7_per)
print("Erg: ", str(succeeded_netbios), " von ", str(succeeded_netbios+failed_netbios), " korrekt. (", test7_per, "%)")


print("Test 8: Check Byte Packet Relation") 
test8_per = float(succeeded_byte_packet) 
if succeeded_byte_packet+failed_byte_packet > 0:    
    test8_per /= (succeeded_byte_packet+failed_byte_packet) 
test8_per *= 100
test8_per = str(test8_per)
print("Erg: ", str(succeeded_byte_packet), " von ", str(succeeded_byte_packet+failed_byte_packet), " korrekt. (", test8_per, "%)")


print("Test 9: Check Client Ports") 
test9_per = float(succeeded_client_port) 
if succeeded_client_port+failed_client_port > 0:    
    test9_per /= (succeeded_client_port+failed_client_port) 
test9_per *= 100
test9_per = str(test9_per)
print("Erg: ", str(succeeded_client_port), " von ", str(succeeded_client_port+failed_client_port), " korrekt. (", test9_per, "%)")


print("Test 10: Check Server Ports") 
test10_per = float(succeeded_server_port) 
if succeeded_server_port+failed_server_port > 0:    
    test10_per /= (succeeded_server_port+failed_server_port) 
test10_per *= 100
test10_per = str(test10_per)
print("Erg: ", str(succeeded_server_port), " von ", str(succeeded_server_port+failed_server_port), " korrekt. (", test10_per, "%)")


print("Test 11: Relation internal to all traffic") 
test11_per = float(succeeded_rel_internextern) 
if succeeded_rel_internextern+failed_rel_internextern > 0:    
    test11_per /= (succeeded_rel_internextern+failed_rel_internextern) 
test11_per *= 100
test11_per = str(test11_per)
print("Erg: ", str(succeeded_rel_internextern), " von ", str(succeeded_rel_internextern+failed_rel_internextern), " korrekt. (", test11_per, "%)")


print("Summary:") 
print(test1_per)
print(test2_per)  
#print(test3_per) 
print(test4_per) 
print(test5_per) 
print(test6_per) 
print(test7_per) 
print(test8_per) 
print(test9_per) 
print(test10_per) 
print(test11_per)

