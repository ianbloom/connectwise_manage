#! /usr/bin/python
import cw_api as CWAPI
import lm_api as LMAPI
import json, argparse
from pprint import pprint, pformat
from datetime import datetime
query_size = 1000 #number of items to pull from the LM API, helps with pagination
parser=argparse.ArgumentParser()
parser.add_argument('-file', help='Path to file containing API credentials', default='keyfile.txt')
args = parser.parse_args()
with open(args.file) as file: config = json.loads(file.read())
lm_creds = {"_lm_id": config['lm_id'], "_lm_key": config['lm_key'], "_lm_account": config['lm_company']}
cw_creds = {"_cw_api_id": config['cw_id'], "_cw_api_key": config['cw_key'], "_cw_company": config['cw_company'], "_cw_site": config['cw_site'], "_cw_agentId": config['cw_agentId']}
cw_device_response = CWAPI.get_cw_config_list(**cw_creds)
if cw_device_response['code'] in (200, 201): cw_devices = cw_device_response['items'].decode()
else: cw_devices = {"Octoprint": 4,"pitunes2": 7}
cw_company_response = CWAPI.get_cw_company_list(**cw_creds)
if cw_company_response['code'] in (200, 201): cw_companies = cw_company_response['items']
else: cw_companies = {"Acme": {"id":1, "identifier": 0xFEEDFACE}, "NetQoS": {"id": 2, "identifier": 0xDEFACED}}
cw_type_response = CWAPI.get_cw_type_list(**cw_creds)
if cw_type_response['code'] in (200, 201): cw_types = cw_type_response['items']
else: cw_types = {"Hyper-V": 1,"Server": 2,"Misc": 3,"Network": 4}
queryParams = {"fields": "id,name,displayName,hostGroupIds,customProperties,systemProperties,autoProperties,inheritedProperties"}
raw_response = LMAPI.LM_GET(_resource_path = '/device/devices', _query_params = queryParams, **lm_creds)
if raw_response['code'] in (200, 201):
	devices = raw_response['items']
	device_array = {}
	for item in devices:
		device_name = item['displayName']
		device_array[device_name] = {}
		device_array[device_name]['name'] = device_name
		all_properties = {}
		for dict in item['systemProperties']: all_properties[dict['name']] = dict['value'] #could probably use list comprehension here
		for dict in item['systemProperties']: all_properties[dict['name']] = dict['value']
		for dict in item['autoProperties']: all_properties[dict['name']] = dict['value']
		for dict in item['customProperties']: all_properties[dict['name']] = dict['value']
		for dict in item['inheritedProperties']: all_properties[dict['name']] = dict['value']
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
		company = all_properties['cw_company.name'] if 'cw_company.name' in all_properties.keys() else 'Unknown_Company'
		if company in cw_companies.keys():
			company_id = cw_companies[company]['id']
			company_identifier = cw_companies[company]['identifier']
		else:
			company_id = 0
			company_identifier = 0
		device_array[device_name]['company'] = {'id': company_id, 'name': company, 'identifier': company_identifier}
		type = all_properties['cw_type'] if 'cw_type' in all_properties.keys() else "Unknown_Type"
		if type in cw_types.keys(): type_id = cw_types[type]
		else: type_id = 0
		device_array[device_name]['type'] = {'id': type_id, 'name': type}
for key, value in device_array.items():
	if value['company']['name'] not in cw_companies: continue
	if value['type']['name'] not in cw_types: continue
	if(key in cw_devices.keys()):
		get_id = cw_devices[key]
		patch_response = CWAPI.patch_cw_configuration(_config_dict = value, _config_id = get_id, **cw_creds)
		if(patch_response['code'] == 200 or patch_response['code'] == 201): print(f'Done.')
	else:
		post_response = CWAPI.post_cw_configuration(_config_dict = value, **cw_creds)
		if(post_response['code'] == 200 or post_response['code'] == 201): print(f'Done.')
