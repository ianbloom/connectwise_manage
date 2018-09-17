from api_helpers.lm_api import *
import json
from pprint import pprint

# Takes LM API keys and an LM group ID as input, outputs an array of LM 'Devices by Type'
def get_lm_device_types(_lm_id, _lm_key, _lm_account, _group_id):
	resource_path = f'/device/groups/{_group_id}'
	query_params  = ''
	data          = ''

	return_dict = LM_GET(_lm_id, _lm_key, _lm_account, resource_path, query_params, data)
	json_dict = json.loads(return_dict['body'])['data']

	subgroups = json_dict['subGroups']

	return_dict = {}

	for group in subgroups:
		subgroup_name = group['name']
		subgroup_id = group['id']

		sub_dict = {}
		return_dict[f'{subgroup_name}'] = sub_dict

		return_dict[f'{subgroup_name}']['lm_id'] = subgroup_id

	return return_dict

def get_lm_companies(_lm_id, _lm_key, _lm_account):
	resource_path = '/device/devices'
	query_params  = '?size=1000'
	data          = ''

	return_dict = LM_GET(_lm_id, _lm_key, _lm_account, resource_path, query_params, data)
	json_dict = json.loads(return_dict['body'])['data']['items']
	# Initialize company_dict
	company_dict = {}
	for item in json_dict:
		found = False
		custom_props = item['customProperties']
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

	return company_dict