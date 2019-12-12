#! /usr/bin/python

import api_helpers.cw_api as CWAPI
import api_helpers.lm_api as LMAPI

import json, argparse
from pprint import pprint

debug = False
query_size = 5 #number of items to pull from the LM API, helps with pagination

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
lm_creds = {"_lm_id": config['lm_id'], "_lm_key": config['lm_key'], "_lm_account": config['lm_company']}
cw_creds = {"_cw_api_id": config['cw_id'], "_cw_api_key": config['cw_key'], "_cw_company": config['cw_company'], "_cw_site": config['cw_site'], "_cw_agentId": config['cw_agentId']}

###########################
# GET ALL DEVICES FROM LM #
###########################
resourcePath = '/device/devices'
queryParams = {"fields": "id,name,displayName,hostGroupIds,customProperties,systemProperties,autoProperties,inheritedProperties"}
raw_response = LMAPI.LM_GET(_resource_path = resourcePath, _query_params = queryParams, **lm_creds)
if raw_response['code'] == 200:
	devices = raw_response['items']
	device_array = {}
	print(f"Fetched {len(devices)} devices from {lm_creds['_lm_account']}.logicmonitor.com.")
	for item in devices:
		device_name = item['displayName']
		if debug: print(f"Gathering information for {device_name}")
		device_array[device_name] = {}
		device_array[device_name]['name'] = device_name
		#extract device properties from LM data to use in CW fields, could probably use list comprehension here
		if debug: print(f"\tProcessing data...")
		all_properties = {}
		for dict in item['systemProperties']:    all_properties[dict['name']] = dict['value']
		for dict in item['systemProperties']:    all_properties[dict['name']] = dict['value']
		for dict in item['autoProperties']:      all_properties[dict['name']] = dict['value']
		for dict in item['customProperties']:    all_properties[dict['name']] = dict['value']
		for dict in item['inheritedProperties']: all_properties[dict['name']] = dict['value']
		#now all the properties are in a single dictionary with the property name as the key.
		if debug: #use to see all properties
			print(f"""ID: {item['id']}\n  Name: {item['name']}\n  displayName: {item['displayName']}\n  hostGroupIds: {item['hostGroupIds']}""")
			for k,v in all_properties.items(): print(f"  {k}: {v}")
			print(f"\tExtracting properties...")
		device_array[device_name]['ipAddress'] = all_properties['system.ips'].split(",")[0] if 'system.ips' in all_properties.keys() else ""
		device_array[device_name]['osType'] = all_properties['system.sysinfo'][:250] if 'system.sysinfo' in all_properties.keys() else ""
		device_array[device_name]['uptime'] = all_properties['system.uptime'] if 'system.uptime' in all_properties.keys() else ""
		device_array[device_name]['modelNumber'] = all_properties['system.model'][:50] if 'system.model' in all_properties.keys() else ""
		for k,v in all_properties.items():
			if 'serial' in k: device_array[device_name]['serialNumber'] = v
			if 'model' in k: device_array[device_name]['modelNumber'] = v[:50]
		device_array[device_name]['location'] = all_properties['location'] if 'location' in all_properties.keys() else ""
		company = all_properties['cw_company.name'] if 'cw_company.name' in all_properties.keys() else 'Unknown_Company'
		company_id = all_properties['cw_company.id'] if 'cw_company.id' in all_properties.keys() else 0
		company_identifier = all_properties['cw_company.identifier'] if 'cw_company.identifier' in all_properties.keys() else 0
		device_array[device_name]['company'] = {'id': company_id, 'name': company, 'identifier': company_identifier}
		type = all_properties['cw_type.name'] if 'cw_type.name' in all_properties.keys() else "Unknown_Type"
		type_id = all_properties['cw_type.id'] if 'cw_type.id' in all_properties.keys() else 0
		device_array[device_name]['type'] = {'id': type_id, 'name': type}
		if debug:
			print("\tDone extracting properties")
			print("=" * 80)
			print(item)
			pprint(device_array[device_name])
		else:
			print(f"Done processing data for {device_name}")
	print("Data ready to be sent to CW.")
	if debug:
		for k,v in device_array.items(): print(f"\n{k}:\n\t{v}")
else: print(f"Unable to fetch devices from LM: {raw_response['code']}\n\t{raw_response['err_out']}")

#############################
# SEND ITEMS TO CONNECTWISE #
#############################
#get current device list from CW
cw_device_response = CWAPI.get_cw_config_list(**cw_creds)
if cw_device_response['code'] in (200, 201):
	cw_devices = cw_device_response['body'].decode()
else:
	print(f"Problem obtaining current CIs from CW Manage: {cw_device_response['code']} {cw_device_response['body']}")
	cw_devices = []

#get current company list from CW
cw_company_response = CWAPI.get_cw_company_list(**cw_creds)
if cw_company_response['code'] in (200, 201):
	cw_companies = cw_company_response['body'].decode()
else:
	print(f"Problem obtaining current company list from CW Manage: {cw_company_response['code']} {cw_company_response['body']}")
	cw_companies = []

#get current type list from CW
cw_type_response = CWAPI.get_cw_type_list(**cw_creds)
if cw_type_response['code'] in (200, 201):
	cw_types = cw_type_response['body'].decode()
else:
	print(f"Problem obtaining current type list from CW Manage: {cw_type_response['code']} {cw_type_response['body']}")
	cw_types = []

for key, value in device_array.items():
	#if this item doesn't exist in CW, post it there.
	if(key not in cw_devices):
		post_response = CWAPI.post_cw_configuration(_config_dict = value, **cw_creds)
		if(post_response['code'] == 200 or post_response['code'] == 201):
			print(f'Record for {key} successfully created')
		else:
			print(f'Unable to create record for {key} with response code {post_response["code"]}: {post_response["body"]}')
	#else, the item already exists, patch it with new information
	else:
		get_id = cw_devices[key]['id']
		patch_response = CWAPI.patch_cw_configuration(_config_dict = value, _config_id = get_id, **cw_creds)
		if(patch_response['code'] == 200 or patch_response['code'] == 201):
			print(f'Record for {key} successfully updated')
		else:
			print(f'Update record for {key} with response code {patch_response["code"]}: {patch_response["body"]}')
