# Imports
import csv 
import sys
from datetime import datetime
import time
from random import randint
import math 
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
import numpy as np 
import math 
import tensorflow as tf


# Path to data
inputFile = sys.argv[1]
inputFileEmbedding = sys.argv[2]
outputFileData = sys.argv[3] 

ipToEmbed = dict() 
portToEmbed = dict() 
byteToEmbed = dict() 
packToEmbed = dict() 
durToEmbed = dict() 
default = ""
embSizeIP = -1

with open(inputFileEmbedding, 'r') as fl: 
    reader = csv.reader(fl, delimiter=',')
    firstLine = True
    num = 0 
    # Iterate through each line 
    for row in reader:
        # Handle header
        if firstLine == True : 
            firstLine = False
            continue
        # Read the values
        del row[0] # delete id
        key = row[-1]
        del row[-1] 
        embSizeIP = len(row)
        if key.count('.') > 2:
            ipToEmbed[key] = np.asarray(row).reshape(1,-1) 
        elif "_p" in key:
            key = key.split("_")[0]
            portToEmbed[key] = np.asarray(row).reshape(1,-1)  
        elif "_k" in key:
            key = key.split("_")[0]
            packToEmbed[key] = np.asarray(row).reshape(1,-1) 
        elif "_b" in key:
            key = key.split("_")[0]
            byteToEmbed[key] = np.asarray(row).reshape(1,-1) 
        elif "_d" in key:
            key = key.split("_")[0]
            durToEmbed[key] = np.asarray(row).reshape(1,-1)


emb_ips = [] 
lst_tmp = [] 
comp_id = -1 # temp 
for k,v in ipToEmbed.items(): 
    lst_tmp.append(v) 
    emb_ips.append(k) 
    if k == "192.168.220.255": 
        comp_id = len(emb_ips) - 1

embedding_ip = np.reshape( np.array(lst_tmp,dtype=np.float32) , (len(ipToEmbed),embSizeIP) ) 
ips_norm= np.ndarray(shape=(1,len(ipToEmbed)),dtype=np.float32)
for i in range(0,len(embedding_ip)): 
    line = embedding_ip[i]
    res = 0 
    for value in line: 
        res += (value*value) 
    res = math.sqrt(res) 
    ips_norm[0][i] = res


emb_pts = [] 
lst_pts = [] 
for k,v in portToEmbed.items(): 
    lst_pts.append(v) 
    emb_pts.append(k) 

embedding_pt = np.reshape( np.array(lst_pts,dtype=np.float32) , (len(portToEmbed),embSizeIP) ) 
pts_norm = np.ndarray(shape=(1,len(portToEmbed)),dtype=np.float32)
for i in range(0,len(embedding_pt)): 
    line = embedding_pt[i]
    res = 0 
    for value in line: 
        res += (value*value) 
    res = math.sqrt(res) 
    pts_norm[0][i] = res


emb_byt = [] 
lst_byt = [] 
for k,v in byteToEmbed.items(): 
    lst_byt.append(v) 
    emb_byt.append(k) 


embedding_by = np.reshape( np.array(lst_byt,dtype=np.float32) , (len(byteToEmbed),embSizeIP) ) 
byt_norm= np.ndarray(shape=(1,len(byteToEmbed)),dtype=np.float32)
for i in range(0,len(embedding_by)): 
    line = embedding_by[i]
    res = 0 
    for value in line: 
        res += (value*value) 
    res = math.sqrt(res) 
    byt_norm[0][i] = res


emb_pck = [] 
lst_pck = [] 
for k,v in packToEmbed.items(): 
    lst_pck.append(v) 
    emb_pck.append(k) 


embedding_pk = np.reshape( np.array(lst_pck,dtype=np.float32) , (len(packToEmbed),embSizeIP) ) 
pck_norm= np.ndarray(shape=(1,len(packToEmbed)),dtype=np.float32)
for i in range(0,len(embedding_pk)): 
    line = embedding_pk[i]
    res = 0 
    for value in line: 
        res += (value*value) 
    res = math.sqrt(res) 
    pck_norm[0][i] = res


emb_dur = [] 
lst_dur = [] 
for k,v in durToEmbed.items(): 
    lst_dur.append(v) 
    emb_dur.append(k) 


embedding_du = np.reshape( np.array(lst_dur,dtype=np.float32) , (len(durToEmbed),embSizeIP) ) 
dur_norm= np.ndarray(shape=(1,len(durToEmbed)),dtype=np.float32)
for i in range(0,len(embedding_du)): 
    line = embedding_du[i]
    res = 0 
    for value in line: 
        res += (value*value) 
    res = math.sqrt(res) 
    dur_norm[0][i] = res

# IP 
# Create placeholders
ip_row = tf.placeholder(tf.float32,shape=[1,embSizeIP]) 
ip_mat = tf.placeholder(tf.float32,shape=[len(embedding_ip),embSizeIP]) 
ip_nor = tf.placeholder(tf.float32,shape=[1,len(embedding_ip)]) 
# Execute multiplikation 
ip_sim = tf.matmul(ip_row,ip_mat,transpose_b=True) 
ip_res = tf.div(ip_sim,ip_nor)


# Ports
# Create placeholders 
pt_row = tf.placeholder(tf.float32,shape=[1,embSizeIP]) 
pt_mat = tf.placeholder(tf.float32,shape=[len(embedding_pt),embSizeIP]) 
pt_nor = tf.placeholder(tf.float32,shape=[1,len(embedding_pt)]) 
# Execute multiplikation 
pt_sim = tf.matmul(pt_row,pt_mat,transpose_b=True) 
pt_res = tf.div(pt_sim,pt_nor)


# Byte
# Create placeholders
by_row = tf.placeholder(tf.float32,shape=[1,embSizeIP]) 
by_mat = tf.placeholder(tf.float32,shape=[len(embedding_by),embSizeIP]) 
by_nor = tf.placeholder(tf.float32,shape=[1,len(embedding_by)]) 
# Execute multiplikation 
by_sim = tf.matmul(by_row,by_mat,transpose_b=True) 
by_res = tf.div(by_sim,by_nor)

# Packets
# Create placeholders
pk_row = tf.placeholder(tf.float32,shape=[1,embSizeIP]) 
pk_mat = tf.placeholder(tf.float32,shape=[len(embedding_pk),embSizeIP]) 
pk_nor = tf.placeholder(tf.float32,shape=[1,len(embedding_pk)]) 
# Execute multiplikation 
pk_sim = tf.matmul(pk_row,pk_mat,transpose_b=True) 
pk_res = tf.div(pk_sim,pk_nor)

# Duration
# Create placeholders
du_row = tf.placeholder(tf.float32,shape=[1,embSizeIP]) 
du_mat = tf.placeholder(tf.float32,shape=[len(embedding_du),embSizeIP]) 
du_nor = tf.placeholder(tf.float32,shape=[1,len(embedding_du)]) 
# Execute multiplikation 
du_sim = tf.matmul(du_row,du_mat,transpose_b=True) 
du_res = tf.div(du_sim,du_nor)

sess = tf.Session() 
init = tf.global_variables_initializer()

def findIP(vec):
    res = sess.run([ip_res], feed_dict = {ip_row: vec, ip_mat: embedding_ip, ip_nor: ips_norm})
    return emb_ips[ res[0].argmax() ] 

def findPt(vec):
    res = sess.run([pt_res], feed_dict = {pt_row: vec, pt_mat: embedding_pt, pt_nor: pts_norm})
    return emb_pts[ res[0].argmax() ] 

def findBy(vec):
    res = sess.run([by_res], feed_dict = {by_row: vec, by_mat: embedding_by, by_nor: byt_norm})
    return emb_byt[ res[0].argmax() ] 

def findPk(vec):
    res = sess.run([pk_res], feed_dict = {pk_row: vec, pk_mat: embedding_pk, pk_nor: pck_norm})
    return emb_pck[ res[0].argmax() ] 

def findDu(vec):
    res = sess.run([du_res], feed_dict = {du_row: vec, du_mat: embedding_du, du_nor: dur_norm})
    return emb_dur[ res[0].argmax() ] 

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

                # Read the weekday 
                d_id = np.array(row[0:7],dtype=np.float32).argmax() 
                rl.append(d_id)

                # Read the weekday 
                time = (float( row[7] )) * 86400
                if time < 0: 
                    time += 86400 
                if time > 86399: 
                    time = time % 86400
                h = int( time / 3600 ) 
                m = int( (time-(h*3600)) / 60 ) 
                s = round( (time-(h*3600)-(m*60)) ) 
                rl.append(str(h)+":"+str(m)+":"+str(s))

                # Duration
                du = row[8:8+embSizeIP]
                rl.append(findDu( np.array(du).reshape(1,embSizeIP)) ) 

                # Transport Protocol
                p_id = np.array(row[8+embSizeIP:8+embSizeIP+3],dtype=np.float32).argmax() 
                if p_id == 0: 
                    rl.append("ICMP")
                if p_id == 1: 
                    rl.append("UDP")
                if p_id == 2: 
                    rl.append("TCP")

                # Read the proto 
                sip = row[11+embSizeIP:11+2*embSizeIP]
                rl.append(findIP( np.array(sip).reshape(1,embSizeIP)) ) 

                sp = row[11+2*embSizeIP:11+3*embSizeIP]
                rl.append(findPt( np.array(sp).reshape(1,embSizeIP)) ) 

                dip = row[11+3*embSizeIP:11+4*embSizeIP]
                rl.append(findIP( np.array(dip).reshape(1,embSizeIP)) ) 
                
                dp = row[11+4*embSizeIP:11+5*embSizeIP]
                dst_p = findPt( np.array(dp).reshape(1,embSizeIP))
                rl.append( dst_p ) 
                
                 # Packete
                pk = row[11+5*embSizeIP:11+6*embSizeIP]
                rl.append(findPk( np.array(pk).reshape(1,embSizeIP)) ) 

                # Bytes 
                by = row[11+6*embSizeIP:11+7*embSizeIP]
                rl.append(findBy( np.array(by).reshape(1,embSizeIP)) ) 
                    
                # Read the flags 
                synFlag     = ( float( row[11+7*embSizeIP+0].strip() ) )
                ackFlag     = ( float( row[11+7*embSizeIP+1].strip() ) )
                finFlag     = ( float( row[11+7*embSizeIP+2].strip() ) )
                urgentFlag  = ( float( row[11+7*embSizeIP+3].strip() ) )
                pushFlag    = ( float( row[11+7*embSizeIP+4].strip() ) )
                resetFlag   = ( float( row[11+7*embSizeIP+5].strip() ) )  

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
                normal = 0.0
                attacker = 0.0 
                victim = 0.0
                c_id = np.array(row[11+7*embSizeIP+6:11+7*embSizeIP+6+3],dtype=np.float32).argmax() 

                if c_id == 0: 
                    rl.append("normal")
                if c_id == 1: 
                    rl.append("attacker")
                if c_id == 2: 
                    rl.append("victim")          

                writer.writerow(rl)

            except Exception as inst: 
                print("expt", inst)
              