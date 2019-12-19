#! /usr/bin/python3

import api_helpers.cw_api as CWAPI
import api_helpers.lm_api as LMAPI

import json, argparse, re
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

log_msg("START SCRIPT EXECUTION")
###############################
# FETCH CURRENT ITEMS FROM CW #
###############################
log_msg(f"Fetching current manufacturer list from CW...", end="")
cw_manufacturer_response = CWAPI.get_cw_manufacturer_list(**cw_creds)
if cw_manufacturer_response['code'] in (200, 201):
	cw_manufacturers = cw_manufacturer_response['items']
	if info: print(f"Done fetching {len(cw_manufacturers)} manufacturers.")
else:
	if info: print("Failed.")
	log_msg(f"Problem obtaining current manufacturers from CW Manage: {cw_manufacturer_response['code']}: {cw_manufacturer_response['items']}", "ERROR")
	cw_manufacturers = {}
log_msg(f"Fetched manufacturer list from CW: {cw_manufacturers.keys()}", "DEBUG")

log_msg(f"Fetching current device list from CW...", end="")
cw_device_response = CWAPI.get_cw_config_list(**cw_creds)
if cw_device_response['code'] in (200, 201):
	cw_devices = cw_device_response['items']
	if info: print(f"Done fetching {len(cw_devices)} configurations.")
else:
	if info: print("Failed.")
	log_msg(f"Problem obtaining current CIs from CW Manage: {cw_device_response['code']}: {cw_device_response['items']}", "ERROR")
	cw_devices = {}
log_msg(f"Fetched CI list from CW: {cw_devices.keys()}", "DEBUG")

log_msg(f"Fetching current company list from CW...", end="")
cw_company_response = CWAPI.get_cw_company_list(**cw_creds)
if cw_company_response['code'] in (200, 201):
	cw_companies = cw_company_response['items']
	if info: print(f"Done fetching {len(cw_companies.keys())} companies.")
else:
	if info: print("Failed.")
	error_message = json.loads(cw_company_response['items'].decode())
	log_msg(f"Problem obtaining current company list from CW Manage: {cw_company_response['code']} {error_message['code']}: {error_message['message']}", "ERROR")
	cw_companies = {}
log_msg(f"Fetched company list from CW: {cw_companies.keys()}", "DEBUG")

log_msg(f"Fetching current type list from CW...", end="")
cw_type_response = CWAPI.get_cw_type_list(**cw_creds)
if cw_type_response['code'] in (200, 201):
	cw_types = cw_type_response['items']
	if info: print(f"Done fetching {len(cw_types)} types.")
else:
	if info: print("Failed.")
	log_msg(f"Problem obtaining current type list from CW Manage: {cw_type_response['code']}: {cw_type_response['items']}", "ERROR")
	cw_types = {}
log_msg(f"Fetched type list from CW: {cw_types.keys()}", "DEBUG")

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
		log_msg(f"Processing data. (Extracting device properties from LM data to use in CW fields)", "DEBUG")
		all_properties = {}
		for dict in item['systemProperties']:
			all_properties[dict['name']] = dict['value'] #could probably use list comprehension here
		for dict in item['autoProperties']:
			all_properties[dict['name']] = dict['value']
		for dict in item['customProperties']:
			all_properties[dict['name']] = dict['value']
		for dict in item['inheritedProperties']:
			all_properties[dict['name']] = dict['value']
		log_msg(f"Now all the properties are in a single dictionary with the property name as the key.", "DEBUG")
		# log_msg(f"ID: {item['id']} Name: {item['name']}", "DEBUG")
		# log_msg(f"  displayName: {item['displayName']}", "DEBUG")
		# log_msg(f"  hostGroupIds: {item['hostGroupIds']}", "DEBUG")
		# for k,v in all_properties.items(): log_msg(f"  {k}: {v}", "DEBUG")

		device_name = item['displayName']
		log_msg(f"Gathering information for {device_name}...", "DEBUG")
		device_array[device_name] = {}

		#name
		device_array[device_name]['name'] = device_name

		#ipAddress
		if 'system.ips' in all_properties.keys():
			device_array[device_name]['ipAddress'] = all_properties['system.ips'].split(",")[0]

		#osType
		if 'system.sysinfo' in all_properties.keys():
			device_array[device_name]['osType'] = all_properties['system.sysinfo'][:250]

		#manufacturer
		if 'system.sysinfo' in all_properties.keys():
			lm_manufacturer = all_properties['system.sysinfo'].split(" ",1)[0]
			if lm_manufacturer in cw_manufacturers.keys():
				device_array[device_name]['manufacturer'] = {"id": cw_manufacturers[lm_manufacturer]['id'], "name": cw_manufacturers[lm_manufacturer]['name']}

		#mac Address
		if 'auto.network.mac_address' in all_properties.keys():
			device_array[device_name]['macAddress'] = all_properties['auto.network.mac_address']

		#model
		for mp in ['model','system.model','auto.endpoint.model','auto.entphysical.modelname','auto.cisco.chassis_model']:
			if mp in all_properties.keys():
				device_array[device_name]['modelNumber'] = all_properties[mp][:50]
				log_msg(f"Found model information in {mp} ({all_properties[mp]}). Overwriting any previously discovered model information.", "DEBUG")
		for k,v in all_properties.items():
			if re.search("auto\.netapp\..*\.model", k):
				log_msg(f"Found model information in {k} ({v}). Overwriting any previously discovered model information.", "DEBUG")
				device_array[device_name]['modelNumber'] = v[:50]

		#serial
		for k,v in all_properties.items():
			if 'serial' in k:
				device_array[device_name]['serialNumber'] = v

		#company
		log_msg(f"Extracting company information.", "DEBUG")
		if 'connectwise_training.companyid' in all_properties.keys():
			company_id = all_properties['connectwise_training.companyid']
			log_msg(f"Company tag found for {device_name}: {company_id}", "DEBUG")
			if company_id in cw_companies.keys():
				log_msg(f"{company_id} was found in cw_companies. Injecting metadata", "DEBUG")
				company_name = cw_companies[company_id]['name']
				company_identifier = cw_companies[company_id]['identifier']
			else:
				log_msg(f"{company} was not found in cw_companies. Injecting defaults.", "DEBUG")
				company_name = "Unknown_Company"
				company_identifier = 0
		else:
			company_name = 'Unknown_Company'
			company_id = 0
			company_identifier = 0
		device_array[device_name]['company'] = {'id': company_id, 'name': company_name, 'identifier': company_identifier}

		#type
		log_msg(f"Extracting type information.", "DEBUG")
		type = all_properties['cw_type'] if 'cw_type' in all_properties.keys() else "Unknown_Type"
		log_msg(f"Type tag found for {device_name}: {type}", "DEBUG")
		if type in cw_types.keys():
			log_msg(f"{type} was found in cw_types. Injecting ids", "DEBUG")
			type_id = cw_types[type]
		else:
			log_msg(f"{type} was not found in cw_types. Injecting defaults.", "DEBUG")
			type_id = 0
		device_array[device_name]['type'] = {'id': type_id, 'name': type}

		# example static answers to additional questions
		# log_msg("This is a server, so we need to answer some extra questions.", "DEBUG")
		# if type == "Server":
		# 	device_array[device_name]["questions"] = [
		# 		{"questionId": 23, "answer": "File & Print Server"},
		# 		{"questionId": 32, "answer": "Windows 2003 Standard Server"}
		# 	]

		log_msg(f"Done extracting properties", "DEBUG")
		log_msg(f"Raw device details: {item}", "DEBUG")
		log_msg(f"Extracted properties: {device_array[device_name]}", "DEBUG")
	log_msg(f"Data ready to be sent to CW.")
	log_msg(f"All items' extracted properties:", "DEBUG")
	for k,v in device_array.items():
		log_msg(f"{k}: {v}", "DEBUG")
else:
	log_msg(f"Unable to fetch devices from LM: {raw_response['code']}\n\t{raw_response['err_out']}", "ERROR")
# pprint(device_array);quit()
#############################
# SEND ITEMS TO CONNECTWISE #
#############################
bad_type_devices = {}
bad_company_devices = {}
new_devices = {}
new_failed = {}
updated_devices = {}
update_failed = {}

for key, value in device_array.items():
	if value['company']['id'] not in cw_companies.keys():
		log_msg(f"\"{key}\" LM company tag ({value['company']['name']}) does not exist in CW. \"{key}\" not synchronized to CW.", "ERROR")
		bad_company_devices[key] = value['company']['name']
		continue
	if value['type']['name'] not in cw_types:
		log_msg(f"\"{key}\" LM type tag ({value['type']['name']}) does not exist in CW. \"{key}\" not synchronized to CW.", "ERROR")
		bad_type_devices[key] = value['type']['name']
		continue
	log_msg(f"\"{key}\" passed validation checks. Ready to post/patch {value}", "DEBUG")
	log_msg(f"\"{key}\" passed validation checks.")
	if(key in cw_devices.keys()):
		log_msg(f"\"{key}\" exists in CW Manage, updating fields...", end="")
		type_from_cw = cw_devices[key][1]['name']
		type_from_lm = value['type']['name']
		if type_from_cw == type_from_lm:
			get_id = cw_devices[key][0]
			patch_response = CWAPI.patch_cw_configuration(_config_dict = value, _config_id = get_id, **cw_creds)
			if(patch_response['code'] == 200 or patch_response['code'] == 201):
				if info: print(f'Done.')
				updated_devices[key] = value
			else:
				if info: print(f'Failed.')
				log_msg(f'Unable to update record for \"{key}\" with response code {patch_response["code"]}: {patch_response["body"]}. Request payload {value}', "ERROR")
				update_failed[key] = value
		else:
			print(f'Failed.')
			log_msg(f"Unable to update record for \"{key}\" because the type from LM ({type_from_lm}) doesn't match the type already set in CW ({type_from_cw}).", "ERROR")
			update_failed[key] = value
	else:
		log_msg(f"\"{key}\" does not exist in CW Manage, creating CI...", end="")
		post_response = CWAPI.post_cw_configuration(_config_dict = value, **cw_creds)
		if(post_response['code'] == 200 or post_response['code'] == 201):
			if info: print(f'Done.')
			new_devices[key] = value
		else:
			if info: print(f'Failed.')
			log_msg(f'Unable to create record for \"{key}\" with response code {post_response["code"]}: {post_response["body"]}. Request payload {value}', "ERROR")
			new_failed[key] = value
#the following outputs could be formulated into ds collect outputs to track the results over time.
log_msg(f"{len(new_devices)} new devices added to CW.")
log_msg(f"New devices added: {new_devices}", "DEBUG")

log_msg(f"{len(new_failed)} new devices failed to add to CW.")
log_msg(f"New devices that failed to add: {new_failed}", "DEBUG")

log_msg(f"{len(updated_devices)} existing devices updated in CW.")
log_msg(f"Existing devices updated: {updated_devices}", "DEBUG")

log_msg(f"{len(update_failed)} existing devices failed to update in CW.")
log_msg(f"Existing devices that failed to update: {update_failed}", "DEBUG")

log_msg(f"{len(bad_company_devices)} devices were not synchronized to CW due to a company mismatch")
log_msg(f"Devices not synchronized due to bad company: {bad_company_devices.items()}", "DEBUG")
log_msg(f"Valid companies: {cw_companies.keys()}", "DEBUG")

log_msg(f"{len(bad_type_devices)} devices were not synchronized to CW due to a type mismatch")
log_msg(f"Devices not synchronized due to bad type: {bad_type_devices.items()}", "DEBUG")
log_msg(f"Valid companies: {cw_types.keys()}", "DEBUG")

log_msg("END SCRIPT EXECUTION")
