#! /usr/bin/python

#from api_func.api_func import *
import api_helpers.cw_abstract as API
import pandas, json, sys, argparse
#from io import StringIO
from pprint import pprint

debug = True
query_size = 1000 #number of items to pull from the LM API, helps with pagination

#########################
# CLI ARGUMENT HANDLING #
#########################
parser=argparse.ArgumentParser()
parser.add_argument('-file', help='Path to file containing API credentials', default='keyfile.txt')
args = parser.parse_args()

###################
# PARSE API CREDS #
###################
with open(args.file) as file: config = json.loads(file.read())
lm_creds = {
	"_lm_api_id": config['lm_id'],
	"_lm_api_key": config['lm_key'],
	"_lm_company": config['lm_company']
}
cw_creds = {
	"_cw_api_id": config['cw_id'],
	"_cw_api_key": config['cw_key'],
	"_cw_company": config['cw_company'],
	"_cw_site": config['cw_site'],
	"_cw_agentId": config['cw_agentId']
}
creds = {}
creds.update(lm_creds)
creds.update(cw_creds)

# Synchronize Types from LM to CW
get_types = API.type_sync(_group_id = config['lm_group_id'], **creds)
type_dict = get_types.items()
if get_types["result"] == False:
	print(f"Error synchronizing ConnectWise types.\n{get_types['items']}\n")
	type_dict = {}

# Synchronize Companies from LM to CW
get_companies = API.company_sync(**creds)
company_dict = get_companies.items()
if get_companies["result"] == False:
	print(f"Error synchronizing ConnectWise companies.\n{get_companies['items']}\n")
	company_dict = {}

###########################
# GET ALL DEVICES FROM LM #
###########################
# Request Info
resourcePath = '/device/devices'
data         = ''
last_item_found = False
devices = []
fields = 'id,name,displayName,hostGroupIds,customProperties,systemProperties,autoProperties,inheritedProperties'
while not last_item_found:
	queryParams  = f'?size={query_size}&offset={len(devices)}&fields={fields}'
	current_call_devices = json.loads(API.LM_GET(config['lm_id'], config['lm_key'], config['lm_company'], resourcePath, queryParams, data)['body'])['data']['items']
	if len(current_call_devices) < query_size: last_item_found = True
	devices += current_call_devices

if debug:
	for device in devices:
		print(f"""ID: {device['id']}
		Name: {device['name']}
		displayName: {device['displayName']}
		hostGroupIds: {device['hostGroupIds']}""")
		print("\tcustomProperties:")
		pprint(device['customProperties'])
		print("\tsystemProperties")
		pprint(device['systemProperties'])
		print("\tautoProperties")
		pprint(device['autoProperties'])
		print("\tinheritedProperties")
		pprint(device['inheritedProperties'])

device_array = {}
for item in devices:
	#gather information from the device in LM
	device_name = item['displayName']

	#create an entry in the final array for this device
	device_array[device_name] = {}

	########
	# NAME #
	########
	device_array[device_name]['name'] = device_name

	##############
	# PROPERTIES #
	##############
	#extract device properties from LM data to use in CW fields, could probably use list comprehension here
	all_properties = {}
	for dict in item['systemProperties']:    all_properties[dict['name']] = dict['value']
	for dict in item['systemProperties']:    all_properties[dict['name']] = dict['value']
	for dict in item['autoProperties']:      all_properties[dict['name']] = dict['value']
	for dict in item['customProperties']:    all_properties[dict['name']] = dict['value']
	for dict in item['inheritedProperties']: all_properties[dict['name']] = dict['value']
	#now all the properties are in a single dictionary with the property name as the key.

	for key, value in all_properties.items():
		if(key == 'system.ips'):     device_array[device_name]['ipAddress'] = value.split(',')[0]
		if(key == 'system.sysinfo'): device_array[device_name]['osType'] = value[:250]
		if(key == 'system.uptime'):  device_array[device_name]['uptime'] = value
		if(key == 'system.model'):   device_array[device_name]['modelNumber'] = value[:50]
		if('serial' in key):         device_array[device_name]['serialNumber'] = value
		if('model' in key):          device_array[device_name]['modelNumber'] = value[:50]
		if(key == 'location'):       device_array[device_name]['location'] = value
		if(key == 'company'):        company = value
		#else:                        company = 'Unknown' #setting a default value if company isn't found in the properties

	########
	# TYPE #
	########
	# Let's figure out best Configuration Type to use
	# Initialize array of host groups and check which 'Device by Type' group we're in
	host_group_array = [int(x) for x in item['hostGroupIds'].split(',')]

	# Initialize an array to hold all 'Device by Type' groups that this device is a member of
	return_type_array = []
	#check all the available LM types (the names of the sub-groups) to see if any of them belong to this device
	for key, value in type_dict.items():
		#ignore the collector type. if this type belongs to the host...
		if key != 'Collectors' and value['lm_id'] in host_group_array: return_type_array.append(key)
	# Every device must have a configuration type, so append 'Misc'. We're only using the first one in this list anyway.
	return_type_array.append('Misc')

	# Assign a type dict that contains the type ID and type Name to this device
	if len(type_dict) > 0: type_id = type_dict[return_type_array[0]]['cw_id']
	else: type_id = 0
	device_array[device_name]['type'] = {'id': type_id, 'name': return_type_array[0]}

	###########
	# COMPANY #
	###########

	# Add a company dict, containing the company information, to this device
	if len(company_dict) > 0:
		company_id = company_dict[company]['cw_id']
		company_identifier = company_dict[company]['cw_identifier']
	else: #this might not work if company "Unknown" doesn't exist in CW
		company_id = 0
		company_identifier = 0
		company = "Unknown"
	device_array[device_name]['company'] = {'id': company_id, 'name': company, 'identifier': company_identifier}

	if debug: print("=" * 80);print(item);pprint(device_array[device_name])
if debug: pprint(device_array)
else: print(device_array)

#############################
# SEND ITEMS TO CONNECTWISE #
#############################

for key, value in device_array.items():
	#find out what information CW has on this item
	get_body = API.get_cw_config_by_name(_name = key, **cw_creds)['body'].decode()
	#if this item doesn't exist in CW, post it there.
	if(get_body == '[]'):
		answer = API.post_cw_configuration(_config_dict = value, **cw_creds)
		if(answer['code'] == 200 or answer['code'] == 201): print(f'Record for {key} successfully created')
		else:
			print(f'Unable to create record for {key} with response code {answer["code"]}. Retrying...')
			second_attempt = API.post_cw_configuration(_config_dict = value, **cw_creds)
			print(f'Second attempt has produced response code {second_attempt["code"]}\nResponse Body\n{"=" * 80}\n{second_attempt["body"]}')
	#else, the item already exists, patch it with new information
	else:
		get_id = json.loads(get_body)[0]['id']
		patch_dict = API.patch_cw_configuration(_config_dict = value, _config_id = get_id, **cw_creds)
		if(patch_dict['code'] == 200 or answer['code'] == 201): print(f'Record for {key} successfully updated')
		else:
			print(f'Unable to update record for {key} with response code {answer["code"]}. Retrying...')
			second_attempt = API.patch_cw_configuration(_config_dict = value, _config_id = get_id, **cw_creds)
			print(f'Second attempt has produced response code {second_attempt["code"]}\nResponse Body\n{"=" * 80}\n{second_attempt["body"]}')
