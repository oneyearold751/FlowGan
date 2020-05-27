import os, sys
sys.path.append(os.getcwd())

import time
import functools
import csv 
from pathlib import Path
import random 

import numpy as np
import tensorflow as tf

import tflib as lib
import tflib.ops.linear
import tflib.ops.conv2d
import tflib.ops.batchnorm
import tflib.ops.deconv2d
import tflib.save_images
import tflib.data_loader
import tflib.ops.layernorm
import tflib.plot

os.environ["CUDA_VISIBLE_DEVICES"]="2"

# Dataset
###DATA_DIR = 'data/lsun'
#DATASET = "lsun" # celeba, cifar10, svhn, lsun
#if len(DATA_DIR) == 0:
#    raise Exception('Please specify path to data directory in gan_64x64.py!')

input_file = sys.argv[1]
in_output_file_records = sys.argv[2]
in_noise = int( sys.argv[3] ) 
in_epochs = int( sys.argv[4] ) 
in_hidden_size = int( sys.argv[5] ) 
in_batch_size = int( sys.argv[6] )



# Configuration Parameter 
MODE = 'wgan-gp' # wgan, wgan-gp
input_length_data = -1 # TODO 
input_length_noise = in_noise #TODO 
num_epochs = in_epochs
add_noise_to_real_data = False 
conf_name = in_output_file_records
# Log subdirectories are automatically created from
# the above settings and the current timestamp.
BATCH_SIZE = in_batch_size # Batch size. Must be a multiple of N_GPUS
fully_connected_dim = in_hidden_size
LAMBDA = 10 # Gradient penalty lambda hyperparameter
LOG_DIR = "./samples"
SAMPLES_DIR = os.path.join(LOG_DIR, "samples")

# GPU Devices 
DEVICES = ['/gpu:2']
N_GPUS = 1 # Number of GPUs

# Sample generation 
OUTPUT_STEP = 200 # Print output every OUTPUT_STEP
SAVE_SAMPLES_STEP = 200 # Generate and save samples every SAVE_SAMPLES_STEP

# Create directories if necessary
if not os.path.exists(SAMPLES_DIR):
  print("*** create sample dir %s" % SAMPLES_DIR)
  os.makedirs(SAMPLES_DIR)


# Settings for TTUR and orig
TTUR = True
if TTUR:
  CRITIC_ITERS = 1 # How many iterations to train the critic for
  D_LR = 0.0003
  G_LR = 0.0001
  BETA1_D = 0.0
  BETA1_G = 0.0
  ITERS = 100000 # How many iterations to train for
else:
  CRITIC_ITERS = 5 # How many iterations to train the critic for
  D_LR = 0.0005
  G_LR = 0.0005
  BETA1_D = 0.0
  BETA1_G = 0.0
  ITERS = 25009 # How many iterations to train for



############## DATA LOADER ######################
###### Read the data ##########
counter_read = 0 
class NetflowDataFlow():
    def __init__(self, data_file, transform=None):
        
        data_file_path = Path(data_file)
        if not data_file_path.exists():
            raise Exception("data_file does not exist.")  

        def prepare_data(dp):
            global input_length_data
            global counter_read

            if input_length_data == -1: 
                input_length_data = len(dp)
            else: 
                l = len(dp)
                if l != input_length_data:
                    print("Ignore line") 
                    return 

            lst = [] 
            counter_read += 1 
            if counter_read % 100000 == 0: 
                print("Read lines: ", str(counter_read))

            for val in dp: 
                val = float( val.strip() )
                lst.append(val) 
            return lst

        with data_file_path.open("r") as f:
            reader = csv.reader(f, delimiter=",")
            print("Data read from file")
            self.data = [prepare_data(dp) for dp in reader]
            print("Data converted")
            random.shuffle(self.data)
        self.size = len(self.data) 
        self.pointer = 0 
    
    def sample(self,N):
        if self.pointer + N > self.size -1: 
            self.pointer = 0 
            random.shuffle(self.data)
        samples = self.data[self.pointer:self.pointer+N]
        # add noise 
        if add_noise_to_real_data: 
            for q in range(0,N): 
                noise = np.random.uniform(-0.05,0.05,input_length_data)
                samples[q] = samples[q] + noise 
        self.pointer = self.pointer + N 
        return samples

    def __len__(self): 
        return self.size

ndf = NetflowDataFlow(input_file)
DIM = input_length_data # Model dimensionality


def GeneratorAndDiscriminator():
    return FCGenerator, FCDiscriminator

def LeakyReLU(x, alpha=0.2):
    return tf.maximum(alpha*x, x)

def ReLULayer(name, n_in, n_out, inputs):
    output = lib.ops.linear.Linear(name+'.Linear', n_in, n_out, inputs, initialization='he')
    return tf.nn.relu(output)

def LeakyReLULayer(name, n_in, n_out, inputs):
    output = lib.ops.linear.Linear(name+'.Linear', n_in, n_out, inputs, initialization='he')
    return LeakyReLU(output)

# ! Generators
def FCGenerator(n_samples, noise=None, FC_DIM=fully_connected_dim):
    if noise is None:
        noise = tf.random_normal([n_samples, input_length_noise])

    output = ReLULayer('Generator.1', input_length_noise, FC_DIM, noise)
    output = ReLULayer('Generator.2', FC_DIM, FC_DIM, output)
    output = ReLULayer('Generator.3', FC_DIM, FC_DIM, output)
    output = ReLULayer('Generator.4', FC_DIM, FC_DIM, output)
    output = ReLULayer('Generator.Out', FC_DIM, input_length_data, output)
    #output = tf.tanh(output) # TODO check that 

    return output

# ! Discriminators
def FCDiscriminator(inputs, FC_DIM=fully_connected_dim, n_layers=3):
    output = LeakyReLULayer('Discriminator.Input', input_length_data, FC_DIM, inputs)
    for i in range(n_layers):
        output = LeakyReLULayer('Discriminator.{}'.format(i), FC_DIM, FC_DIM, output)
    output = lib.ops.linear.Linear('Discriminator.Out', FC_DIM, 1, output)

    return tf.reshape(output, [-1])


Generator, Discriminator = GeneratorAndDiscriminator()

with tf.Session(config=tf.ConfigProto(allow_soft_placement=True)) as session:

    #all_real_data_conv = tf.placeholder(tf.int32, shape=[BATCH_SIZE, 3, DIM, DIM]) # TODO weglöschen 
    all_real_data_conv = tf.placeholder(tf.float32, shape=[BATCH_SIZE, input_length_data])

    if tf.__version__.startswith('1.'):
        split_real_data_conv = tf.split(all_real_data_conv, len(DEVICES))
    else:
        split_real_data_conv = tf.split(0, len(DEVICES), all_real_data_conv)
    gen_costs, disc_costs = [],[]

    for device_index, (device, real_data_conv) in enumerate(zip(DEVICES, split_real_data_conv)):
        with tf.device(device):

            real_data = real_data_conv
            fake_data = Generator(BATCH_SIZE//len(DEVICES))
 
            disc_fake = Discriminator(fake_data)
            disc_real = Discriminator(real_data)
           

            if MODE == 'wgan':
                gen_cost = -tf.reduce_mean(disc_fake)
                disc_cost = tf.reduce_mean(disc_fake) - tf.reduce_mean(disc_real)

            elif MODE == 'wgan-gp':
                gen_cost = -tf.reduce_mean(disc_fake)
                disc_cost = tf.reduce_mean(disc_fake) - tf.reduce_mean(disc_real)

                alpha = tf.random_uniform(
                    shape=[BATCH_SIZE//len(DEVICES),1],
                    minval=0.,
                    maxval=1.
                )
                differences = fake_data - real_data
                interpolates = real_data + (alpha*differences)
                gradients = tf.gradients(Discriminator(interpolates), interpolates)[0]
                slopes = tf.sqrt(tf.reduce_sum(tf.square(gradients), reduction_indices=[1]))
                gradient_penalty = tf.reduce_mean((slopes-1.)**2)
                disc_cost += LAMBDA*gradient_penalty
            else:
                raise Exception()

            gen_costs.append(gen_cost)
            disc_costs.append(disc_cost)

    gen_cost = tf.add_n(gen_costs) / len(DEVICES)
    disc_cost = tf.add_n(disc_costs) / len(DEVICES)

    if MODE == 'wgan':
        gen_train_op = tf.train.RMSPropOptimizer(learning_rate=G_LR).minimize(gen_cost,
                                             var_list=lib.params_with_name('Generator'), colocate_gradients_with_ops=True)
        disc_train_op = tf.train.RMSPropOptimizer(learning_rate=D_LR).minimize(disc_cost,
                                             var_list=lib.params_with_name('Discriminator.'), colocate_gradients_with_ops=True)

        clip_ops = []
        for var in lib.params_with_name('Discriminator'):
            clip_bounds = [-.01, .01]
            clip_ops.append(tf.assign(var, tf.clip_by_value(var, clip_bounds[0], clip_bounds[1])))
        clip_disc_weights = tf.group(*clip_ops)

    elif MODE == 'wgan-gp':
        gen_train_op = tf.train.AdamOptimizer(learning_rate=G_LR, beta1=BETA1_G, beta2=0.9).minimize(gen_cost,
                                          var_list=lib.params_with_name('Generator'), colocate_gradients_with_ops=True)
        disc_train_op = tf.train.AdamOptimizer(learning_rate=D_LR, beta1=BETA1_D, beta2=0.9).minimize(disc_cost,
                                           var_list=lib.params_with_name('Discriminator.'), colocate_gradients_with_ops=True)
    else:
        raise Exception()

    # For generating samples
    fixed_noise = tf.constant(np.random.normal(size=(BATCH_SIZE, input_length_noise)).astype('float32'))
    all_fixed_noise_samples = []
    for device_index, device in enumerate(DEVICES):
        n_samples = BATCH_SIZE // len(DEVICES)
        all_fixed_noise_samples.append(Generator(n_samples,
                                                 noise=fixed_noise[device_index*n_samples:(device_index+1)*n_samples]))
    if tf.__version__.startswith('1.'):
        all_fixed_noise_samples = tf.concat(all_fixed_noise_samples, axis=0)
    else:
        all_fixed_noise_samples = tf.concat(0, all_fixed_noise_samples)



    session.run(tf.global_variables_initializer())

    # For generating samples 
    #sample_noise = tf.constant(np.random.normal(size=(1024, input_length_noise)).astype('float32'))
    samples_1024 = Generator(1024)
    def generate_final_flows(out_text,num_runs): 
        for z in range(0,num_runs): 
            samples = session.run(samples_1024)
            for i in range(0,100): 
                a = session.run(samples_1024)
                samples = np.concatenate((samples,a),axis=0)
            np.savetxt(out_text+"_"+str(z)+".csv",samples,delimiter=",")

    ITERS = int( (num_epochs * counter_read) / BATCH_SIZE ) 
    epoch = 0 
    old_epoch = 0 
    # Train loop
    for it in range(ITERS):
        
        iteration = it
        epoch = int( (iteration * BATCH_SIZE) / counter_read) 

        if epoch > old_epoch:
            if epoch > 4:# and epoch % 10 == 0:  
                generate_final_flows(conf_name+"_epoch"+str(epoch),100)
            else:
                generate_final_flows(conf_name+"_epoch"+str(epoch),1)
        old_epoch = epoch

        # Train generator
        if iteration > 0:
            _ = session.run(gen_train_op)

        # Train critic
        disc_iters = CRITIC_ITERS
        for i in range(disc_iters):
            _data = ndf.sample(BATCH_SIZE)  # gen.__next__()
            _disc_cost, _ = session.run([disc_cost, disc_train_op], feed_dict={all_real_data_conv: _data})
            if MODE == 'wgan':
                _ = session.run([clip_disc_weights])

        if iteration % 100 == 0: 
            print("Step ", iteration, " von ", ITERS, "(",epoch,"): Disc_cost:", _disc_cost)
    
    # Store final outputs 
    generate_final_flows(conf_name+"_final",100)

   
