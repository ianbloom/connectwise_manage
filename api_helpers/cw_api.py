#! /usr/bin/python
import json
import base64
import requests

###########
# HELPERS #
###########
def header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId):
	header_dict = {}
	header_dict['Content-Type'] = 'application/json'
	header_dict['clientId'] = _cw_agentId
	token = f'{_cw_company}+{_cw_api_id}:{_cw_api_key}'
	encoded_token = (base64.b64encode(token.encode())).decode()
	header_dict['Authorization'] = f'Basic {encoded_token}'
	return header_dict

###########
# GETTERS #
###########
def get_cw_config_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations'
	response = requests.get(url, data="", headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
	devices = {}
	if response.status_code in (200, 201):
		for device in json.loads(response.content): devices[device['name']] = device['id']
	else:
		devices = response.content
	return {'code':response.status_code, 'items':devices}

def get_cw_company_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/companies'
	response = requests.get(url, data="", headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
	companies = {}
	if response.status_code in (200, 201):
		for company in json.loads(response.content):
			companies[company['name']] = {
				'id': company['id'],
				'identifier': company['identifier']
			}
	else:
		companies = response.content
	return {'code':response.status_code, 'items':companies}

def get_cw_type_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations/types'
	response = requests.get(url, data="", headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
	types = {}
	if response.status_code in (200, 201):
		for type in json.loads(response.content): types[type['name']] = type['id']
	else:
		types = response.content
	return {'code':response.status_code, 'items':types}

###########
# POSTERS #
###########
def post_cw_configuration(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId, _config_dict):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations'
	data = json.dumps(_config_dict)
	#something's incomplete in the _config_dict, not sure what.
	print(data)
	response = requests.post(url, data=data, headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
	return {'code':response.status_code, 'body':response.content}

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
