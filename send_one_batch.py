####################
#(Optional update) Names of the wallet files which will be created
##################### 
temp_wallet_1="temp_1" #Temporary file name of the first multisig wallet. It will be restored from seed.
temp_wallet_2="temp_2" #Temporary file name of the second multisig wallet. It will be restored from seed.
temp_multisig_exp="temp_exp"  #Temporary file name of the multisig info export. It will be created from the first wallet and imported into the second.

####################
#(Mandatory update) 
# Seed phrases of the 2 multisig wallets, can be obtained by using "seed" on a finalized multisig wallet
# Target wallet where funds will be sent to
##################### 

seed_1="0200000003000000afcae1f567e5b23da5357897588d8c385dd104b101486fc692084a2a2632370cc7a5efe71e4efa485be6492c11217bd449358d06dfa00ec99428c92e25653bbc99923eb85b93a3fcb2c3b3d0f15c136912a7c9aa510ffc95235a9e8b4767b4075db4172cc53e6981b28289fa9e2324ab2ce234927ff0eff70add8cfaeb921d509d1b7429d2807962b639dd6c724796c9e736e01d28c53ed04a7ab493e03c590312af6dcc956439dbeefb9a2ae645f66e759a2493d98230f6478e959645f5dd0852c5fcf8f916159f6df07759d1d2d20e8ae25abd57c9442ca5a6ad7896e72288cb4a5366e22ba7f1c5832e727ac6d7e25eab761033a6772f3077b9a1088d5257c7b3fe3ded3d7653303102908992be96a0223e34677109d906a417dfd9222b8a"
seed_2="0200000003000000faca5784a4504fdf1b353c943a13ac8903af9be219833ba46429e393c5172d0ec7a5efe71e4efa485be6492c11217bd449358d06dfa00ec99428c92e25653bbc99923eb85b93a3fcb2c3b3d0f15c136912a7c9aa510ffc95235a9e8b4767b4075db4172cc53e6981b28289fa9e2324ab2ce234927ff0eff70add8cfaeb921d50e81beab70eec15042d39a16954cdb51a8e14774f40000bae1c9b4dfd7f224f0512af6dcc956439dbeefb9a2ae645f66e759a2493d98230f6478e959645f5dd0852c5fcf8f916159f6df07759d1d2d20e8ae25abd57c9442ca5a6ad7896e72288cb4a5366e22ba7f1c5832e727ac6d7e25eab761033a6772f3077b9a1088d5257c7b3fe3ded3d7653303102908992be96a0223e34677109d906a417dfd9222b8a"
target_wallet="hvtaJAH6cqjEDBaFSgNDY46bqNGzvWNPxTmm8LQABumWHw6EZKqYhoaBSUbuPfTrsw6sw92XLzmKchJPsCuCjNVY6Y9kmHajER"

####################
#Arguments which depend on the environment
#Paths to havend and haven-wallet-cli
#Extra parameters for haven-wallet-cli and havend (e.g. testnet), can be left blank
#How many blocks at a time to scan
#How many spent outputs at a time to freeze (having this number too high might break things, 50 seems to work)
#RPC ports for the offline daemon and for the online daemon
##################### 
haven_wallet_cli_path="./haven-wallet-cli" #Path to haven-wallet-cli
haven_wallet_cmd_options="--testnet" #Daemon must be in offline mode
haven_wallet_cmd_options_submit="--testnet" #Daemon must be in online mode
blocks_at_a_time=300 #How many blocks to be loaded in the wallets at a time
havend_path="./havend"
havend_cmd_options="--testnet"

mark_as_spent_chunk_size=50
daemon_1_rpc_port='18081' # Offline daemon
daemon_2_rpc_port='27750' # Online daemon


####################
####################
####################
#     START
####################
####################
####################

import subprocess
import os
import requests
import json



####################
#Recreate first multisig wallet
#Refresh height is set to current offline daemon block - blocks_at_a_time - 60
#The 60 is an overlap, and it is needed to account for the blocks which appear locked
##################### 

wallet_file=temp_wallet_1
seed=seed_1

if os.path.exists(wallet_file):
	os.remove(wallet_file)
if os.path.exists(wallet_file+".keys"):
	os.remove(wallet_file+".keys")


input_msg=wallet_file+'\ny\n'+seed+'\n\n0\n\n'
subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --offline --password "" --restore-multisig-wallet', input=input_msg.encode(), shell=True)
subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --daemon-address 127.0.0.1:'+daemon_1_rpc_port+' --wallet-file '+wallet_file+' --password "" set ask-password 0', input='\n'.encode(), shell=True)
cmd_output=subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --daemon-address 127.0.0.1:'+daemon_1_rpc_port+' --wallet-file '+wallet_file+' --password "" status', input='\n'.encode(), shell=True, capture_output=True)
cmd_output=cmd_output.stdout.decode()
last_line=cmd_output.splitlines()[-1]
height=last_line.split("/")[1].split(",")[0]
refresh_height=int(height)-blocks_at_a_time-60
subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --daemon-address 127.0.0.1:'+daemon_1_rpc_port+' --wallet-file '+wallet_file+' --password "" set refresh-from-block-height '+str(refresh_height), input='\n'.encode(), shell=True)
print('Refreshing:')
cmd_output=subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --daemon-address 127.0.0.1:'+daemon_1_rpc_port+' --wallet-file '+wallet_file+' --password "" refresh', input='\n'.encode(), shell=True, capture_output=True)
cmd_output=cmd_output.stdout.decode()
print(cmd_output.splitlines()[-1])


####################
#Recreate second multisig wallet
##################### 


wallet_file=temp_wallet_2
seed=seed_2

if os.path.exists(wallet_file):
	os.remove(wallet_file)
if os.path.exists(wallet_file+".keys"):
	os.remove(wallet_file+".keys")


input_msg=wallet_file+'\ny\n'+seed+'\n\n0\n\n'
subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --offline --password "" --restore-multisig-wallet', input=input_msg.encode(), shell=True)
subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --daemon-address 127.0.0.1:'+daemon_1_rpc_port+' --wallet-file '+wallet_file+' --password "" set ask-password 0', input='\n'.encode(), shell=True)
subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --daemon-address 127.0.0.1:'+daemon_1_rpc_port+' --wallet-file '+wallet_file+' --password "" set refresh-from-block-height '+str(refresh_height), input='\n'.encode(), shell=True)
print('Refreshing:')
cmd_output=subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --daemon-address 127.0.0.1:'+daemon_1_rpc_port+' --wallet-file '+wallet_file+' --password "" refresh', input='\n'.encode(), shell=True, capture_output=True)
cmd_output=cmd_output.stdout.decode()
print(cmd_output.splitlines()[-1])




####################
#Recreate multisig export
##################### 

if os.path.exists(temp_multisig_exp):
	os.remove(temp_multisig_exp)
print('Exporting multisig info:')
subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --daemon-address 127.0.0.1:'+daemon_1_rpc_port+' --wallet-file '+temp_wallet_1+' --password "" export_multisig_info '+temp_multisig_exp, shell=True)

####################
#Import multisig export
##################### 
print('Importing multisig info (it is the slowest operation):')
cmd_output=subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --daemon-address 127.0.0.1:'+daemon_1_rpc_port+' --wallet-file '+temp_wallet_2+' --password "" import_multisig_info '+temp_multisig_exp, shell=True, capture_output=True)
cmd_output=cmd_output.stdout.decode()
last_line=cmd_output.splitlines()[-1]
print(last_line)



####################
#Freeze spent inputs
#
#This works by first creating a list of all unlocked key images, then making an RPC call to the live daemon to check if they are spent.
#If all inputs are spent, then there is nothing to do and generating a transfer is skipped
#Otherwise, all spent inputs are frozen (to avoid transaction rejection) in chunks of mark_as_spent_chunk_size
##################### 

list_key_images=[]
cmd_output=subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options_submit+' --wallet-file '+temp_wallet_2+' --password "" incoming_transfers verbose', shell=True, capture_output=True)
cmd_output=cmd_output.stdout.decode()
cmd_output=cmd_output.splitlines()
key_images=[]
rpc_call_string=''
for line in cmd_output:
	a=line.split()
	if len(a)>=4:
		if (a[3]=='RingCT') and (a[2] != 'locked') :
			key_images.append(a[8])
key_images_rpc=','.join('"'+k+'"' for k in key_images)


headers = {'Content-Type': 'application/json',}
data = '{"key_images":['+key_images_rpc+']}'
response = requests.post('http://127.0.0.1:'+daemon_2_rpc_port+'/is_key_image_spent', headers=headers, data=data)
print("RPC call status: "+str(response.status_code))

json_obj = json.loads(response.content.decode())
i=0
spent_images=[]
for j in json_obj['spent_status']:
	i+=j
	spent_images.append(j)
all_inputs_spent=(i==len(key_images))
if all_inputs_spent:
	print('All inputs in the current range were already spent, nothing to do')

spent_key_images=[]
for (i,j) in zip(key_images,spent_images):
	if j==1:
		spent_key_images.append(i)

spent_chunks = (spent_key_images[i:i + mark_as_spent_chunk_size] for i in range(0, len(spent_key_images), mark_as_spent_chunk_size))
if all_inputs_spent==False:
	for i in spent_chunks:
		print('Freezing '+str(len(i))+' key images which were spent in later blocks ...')
		input_cmd='\nfreeze '+'\nfreeze '.join(i)
		cmd_output=subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --daemon-address 127.0.0.1:'+daemon_1_rpc_port+' --wallet-file '+temp_wallet_2+' --password "" ', shell=True, input=input_cmd.encode(), capture_output=True)
		cmd_output=cmd_output.stdout.decode()
		cmd_output=cmd_output.splitlines()
		print(cmd_output[-1])

################################
#Extract all XHV, XUSD, and XBTC
################################

transfer_types=['sweep_all', 'offshore_sweep_all', 'xasset_sweep_all']
if all_inputs_spent:
	transfer_types=[]
for transfer_type in transfer_types:
	####################
	#Create transfer
	#####################
	if os.path.exists('multisig_haven_tx'):
		os.remove('multisig_haven_tx')

	transfer_cmd=transfer_type+' '+target_wallet
	if (transfer_type=="xasset_sweep_all"):
		transfer_cmd=transfer_cmd+' XBTC'
	print('Creating transactions: ' + transfer_cmd) 
	subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --daemon-address 127.0.0.1:'+daemon_1_rpc_port+' --wallet-file '+temp_wallet_2+' --password "" '+ transfer_cmd, input='y\ny\ny\n'.encode(), shell=True)


	####################
	#Sign transfer
	##################### 
	print('Signing transactions:')
	subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options+' --daemon-address 127.0.0.1:'+daemon_1_rpc_port+' --wallet-file '+temp_wallet_1+' --password "" sign_multisig multisig_haven_tx', input='y\ny\ny\n'.encode(), shell=True)


	####################
	#Send transfer
	##################### 
	print('Submit transactions:')
	subprocess.run(haven_wallet_cli_path+' '+haven_wallet_cmd_options_submit+' --daemon-address 127.0.0.1:'+daemon_2_rpc_port+' --wallet-file '+temp_wallet_1+' --password "" submit_multisig multisig_haven_tx', input='y\ny\ny\n'.encode(), shell=True)


####################
#Pop blocks
#Pops blocks from the offline daemon
##################### 
print('popping blocks')
subprocess.run(havend_path+' '+havend_cmd_options+' --rpc-bind-port '+daemon_1_rpc_port+' pop_blocks ' + str(blocks_at_a_time), shell=True)



