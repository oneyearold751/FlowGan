Step 1: Use CIDDS-001 data set # We used in our experiments the non-anonymized CIDDS-001 data set 

Step 2: Split data set in week1 and week2-4

Step 3: Convert big Byte-Flows with script ./data/updateNetFlowFormat.py INPUT_FILE OUTPUT_FILE

Step 4: optional - learn embeddings with IP2Vec 
extract context attributs with script ./ip2vec/preprocessing/extractContext.py 
>>> python3 extractContext.py INPUT_FILE OUTPUT_FILE

Step 5: optional - learn embeddings with script ./ip2vec/ip2vec_oneEmbedding.py 
>>> python3 ip2vec_oneEmbedding.py INPUT_FILE 

Step 6: Create Baseline with script ./baseline/generateBaseline.py 
>>> python3 generateBaseline.py INPUT_FILE OUTPUT_FILE NUM_EXAMPLES

Step 7: Prepare data for GAN 

Step 7a: Binarize data with script  ./preprocess_input/preprocess_for_binar.py 
>>> python3 preprocess_for_binar.py INPUT_FILE OUTPUT_FILE 

Step 7b: Numeric translation of data using script ./preprocess_input/preprocess_for_numeric.py 
>>> python3 preprocess_for_numeric.py INPUT_FILE OUTPUT_FILE 

Step 7c: Embeddings translation using script ./preprocess_input/preprocess_for_embeddings.py 
>>> python3 preprocess_for_embedding.py INPUT_FILE EMBEDDING_FILE OUTPUT_FILE 


Step 8: Generate new data with WGAN-GP  
Step 8a: Script ./wgan_gp/gan_flow_binar.py 
>>> python3 gan_flow_binar.py INPUT_FILE 
Step 8b: Script ./wgan_gp/gan_flow_numeric.py 
>>> python3 gan_flow_numeric.py INPUT_FILE 
Step 8c: Script ./wgan_gp/gan_flow_embedding.py 
>>> python3 gan_flow_embedding.py INPUT_FILE 


Step 9: Convert back data 
Step 9a: Script ./decode_gan_results/decode_binar.py 
>>> python3 decode_binar.py INPUT_FILE ORGI_FILE OUTPUT_FILE

Step 9b: Script ./decode_gan_results/decode_numeric.py 
>>> python3 decode_numeric.py INPUT_FILE ORGI_FILE OUTPUT_FILE

Step 9c: Script ./decode_gan_results/decode_embedding.py 
>>> python3 decode_embedding.py INPUT_FILE EMBEDDING_FILE OUTPUT_FILE



