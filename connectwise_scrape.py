#! /usr/bin/python3
################################################################################
# © 2007-2019 - LogicMonitor, Inc. All rights reserved.                        #
################################################################################
import json, argparse, re, base64, requests, hashlib, time, hmac
from pprint import pprint, pformat
from datetime import datetime

###########################################################################
#                          CW API CALL FUNCTIONS                          #
###########################################################################
def header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId, addnlheaderitems = {}):
	header_dict = {}
	header_dict['Content-Type'] = 'application/json'
	header_dict['clientId'] = _cw_agentId
	token = f'{_cw_company}+{_cw_api_id}:{_cw_api_key}'
	encoded_token = (base64.b64encode(token.encode())).decode()
	header_dict['Authorization'] = f'Basic {encoded_token}'
	header_dict.update(addnlheaderitems)
	return header_dict

###########
# GETTERS #
###########
def get_cw_config_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	query_size = 1000
	last_found = False
	devices = {}
	page = 1
	while not last_found:
		url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations?pagesize={query_size}&page={page}'
		response = requests.get(url, data="", headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
		this_call_devices = {}
		if response.status_code in (200, 201):
			for device in json.loads(response.content):
				this_call_devices[device['name']] = [device['id'], device['type']]
			links = {}
			if len(response.headers['Link']) > 0:
				for link in response.headers['Link'].split(","):
					links[link.split(";")[1]] = link.split(";")[0]
			last_found = ' rel="last"' not in links.keys()
			devices.update(this_call_devices)
			page += 1
		else:
			devices = response
	return {'code':response.status_code, 'items':devices}

def get_cw_company_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	query_size = 1000
	last_found = False
	companies = {}
	page = 1
	while not last_found:
		url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/companies?pagesize={query_size}&page={page}'
		response = requests.get(url, data="", headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
		this_call_companies = {}
		if response.status_code in (200, 201):
			for company in json.loads(response.content):
				this_call_companies[str(company['id'])] = {'id': company['id'],'name': company['name'],'identifier': company['identifier']}
			links = {}
			if len(response.headers['Link']) > 0:
				for link in response.headers['Link'].split(","):
					links[link.split(";")[1]] = link.split(";")[0]
			last_found = ' rel="last"' not in links.keys()
			companies.update(this_call_companies)
			page += 1
		else:
			companies = response.content
	return {'code':response.status_code, 'items':companies}

def get_cw_type_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	query_size = 1000
	last_found = False
	types = {}
	page = 1
	while not last_found:
		url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations/types?pagesize={query_size}&page={page}'
		response = requests.get(url, data="", headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
		this_call_types = {}
		if response.status_code in (200, 201):
			for type in json.loads(response.content):
				types[type['name']] = type['id']
			links = {}
			if len(response.headers['Link']) > 0:
				for link in response.headers['Link'].split(","):
					links[link.split(";")[1]] = link.split(";")[0]
			last_found = ' rel="last"' not in links.keys()
			types.update(this_call_types)
			page += 1
		else:
			types = response.content
	return {'code':response.status_code, 'items':types}

def get_cw_manufacturer_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	query_size = 1000
	last_found = False
	items = {}
	page = 1
	while not last_found:
		url = f'https://{_cw_site}/v4_6_release/apis/3.0/procurement/manufacturers?pagesize={query_size}&page={page}'
		response = requests.get(url, data="", headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
		this_call_items = {}
		if response.status_code in (200, 201):
			for item in json.loads(response.content):
				this_call_items[str(item['name'])] = {'id': item['id'],'name': item['name'],'inactiveFlag': item['inactiveFlag']}
			links = {}
			if len(response.headers['Link']) > 0:
				for link in response.headers['Link'].split(","):
					links[link.split(";")[1]] = link.split(";")[0]
			last_found = ' rel="last"' not in links.keys()
			items.update(this_call_items)
			page += 1
		else:
			items = response.content
	return {'code':response.status_code, 'items':items}

###########
# POSTERS #
###########
def post_cw_configuration(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId, _config_dict):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations'
	data = json.dumps(_config_dict)
	response = requests.post(url, data=data, headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
	return {'code':response.status_code, 'body':json.loads(response.content.decode())}

############
# PATCHERS #
############
def patch_cw_configuration(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId, _config_dict, _config_id):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations/{_config_id}'
	patch_array = []
	for key, value in _config_dict.items():
		patch_dict = {'op':'replace',
					  'path':key,
					  'value':value}
		patch_array.append(patch_dict)
	data = json.dumps(patch_array)
	response = requests.patch(url, data=data, headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
	return {'code':response.status_code, 'body':response.content}

##############################################################################
#                         END CW API CALL FUNCTIONS                          #
##############################################################################

###########################################################################
#                          LM API CALL FUNCTIONS                          #
###########################################################################
def LM_GET(_lm_id, _lm_key, _lm_account, _resource_path, _query_params = {}, _data = '', _query_size = 1000):
	items = []
	last_item_found = False
	status_code = 0
	_query_params['size'] = _query_size
	err_out = ""
	while not last_item_found:
		_query_params['offset'] = len(items)
		_query_params_string = "?" + "&".join([f"{k}={v}" for k,v in _query_params.items()])
		url = 'https://'+ _lm_account +'.logicmonitor.com/santaba/rest' + _resource_path + _query_params_string
		epoch = str(int(time.time() * 1000))
		requestVars = 'GET' + epoch + _data + _resource_path
		authCode = hmac.new(_lm_key.encode(),msg=requestVars.encode(),digestmod=hashlib.sha256).hexdigest()
		signature = base64.b64encode(authCode.encode())
		auth = 'LMv1 ' + _lm_id + ':' + signature.decode() + ':' + epoch
		headers = {'Content-Type':'multipart/form-data','Authorization':auth,}
		response = requests.get(url, data=_data, headers=headers)
		status_code = response.status_code
		current_call_result = json.loads(response.content)
		data = current_call_result['data']
		errmsg = current_call_result['errmsg']
		status = current_call_result['status']
		fetched_count = len(data['items'])
		fetched_items = data['items']
		items += fetched_items
		last_item_found = fetched_count < _query_size
		err_out += f"Call to {url} results:\n\tHTTP Response code: {status_code}\n\tError Message: {errmsg}\n\tStatus code: {status}\n\tItems fetched: {fetched_count}\n\tTotal items fetched: {len(items)}\n\tLast item found: {last_item_found}\n"
	return {'code':status_code, 'items':items, 'err_out': err_out}

###############################################################################
#                          END LM API CALL FUNCTIONS                          #
###############################################################################

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
# script parameters for ds
# --info
# --cw_agentid ##lm2cw.cw_agentid.pass##
# --cw_company ##lm2cw.cw_company##
# --cw_private ##lm2cw.cw_private.pass##
# --cw_public ##lm2cw.cw_public##
# --cw_site ##lm2cw.cw_site##
# --lm_company ##lm2cw.lm_company##
# --lm_id ##lm2cw.lm_id##
# --lm_key ##lm2cw.lm_key.pass##

for arg in ["cw_agentid", "cw_company", "cw_private", "cw_public", "cw_site", "lm_company", "lm_id", "lm_key"]:
	parser.add_argument('--'+arg)
parser.add_argument('--debug', help='Turns on very verbose output.', action='store_true')
parser.add_argument('--info', help='Turns on information messages (these may or may not indicate a problem).', action='store_true')
args = parser.parse_args()
debug = args.debug
info = args.info

#######################
# CREATE API KEYRINGS #
#######################
lm_creds = {"_lm_id": args.lm_id, "_lm_key": args.lm_key, "_lm_account": args.lm_company}
cw_creds = {"_cw_api_id": args.cw_public, "_cw_api_key": args.cw_private, "_cw_company": args.cw_company, "_cw_site": args.cw_site, "_cw_agentId": args.cw_agentid}

log_msg("START SCRIPT EXECUTION")
###############################
# FETCH CURRENT ITEMS FROM CW #
###############################
log_msg(f"Fetching current manufacturer list from CW...", end="")
cw_manufacturer_response = get_cw_manufacturer_list(**cw_creds)
if cw_manufacturer_response['code'] in (200, 201):
	cw_manufacturers = cw_manufacturer_response['items']
	if info: print(f"Done fetching {len(cw_manufacturers)} manufacturers.")
else:
	if info: print("Failed.")
	log_msg(f"Problem obtaining current manufacturers from CW Manage: {cw_manufacturer_response['code']}: {cw_manufacturer_response['items']}", "ERROR")
	cw_manufacturers = {}
log_msg(f"Fetched manufacturer list from CW: {cw_manufacturers.keys()}", "DEBUG")

log_msg(f"Fetching current device list from CW...", end="")
cw_device_response = get_cw_config_list(**cw_creds)
if cw_device_response['code'] in (200, 201):
	cw_devices = cw_device_response['items']
	if info: print(f"Done fetching {len(cw_devices)} configurations.")
else:
	if info: print("Failed.")
	log_msg(f"Problem obtaining current CIs from CW Manage: {cw_device_response['code']}: {cw_device_response['items']}", "ERROR")
	cw_devices = {}
log_msg(f"Fetched CI list from CW: {cw_devices.keys()}", "DEBUG")

log_msg(f"Fetching current company list from CW...", end="")
cw_company_response = get_cw_company_list(**cw_creds)
if cw_company_response['code'] in (200, 201):
	cw_companies = cw_company_response['items']
	if info: print(f"Done fetching {len(cw_companies.keys())} companies.")
else:
	if info: print("Failed.")
	error_message = json.loads(cw_company_response['items'].decode())
	log_msg(f"Problem obtaining current company list from CW Manage: {cw_company_response['code']} {error_message['code']}: {error_message['message']}", "ERROR")
	cw_companies = {}
log_msg(f"Fetched company list from CW: {cw_companies}", "DEBUG")

log_msg(f"Fetching current type list from CW...", end="")
cw_type_response = get_cw_type_list(**cw_creds)
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
log_msg(f"Fetching current device list from LM...", end="")
raw_response = LM_GET(_resource_path = '/device/devices', _query_params = queryParams, **lm_creds)
if raw_response['code'] in (200, 201):
	devices = raw_response['items']
	device_array = {}
	if info: print(f"Done fetching {len(devices)} devices.")
	#log_msg(f"Fetched {len(devices)} devices from {lm_creds['_lm_account']}.logicmonitor.com.")
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
		if 'cw_company' in all_properties.keys():
			company_id = all_properties['cw_company']
			log_msg(f"Company tag found for {device_name}: {company_id}", "DEBUG")
			if company_id in cw_companies.keys():
				log_msg(f"{company_id} was found in cw_companies. Injecting metadata", "DEBUG")
				company_name = cw_companies[company_id]['name']
				company_identifier = cw_companies[company_id]['identifier']
			else:
				log_msg(f"{company_id} was not found in cw_companies. Injecting defaults.", "DEBUG")
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
		log_msg("This is a server, so we need to answer some extra questions.", "DEBUG")
		if type == "Server":
			device_array[device_name]["questions"] = [
				{"questionId": 23, "answer": "File & Print Server"},
				{"questionId": 32, "answer": "Windows 2003 Standard Server"}
			]

		log_msg(f"Done extracting properties", "DEBUG")
		log_msg(f"Raw device details: {item}", "DEBUG")
		log_msg(f"Extracted properties: {device_array[device_name]}", "DEBUG")
	log_msg(f"Data ready to be sent to CW.")
	log_msg(f"All items' extracted properties:", "DEBUG")
	for k,v in device_array.items():
		log_msg(f"{k}: {v}", "DEBUG")
else:
	if info: print("Failed.")
	log_msg(f"Problem obtaining current device list from LM: {raw_response['code']}\n\t{raw_response['err_out']}", "ERROR")
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
# CW API doesn't support bulk post nor patch. Must do one call for every device :-(
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
			patch_response = patch_cw_configuration(_config_dict = value, _config_id = get_id, **cw_creds)
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
		post_response = post_cw_configuration(_config_dict = value, **cw_creds)
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

print(f"""new_devices: {len(new_devices)}
new_failed: {len(new_failed)}
updated_devices: {len(updated_devices)}
update_failed: {len(update_failed)}
bad_company_devices: {len(bad_company_devices)}
bad_type_devices: {len(bad_type_devices)}""")

log_msg("END SCRIPT EXECUTION")
