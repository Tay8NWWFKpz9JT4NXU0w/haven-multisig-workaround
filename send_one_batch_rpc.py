####################
#(Optional update) Names of the wallet files which will be created
##################### 
wallet_1="wallet_1" #Temporary file name of the first multisig wallet. 
wallet_2="wallet_2" #Temporary file name of the second multisig wallet. 
temp_wallet_1="temp_1" #Temporary file name of the first multisig wallet. 
temp_wallet_2="temp_2" #Temporary file name of the second multisig wallet. 
temp_wallet_dir="E:/testnet"

temp_multisig_exp="temp_exp"  #Temporary file name of the multisig info export. It will be created from the first wallet and imported into the second.

####################
#(Mandatory update) 
# Seed phrases of the 2 multisig wallets, can be obtained by using "seed" on a finalized multisig wallet
# Target wallet where funds will be sent to
##################### 

target_wallet="hvtaJAH6cqjEDBaFSgNDY46bqNGzvWNPxTmm8LQABumWHw6EZKqYhoaBSUbuPfTrsw6sw92XLzmKchJPsCuCjNVY6Y9kmHajER"
####################
#Arguments which depend on the environment
#Paths to havend and haven-wallet-cli
#Extra parameters for haven-wallet-cli and havend (e.g. testnet), can be left blank
#How many blocks at a time to scan
#How many spent outputs at a time to freeze (having this number too high might break things, 50 seems to work)
#RPC ports for the offline daemon and for the online daemon
##################### 
haven_wallet_cli_path="E:/testnet/haven-wallet-cli.exe" #Path to haven-wallet-cli
haven_wallet_rpc_path="E:/testnet/haven-wallet-rpc.exe" #Path to haven-wallet-cli
havend_path="E:/testnet/havend.exe"
haven_wallet_cmd_options="--testnet" #Daemon must be in offline mode
blocks_at_a_time=500 #How many blocks to be loaded in the wallets at a time
havend_path="E:/testnet/havend.exe"
havend_cmd_options="--testnet"

daemon_1_rpc_port='18081' # Offline daemon
daemon_2_rpc_port='27750' # Online daemon
wallet_rpc_port='14591' # Randon port at which the Wallet RPC is started, feel free to change it

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
import shutil
import time

headers = {'Content-Type': 'application/json',}

####################
#Get current block height from offline and online daemon
##################### 

print('Get block height for offline daemon')
data = '{"jsonrpc":"2.0","id":"0","method":"get_block_count"}'
response = requests.post('http://127.0.0.1:'+daemon_1_rpc_port+'/json_rpc', headers=headers, data=data)
print("RPC call status: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
height=json_obj['result']['count']
print('Offline daemon block height:' + str(height))


print('Get block height for offline daemon')
data = '{"jsonrpc":"2.0","id":"0","method":"get_block_count"}'
response = requests.post('http://127.0.0.1:'+daemon_2_rpc_port+'/json_rpc', headers=headers, data=data)
print("RPC call status: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
online_height=json_obj['result']['count']
print('Online daemon block height:' + str(online_height))
####################
#Stop Wallet RPC
#Just in case it is running already
##################### 


data = '{"jsonrpc":"2.0","id":"0","method":"stop_wallet"}'
try:
	response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
	print("RPC call status: "+str(response.status_code))
except:
	print('Wallet RPC is not running, so there is no need to stop it')

time.sleep(5)

####################
#Start Wallet RPC
##################### 


wallet_rpc_proc=subprocess.Popen(haven_wallet_rpc_path+' '+haven_wallet_cmd_options+' --password "" --log-level 0 --disable-rpc-login --rpc-bind-ip 127.0.0.1 --rpc-bind-port '+wallet_rpc_port+' --wallet-dir '+temp_wallet_dir, shell=True, stdout=subprocess.DEVNULL)
time.sleep(5)


####################
#Recreate first multisig wallet
#Refresh height is set to current offline daemon block - blocks_at_a_time - 60
#The 60 is an overlap, and it is needed to account for the blocks which appear locked
##################### 

wallet_file=wallet_1
temp_wallet_file=temp_wallet_1

if os.path.exists(wallet_file)==False:
	print('Wallet file ' + wallet_file+' not found')
	quit()
if os.path.exists(wallet_file+'.keys')==False:
	print('Wallet file ' + wallet_file+'.keys'+' not found')
	quit()

if os.path.exists(temp_wallet_file):
	os.remove(temp_wallet_file)
if os.path.exists(temp_wallet_file+".keys"):
	os.remove(temp_wallet_file+".keys")

shutil.copy(wallet_file+".keys", temp_wallet_file+".keys")
shutil.copy(wallet_file+".keys", temp_wallet_file+".keys")

##Open Wallet

data = '{"jsonrpc":"2.0","id":"0","method":"open_wallet","params":{"filename":"'+temp_wallet_file+'","password":""}}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Open Wallet')
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')

##Disable auto-refresh

data = '{"jsonrpc":"2.0","id":"0","method":"auto_refresh","params":{"enable":false, "period":10}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Disable auto-refresh')
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')


##Connect to offline daemon

data = '{"jsonrpc":"2.0","id":"0","method":"set_daemon","params": {"address":"http://localhost:'+daemon_1_rpc_port+'","trusted":true}},'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Connect to offline daemon')
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')



##Refresh
refresh_height=int(height)-blocks_at_a_time
if refresh_height<0:
    refresh_height=0

data = '{"jsonrpc":"2.0","id":"0","method":"refresh","params":{"start_height":'+str(refresh_height)+'}}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Refresh from block '+str(refresh_height))
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')


##Connect to online daemon

data = '{"jsonrpc":"2.0","id":"0","method":"set_daemon","params": {"address":"http://localhost:'+daemon_2_rpc_port+'","trusted":true}},'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Connect to offline daemon')
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')

##Refresh

data = '{"jsonrpc":"2.0","id":"0","method":"refresh","params":{"start_height":'+str(online_height-10)+'}}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Refresh from block '+str(refresh_height))
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')



####################
#Recreate multisig export
##################### 

data = '{"jsonrpc":"2.0","id":"0","method":"export_multisig_info"}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Export multisig data ')
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
multisig_data=json_obj['result']['info']
print('Multisig data length: '+str(len(multisig_data)))
print('################')


####################
#Save Wallet 1
##################### 

data = '{"jsonrpc":"2.0","id":"0","method":"store"}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print("Save Wallet 1 RPC code:  " + str(response.status_code))
print('################')


####################
#Recreate the second multisig wallet
#Refresh height is set to current offline daemon block - blocks_at_a_time - 60
#The 60 is an overlap, and it is needed to account for the blocks which appear locked
##################### 

##Connect to offline daemon

data = '{"jsonrpc":"2.0","id":"0","method":"set_daemon","params": {"address":"http://localhost:'+daemon_1_rpc_port+'","trusted":true}},'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Connect to offline daemon')
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')




wallet_file=wallet_2
temp_wallet_file=temp_wallet_2

if os.path.exists(wallet_file)==False:
	print('Wallet file ' + wallet_file+' not found')
	quit()
if os.path.exists(wallet_file+'.keys')==False:
	print('Wallet file ' + wallet_file+'.keys'+' not found')
	quit()

if os.path.exists(temp_wallet_file):
	os.remove(temp_wallet_file)
if os.path.exists(temp_wallet_file+".keys"):
	os.remove(temp_wallet_file+".keys")

shutil.copy(wallet_file+".keys", temp_wallet_file+".keys")
shutil.copy(wallet_file+".keys", temp_wallet_file+".keys")

##Open Wallet

data = '{"jsonrpc":"2.0","id":"0","method":"open_wallet","params":{"filename":"'+temp_wallet_file+'","password":""}}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Open Wallet')
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')

##Disable auto-refresh

data = '{"jsonrpc":"2.0","id":"0","method":"auto_refresh","params":{"enable":false, "period":10}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Disable auto-refresh')
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')

##Refresh

data = '{"jsonrpc":"2.0","id":"0","method":"refresh","params":{"start_height":'+str(refresh_height)+'}}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Refresh from block '+str(refresh_height))
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')


##Connect to online daemon

data = '{"jsonrpc":"2.0","id":"0","method":"set_daemon","params": {"address":"http://localhost:'+daemon_2_rpc_port+'","trusted":true}},'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Connect to offline daemon')
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')

##Refresh

data = '{"jsonrpc":"2.0","id":"0","method":"refresh","params":{"start_height":'+str(online_height-10)+'}}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Refresh from block '+str(refresh_height))
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')

##Connect to offline daemon

data = '{"jsonrpc":"2.0","id":"0","method":"set_daemon","params": {"address":"http://localhost:'+daemon_1_rpc_port+'","trusted":true}},'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Connect to offline daemon')
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')


####################
#Import multisig info
##################### 

data = '{"jsonrpc":"2.0","id":"0","method":"import_multisig_info","params":{"info":["'+multisig_data+'"]}}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Import multisig data ')
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
outputs_loaded=json_obj['result']['n_outputs']
print('Outputs loaded: '+str(outputs_loaded))
print('################')

##Connect to online daemon

data = '{"jsonrpc":"2.0","id":"0","method":"set_daemon","params": {"address":"http://localhost:'+daemon_2_rpc_port+'","trusted":true}},'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Connect to offline daemon')
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')

##Refresh

data = '{"jsonrpc":"2.0","id":"0","method":"refresh","params":{"start_height":'+str(online_height-10)+'}}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print('Refresh from block '+str(refresh_height))
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
print(json_obj)
print('################')

####################
#Freeze spent inputs
#
#This works by first creating a list of all unlocked key images, then making an RPC call to the live daemon to check if they are spent.
#If all inputs are spent, then there is nothing to do and generating a transfer is skipped
#Otherwise, all spent inputs are frozen (to avoid transaction rejection) in chunks of mark_as_spent_chunk_size
##################### 

list_key_images=[]


data = '{"jsonrpc":"2.0","id":"0","method":"incoming_transfers","params":{"transfer_type":"all"}}'

print('Exporting key images ')
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print("RPC return code: "+str(response.status_code))
json_obj = json.loads(response.content.decode())
if 'transfers' not in json_obj['result']:
	incoming_transfers=[]
else:
	incoming_transfers=json_obj['result']['transfers']

key_images=[]
for transfer in incoming_transfers:
	if transfer['unlocked']==True:
		key_images.append(transfer['key_image'])

print('Number of inputs in unlocked status: ' + str(len(key_images)))

key_images_rpc=','.join('"'+k+'"' for k in key_images)

headers = {'Content-Type': 'application/json',}
data = '{"key_images":['+key_images_rpc+']}'
response = requests.post('http://127.0.0.1:'+daemon_2_rpc_port+'/is_key_image_spent', headers=headers, data=data)
print("RPC call status: "+str(response.status_code))

json_obj = json.loads(response.content.decode())

i=0
spent_images=[]
if len(key_images)>0:
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


if all_inputs_spent==False:
	for spent_img in spent_key_images:
		data='{"jsonrpc":"2.0","id":"0","method":"freeze","params":{"key_image":"'+spent_img+'"}}'
		response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)


data = '{"jsonrpc":"2.0","id":"0","method":"incoming_transfers","params":{"transfer_type":"all"}}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
json_obj = json.loads(response.content.decode())

if 'transfers' not in json_obj['result']:
	incoming_transfers=[]
else:
	incoming_transfers=json_obj['result']['transfers']


frozen_count=0
for transfer in incoming_transfers:
	if transfer['frozen']==True:
		frozen_count+=1

print('Frozen + ' + str(frozen_count) + ' out of ' + str(len(spent_key_images)) + ' spent inputs')

#quit()
################################
#Extract all XHV, XUSD, and XBTC
################################

asset_types=['XHV','XUSD','XBTC']
if all_inputs_spent:
	asset_types=[]

multisig_txset_list=[]


for asset_type in asset_types:
	####################
	#Create transfer
	#####################
	'''
	data = '{"jsonrpc":"2.0","id":"0","method":"set_daemon","params": {"address":"http://localhost:'+daemon_1_rpc_port+'","trusted":true}},'
	response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
	print('################')
	print('Connect to offline daemon')
	print("RPC return code: "+str(response.status_code))
	'''
	data='{"jsonrpc":"2.0","id":"0","method":"sweep_all","params":{"address":"'+target_wallet+'","asset_type":"'+asset_type+'"}}'
	#data='{"jsonrpc":"2.0","id":"0","method":"transfer","params":{"destinations":[{"amount":10,"address":"'+target_wallet+'"}],"account_index":0,"subaddr_indices":[0]}}'	
	print('Creating transactions: ' + data) 	
	response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
	print("RPC return code: "+str(response.status_code))
	json_obj = json.loads(response.content.decode())	

	if 'result' not in json_obj:
		print(json_obj['error']['message'])
	else:
		multisig_txset=json_obj['result']['multisig_txset']
		multisig_txset_list.append(multisig_txset)

####################
#Save Wallet 2
##################### 

data = '{"jsonrpc":"2.0","id":"0","method":"store"}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print("Save Wallet 1 RPC code:  " + str(response.status_code))
print('################')



data = '{"jsonrpc":"2.0","id":"0","method":"close_wallet"}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('Closing wallet, RPC response')
print(str(response.status_code))

data = '{"jsonrpc":"2.0","id":"0","method":"open_wallet","params":{"filename":"'+temp_wallet_1+'","password":""}}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('Opening wallet 1, RPC response: ')
print(str(response.status_code))


for multisig_txset in multisig_txset_list:
		
	data='{"jsonrpc":"2.0","id":"0","method":"sign_multisig","params":{"tx_data_hex":"'+multisig_txset+'"}}'
	response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
	print("Signing multisig, RPC response" + str(response.status_code))

	json_obj = json.loads(response.content.decode())
	
	if 'result' not in json_obj:
		print(json_obj['error']['message'])
		tx_data_hex=''
	else:	
		tx_data_hex=json_obj['result']['tx_data_hex']
	


	print('Submitting multisig')
	data='{"jsonrpc":"2.0","id":"0","method":"submit_multisig","params":{"tx_data_hex":"'+tx_data_hex+'"}}'
	response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
	print("RPC return code: "+str(response.status_code))
	json_obj = json.loads(response.content.decode())
	print(json_obj)

####################
#Save Wallet 1
##################### 

data = '{"jsonrpc":"2.0","id":"0","method":"store"}'
response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
print('################')
print("Save Wallet 1 RPC code:  " + str(response.status_code))
print('################')
	

data = '{"jsonrpc":"2.0","id":"0","method":"stop_wallet"}'
try:
	response = requests.post('http://127.0.0.1:'+wallet_rpc_port+'/json_rpc',headers=headers, data=data)
	print("RPC call status: "+str(response.status_code))
except:
	print('Wallet RPC is not running, so there is no need to stop it')

time.sleep(5)


####################
#Pop blocks
#Pops blocks from the offline daemon
##################### 
print('popping blocks')
subprocess.run(havend_path+' '+havend_cmd_options+' --rpc-bind-port '+daemon_1_rpc_port+' pop_blocks ' + str(blocks_at_a_time), shell=True)
