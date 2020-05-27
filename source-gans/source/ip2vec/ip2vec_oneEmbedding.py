# IMPORTS 
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import math
import os
import random
import zipfile
import sys
import time 

import pandas as pd 
import numpy as np
from six.moves import urllib
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf
from tensorflow.contrib.tensorboard.plugins import projector
os.environ["CUDA_VISIBLE_DEVICES"]="1"


###### USER PARAMETERS ########
# input data file 
input_filename = sys.argv[1] 
split_sign = ","
# path to store embeddings and models  
save_embeddings = "/home/markus/code/paper/code_gans/ip2vec/"
###### END USER PARMETERS #####


###### Parameters for the Embedding #### 
batch_size = 128     # Consider for each learning step X flows  
embedding_size = 20 # Size of the embedding 
num_sampled = 32 
num_epochs = 10    # Number of training epochs 
valid_size = 16     # Random set of words to evaluate similarity on.
valid_window = 200  # Only pick dev samples in the head of the distribution.
valid_examples = np.random.choice(valid_window, valid_size, replace=False)
###### END PARAMETERS FOR THE EMBEDDING ##### 


####### FUNCTIONS ###############

# Reads the file with the preprocessed flow-based data and returns a list with all "words"
# The file must have the following structure: 
#   srcip, context_attribute1, context_attribute_2, ... 
def read_file_and_convert_to_list(input_filename):
  # Stores the number of attributes (target and context) for each flow  
  global num_elems
  # Read the file line by line 
  with open(input_filename, 'r') as f:
    data = tf.compat.as_str(f.read()).splitlines()
    num_elems = len(data[0].split(","))
  # Convert to list 
  res = [] 
  first = True
  for line in data: 
      if first == True: 
          first = False 
          continue 
      for word in line.split(","): 
          res.append(word.strip())   
  return res, len(data)


# This functions builds the data set (all values are converted to ids) 
def build_dataset(words):    
     # Count the frequency of all values 
    count = []
    count.extend(collections.Counter(words).most_common())
    size = len(count)

    # Build the dictionary 
    # e.g. ("129.3.3.3" , 2)
    dictionary = dict() 
    for word, _ in count: 
        dictionary[word] = len(dictionary)
    # Build the reverse dictionary 
    reverse_dictionary = dict(zip(dictionary.values(),dictionary.keys())) 
    
    # Transfer the list of words to a list of IDs
    data = list() 
    for word in words: 
        if word in dictionary: 
            index = dictionary[word]
        data.append(index) 

    return data, count, dictionary, reverse_dictionary, size


c_iter = 0 
# Generates the next batch 
def generate_batch(): 
    # use the global data_index variable (recent pointer)
    global data_index  
    global num_elems  
    global c_iter 
    # create variables for the training sets 
    batch = np.ndarray(shape=(training_pairs),dtype=np.int32) 
    labels= np.ndarray(shape=(training_pairs,1), dtype=np.int32)

    # set data index 
    data_index = idx[c_iter] * num_elems

    # Read batch_size flows and create training sets 
    for i in range(batch_size): 
        # input SrcIP 
        batch[i*pairs+0]    = data[data_index]
        labels[i*pairs+0,0] = data[data_index+1] 

        batch[i*pairs+1]    = data[data_index]
        labels[i*pairs+1,0] = data[data_index+2] 

        batch[i*pairs+2]    = data[data_index]
        labels[i*pairs+2,0] = data[data_index+4] 

        # input DstIP 
        batch[i*pairs+3]    = data[data_index+2]
        labels[i*pairs+3,0] = data[data_index] 

        batch[i*pairs+4]    = data[data_index+2]
        labels[i*pairs+4,0] = data[data_index+4] 

        batch[i*pairs+5]    = data[data_index+2]
        labels[i*pairs+5,0] = data[data_index+3] 

        # input srcPt 
        batch[i*pairs+6]    = data[data_index+1]
        labels[i*pairs+6,0] = data[data_index+0] 

        # input dstPt
        batch[i*pairs+7]    = data[data_index+3]
        labels[i*pairs+7,0] = data[data_index+2] 

        # input dur
        batch[i*pairs+8]    = data[data_index+7]
        labels[i*pairs+8,0] = data[data_index+5] 

        # input byt
        batch[i*pairs+9]    = data[data_index+6]
        labels[i*pairs+9,0] = data[data_index+5] 

        batch[i*pairs+10]    = data[data_index+6]
        labels[i*pairs+10,0] = data[data_index+7] 

        # input packets
        batch[i*pairs+11]    = data[data_index+5]
        labels[i*pairs+11,0] = data[data_index+6] 

        batch[i*pairs+12]    = data[data_index+5]
        labels[i*pairs+12,0] = data[data_index+7] 

        # Check if end of training list is reached 
        #data_index = (data_index + num_elems) % len_value
        c_iter += 1 
        if c_iter == num_lines - 1: 
            c_iter = 0 
            random.shuffle(idx)
        data_index = idx[c_iter] * num_elems
    
    return batch, labels 

######## END FUNCTIONS #######

#### Global variales
# Recent pointer for data
data_index = 0 
# Number of attributes per line 
num_elems = -1        
#### End Global variales

#### STEP 1: Read the file  
print("Step 1: Read the file")
input_values, num_lines = read_file_and_convert_to_list(input_filename)
len_value = len(input_values)
idx = [] 
for i in range(0,num_lines-1): 
    idx.append(i)
# define the number of of extractable pairs per flow  
pairs = 13 #num_elems - 1 + 2
# The number of training pers created per flow 
training_pairs = pairs * batch_size  


#### Step 2: Build the data set 
print("Step 2: Build the data set")
data, count, dictionary, reverse_dictionary, vocabluary_size = build_dataset(input_values)
print("Voc: --- ", len(dictionary))
print("VOC: ", vocabluary_size)
generate_batch()


#### Step 3: Build the model  
print("Step 3: Build the model")

graph = tf.Graph() 

with graph.as_default(): 
    # Input data 
    train_inputs = tf.placeholder(tf.int32,shape=[training_pairs])
    train_labels = tf.placeholder(tf.int32,shape=[training_pairs,1])
    valid_dataset= tf.constant(valid_examples, dtype=tf.int32) 

    with tf.device('/cpu:0'): 
        # Look up embedding for inputs 
        embeddings = tf.Variable(tf.random_uniform([vocabluary_size,embedding_size],-1.0,1.0)) 
        embed = tf.nn.embedding_lookup(embeddings,train_inputs)

        # Construct the variables for NCE loss 
        nce_weights = tf.Variable(
            tf.truncated_normal([vocabluary_size,embedding_size],stddev=1.0 / math.sqrt(embedding_size)) )
        nce_biases = tf.Variable(tf.zeros([vocabluary_size]))

        # Compute the average NCE loss for the batch.
        # tf.nce_loss automatically draws a new sample of the negative labels each
        # time we evaluate the loss.
        loss = tf.reduce_mean(
            tf.nn.nce_loss(weights=nce_weights,
                     biases=nce_biases,
                     labels=train_labels,
                     inputs=embed,
                     num_sampled=num_sampled,
                     num_classes=vocabluary_size))

        # Construct the SGD optimizer using a learning rate of 1.0 
        optimizer = tf.train.GradientDescentOptimizer(0.05).minimize(loss) 

        # compute 
        norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
        normalized_embeddings = embeddings / norm

        # init 
        init = tf.global_variables_initializer() 


# Step 4: Train the model  
print("Step 4: Train the model")

# calculate the number of training steps 
num_steps = int(num_lines / batch_size * num_epochs)

with tf.Session(graph=graph) as session: 
    # Init 
    init.run() 
    print("Step 4.1: Initialized") 

    average_loss = 0
    for step in xrange(num_steps): 
        batch_inputs, batch_labels = generate_batch()
        feed_dict = {train_inputs: batch_inputs, train_labels: batch_labels}

        # We perform one update step by evaluating the optimizer op (including it
        # in the list of returned values for session.run()
        _, loss_val = session.run([optimizer, loss], feed_dict=feed_dict)
        average_loss += loss_val

        if step % 2000 == 0: 
            if step > 0:
                average_loss /= 2000
            print("Average loss at step", step, ": ", average_loss, " from ", num_steps ," steps.")
            average_loss = 0 
			

    # Save the embedding 
    to_save_n = session.run(embeddings) 
    to_save = (to_save_n - to_save_n.min(0)) / to_save_n.ptp(0) 
    to_save_norm = to_save / to_save.max(axis=0) 
    target = save_embeddings + "embedding-one-20.csv"
    dataframe = pd.DataFrame(data=to_save_norm[0:,0:])
    vals = [] 
    for u in range(0,len(to_save)): 
        vals.append(reverse_dictionary.get(u)) 
    dataframe['values'] = vals
    dataframe.to_csv(target,sep=",")
