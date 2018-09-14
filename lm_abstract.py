from api_helpers.lm_api import *
import json
from pprint import pprint

def get_lm_device_types(_lm_id, _lm_key, _lm_account, _group_id):
	resource_path = f'/device/groups/{_group_id}'
	query_params = ''
	data = ''

	return_dict = LM_GET(_lm_id, _lm_key, _lm_account, resource_path, query_params, data)
	# pprint(json.loads(return_dict['body']))
	json_dict = json.loads(return_dict['body'])['data']

	subgroups = json_dict['subGroups']

	return_array = []

	for group in subgroups:
		subgroup_name = group['fullPath'].split('/')[1]
		return_array.append(subgroup_name)

	return return_array