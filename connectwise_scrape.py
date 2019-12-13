#! /usr/bin/python

import api_helpers.cw_api as CWAPI
import api_helpers.lm_api as LMAPI

import json, argparse
from pprint import pprint, pformat
from datetime import datetime

query_size = 1000 #number of items to pull from the LM API, helps with pagination

##############################
# STANDARDIZED OUTPUT LOGGER #
##############################
def log_msg(msg, severity = "INFO", end = "\n", crb = False):
	if (severity == "DEBUG" and debug) or (severity == "INFO" and info) or severity not in ("DEBUG", "INFO"):
		print(f"{datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')} {severity}: {msg}", end=end)

#########################
# CLI ARGUMENT HANDLING #
#########################
parser=argparse.ArgumentParser()
parser.add_argument('-file', help='Path to file containing API credentials', default='keyfile.txt')
parser.add_argument('--debug', help='Turns on very verbose output.', action='store_true')
parser.add_argument('--info', help='Turns on information messages (these may or may not indicate a problem).', action='store_true')
args = parser.parse_args()
debug = args.debug
info = args.info

###################
# PARSE API CREDS #
###################
with open(args.file) as file:
	config = json.loads(file.read())
lm_creds = {"_lm_id": config['lm_id'], "_lm_key": config['lm_key'], "_lm_account": config['lm_company']}
cw_creds = {"_cw_api_id": config['cw_id'], "_cw_api_key": config['cw_key'], "_cw_company": config['cw_company'], "_cw_site": config['cw_site'], "_cw_agentId": config['cw_agentId']}

###############################
# FETCH CURRENT ITEMS FROM CW #
###############################
log_msg(f"Fetching current company list from CW...", end="")
cw_device_response = CWAPI.get_cw_config_list(**cw_creds)
if cw_device_response['code'] in (200, 201):
	cw_devices = cw_device_response['items'].decode()
	if info: print("Done.")
else:
	if info: print("Failed.")
	error_message = json.loads(cw_device_response['items'].decode())
	log_msg(f"Problem obtaining current CIs from CW Manage: {cw_device_response['code']} {error_message['code']}: {error_message['message']}", "ERROR")
	# cw_devices = {}
	# this dict is to inject some fake data for testing. The result of get_cw_config_list should look like this:
	cw_devices = {
		"Octoprint": 4,
		"pitunes2": 7
	}

log_msg(f"Fetching current company list from CW...", end="")
cw_company_response = CWAPI.get_cw_company_list(**cw_creds)
if cw_company_response['code'] in (200, 201):
	cw_companies = cw_company_response['items']
	if info: print("Done.")
else:
	if info: print("Failed.")
	error_message = json.loads(cw_company_response['items'].decode())
	log_msg(f"Problem obtaining current company list from CW Manage: {cw_company_response['code']} {error_message['code']}: {error_message['message']}", "ERROR")
	# cw_companies = {}
	# this dict is to inject some fake data for testing. The result of cw_company_response should look like this:
	cw_companies = {
		"Acme": {"id":1, "identifier": "FEEDFACE"},
		"NetQoS": {"id": 2, "identifier": "DEFACED"}
	}
log_msg(f"cw_companies = {cw_companies}")

log_msg(f"Fetching current type list from CW...", end="")
cw_type_response = CWAPI.get_cw_type_list(**cw_creds)
if cw_type_response['code'] in (200, 201):
	cw_types = cw_type_response['items']
	if info: print("Done.")
else:
	if info: print("Failed.")
	error_message = json.loads(cw_type_response['items'].decode())
	log_msg(f"Problem obtaining current type list from CW Manage: {cw_type_response['code']} {error_message['code']}: {error_message['message']}", "ERROR")
	# cw_types = {}
	# this dict is to inject some fake data for testing. The result of cw_type_response should look like this:
	cw_types = {
		"Hyper-V": 1,
		"Server": 2,
		"Misc": 3,
		"Network": 4
	}

###########################
# GET ALL DEVICES FROM LM #
###########################
queryParams = {"fields": "id,name,displayName,hostGroupIds,customProperties,systemProperties,autoProperties,inheritedProperties"}
raw_response = LMAPI.LM_GET(_resource_path = '/device/devices', _query_params = queryParams, **lm_creds)
if raw_response['code'] in (200, 201):
	devices = raw_response['items']
	device_array = {}
	log_msg(f"Fetched {len(devices)} devices from {lm_creds['_lm_account']}.logicmonitor.com.")
	for item in devices:
		device_name = item['displayName']
		log_msg(f"Gathering information for {device_name}...", end="")
		device_array[device_name] = {}
		device_array[device_name]['name'] = device_name
		log_msg(f"Processing data. (Extracting device properties from LM data to use in CW fields)", "DEBUG")
		all_properties = {}
		for dict in item['systemProperties']:
			all_properties[dict['name']] = dict['value'] #could probably use list comprehension here
		for dict in item['systemProperties']:
			all_properties[dict['name']] = dict['value']
		for dict in item['autoProperties']:
			all_properties[dict['name']] = dict['value']
		for dict in item['customProperties']:
			all_properties[dict['name']] = dict['value']
		for dict in item['inheritedProperties']:
			all_properties[dict['name']] = dict['value']
		log_msg(f"Now all the properties are in a single dictionary with the property name as the key.", "DEBUG")

		log_msg(f"ID: {item['id']} Name: {item['name']}", "DEBUG")
		log_msg(f"  displayName: {item['displayName']}", "DEBUG")
		log_msg(f"  hostGroupIds: {item['hostGroupIds']}", "DEBUG")
		for k,v in all_properties.items():
			log_msg(f"  {k}: {v}", "DEBUG")

		log_msg(f"Extracting properties...", "DEBUG")
		device_array[device_name]['ipAddress'] = all_properties['system.ips'].split(",")[0] if 'system.ips' in all_properties.keys() else ""
		device_array[device_name]['osType'] = all_properties['system.sysinfo'][:250] if 'system.sysinfo' in all_properties.keys() else ""
		device_array[device_name]['uptime'] = all_properties['system.uptime'] if 'system.uptime' in all_properties.keys() else ""
		device_array[device_name]['modelNumber'] = all_properties['system.model'][:50] if 'system.model' in all_properties.keys() else ""
		for k,v in all_properties.items():
			if 'serial' in k:
				device_array[device_name]['serialNumber'] = v
			if 'model' in k:
				device_array[device_name]['modelNumber'] = v[:50]
		device_array[device_name]['location'] = all_properties['location'] if 'location' in all_properties.keys() else ""

		log_msg(f"Extracting company information, building company dictionary for this one device.", "DEBUG")
		company = all_properties['cw_company.name'] if 'cw_company.name' in all_properties.keys() else 'Unknown_Company'
		log_msg(f"Company tag found for {device_name}: {company}", "DEBUG")
		if company in cw_companies.keys():
			log_msg(f"{company} was found in cw_companies. Injecting ids", "DEBUG")
			company_id = cw_companies[company]['id']
			company_identifier = cw_companies[company]['identifier']
		else:
			log_msg(f"{company} was not found in cw_companies. Injecting defaults.", "DEBUG")
			company_id = 0
			company_identifier = 0
		device_array[device_name]['company'] = {'id': company_id, 'name': company, 'identifier': company_identifier}

		log_msg(f"Extracting type information, building type dictionary for this one device", "DEBUG")
		type = all_properties['cw_type'] if 'cw_type' in all_properties.keys() else "Unknown_Type"
		log_msg(f"Type tag found for {device_name}: {type}", "DEBUG")
		if type in cw_types.keys():
			log_msg(f"{type} was found in cw_types. Injecting ids", "DEBUG")
			type_id = cw_types[type]
		else:
			log_msg(f"{type} was not found in cw_types. Injecting defaults.", "DEBUG")
			type_id = 0
		device_array[device_name]['type'] = {'id': type_id, 'name': type}

		log_msg(f"Done extracting properties", "DEBUG")
		log_msg(f"Raw device details: {item}", "DEBUG")
		log_msg(f"Extracted properties: {device_array[device_name]}", "DEBUG")
		if info: print(f"Done")
	log_msg(f"Data ready to be sent to CW.")
	log_msg(f"All items' extracted properties:", "DEBUG")
	for k,v in device_array.items():
		log_msg(f"{k}: {v}", "DEBUG")
else:
	log_msg(f"Unable to fetch devices from LM: {raw_response['code']}\n\t{raw_response['err_out']}", "ERROR")

#############################
# SEND ITEMS TO CONNECTWISE #
#############################
for key, value in device_array.items():
	if value['company']['name'] not in cw_companies:
		log_msg(f"\"{key}\" LM company tag ({value['company']['name']}) does not exist in CW. {key} not synchronized to CW.", "ERROR")
		continue
	if value['type']['name'] not in cw_types:
		log_msg(f"\"{key}\" LM type tag ({value['type']['name']}) does not exist in CW. {key} not synchronized to CW.", "ERROR")
		continue
	log_msg(f"\"{key}\" passed validation checks.")

	if(key in cw_devices.keys()):
		log_msg(f"\"{key}\" exists in CW Manage, updating fields...", end="")
		get_id = cw_devices[key]
		patch_response = CWAPI.patch_cw_configuration(_config_dict = value, _config_id = get_id, **cw_creds)
		if(patch_response['code'] == 200 or patch_response['code'] == 201):
			if info: print(f'Done.')
		else:
			if info: print(f'Failed.')
			log_msg(f'Unable to update record for \"{key}\" with response code {patch_response["code"]}: {json.loads(patch_response["body"].decode())["code"]}: {json.loads(patch_response["body"].decode())["message"]}', "ERROR")
	else:
		log_msg(f"\"{key}\" does not exist in CW Manage, creating CI...", end="")
		post_response = CWAPI.post_cw_configuration(_config_dict = value, **cw_creds)
		if(post_response['code'] == 200 or post_response['code'] == 201):
			if info: print(f'Done.')
		else:
			if info: print(f'Failed.')
			log_msg(f'Unable to create record for \"{key}\" with response code {post_response["code"]}: {json.loads(post_response["body"].decode())["code"]}: {json.loads(post_response["body"].decode())["message"]}', "ERROR")
