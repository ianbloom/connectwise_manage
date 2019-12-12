#moved these to the main script for simplification. this module shouldn't be needed.
import api_helpers.lm_api as LMAPI
import json

def get_lm_device_types(_lm_id, _lm_key, _lm_account, _group_id):
	# Takes LM API keys and an LM group ID as input, outputs an array of LM 'Devices by Type'
	resource_path = f'/device/groups/{_group_id}'
	query_params  = ''
	data          = ''

	return_dict = LMAPI.LM_GET(_lm_id, _lm_key, _lm_account, resource_path, query_params, data)
	json_dict = json.loads(return_dict['body'])['data']

	subgroups = json_dict['subGroups']

	return_dict = {}

	for group in subgroups:
		subgroup_name = group['name']
		subgroup_id   = group['id']

		sub_dict = {}
		return_dict[f'{subgroup_name}'] = sub_dict

		return_dict[f'{subgroup_name}']['lm_id'] = subgroup_id

	return return_dict

def get_lm_companies(_lm_id, _lm_key, _lm_account):
	resource_path = '/device/devices'
	data          = ''
	last_item_found = False
	devices = []
	while not last_item_found:
		query_params  = f'?size=1000&offset={len(devices)}'
		current_call_devices = json.loads(LMAPI.LM_GET(_lm_id, _lm_key, _lm_account, resource_path, query_params, data)['body'])['data']['items']
		if len(current_call_devices) < 1000: last_item_found = True
		devices += current_call_devices
	# Initialize company_dict
	company_dict = {}
	for item in devices:
		found = False
		custom_props    = item['customProperties']
		inherited_props = item['inheritedProperties']

		company = ''
		for prop in inherited_props:
			if(prop['name'] == 'company'):
				company = prop['value']
				found = True

		for prop in custom_props:
			if(prop['name'] == 'company'):
				company = prop['value']
				found = True

		# If we don't have a defined company then don't bother trying to add to dictionary
		if(found == True):
			if(company not in company_dict.keys()):
				company_dict[f'{company}'] = {}
		# Account for devices with no company assigned
		company_dict['Unknown'] = {}

	return company_dict
