import json
import base64
import requests
def header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId):
	header_dict = {}
	header_dict['Content-Type'] = 'application/json'
	header_dict['clientId'] = _cw_agentId
	token = f'{_cw_company}+{_cw_api_id}:{_cw_api_key}'
	encoded_token = (base64.b64encode(token.encode())).decode()
	header_dict['Authorization'] = f'Basic {encoded_token}'
	return header_dict
def get_cw_config_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations'
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)
	data = ''
	response = requests.get(url, data=data, headers=header_dict)
	return {'code':response.status_code, 'items':response.content}
def get_cw_company_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/companies'
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)
	data = ''
	response = requests.get(url, data=data, headers=header_dict)
	return {'code':response.status_code, 'items':response.content}
def get_cw_type_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations/types'
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)
	data = ''
	response = requests.get(url, data=data, headers=header_dict)
	return {'code':response.status_code, 'items':response.content}
def post_cw_configuration(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId, _config_dict):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations'
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)
	data = json.dumps(_config_dict)
	response = requests.post(url, data=data, headers=header_dict)
	return {'code':response.status_code, 'body':response.content}
def patch_cw_configuration(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId, _config_dict, _config_id):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations/{_config_id}'
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)
	patch_array = []
	for key, value in _config_dict.items():
		patch_dict = {'op':'replace', 'path':key, 'value':value}
		patch_array.append(patch_dict)
	data = json.dumps(patch_array)
	response = requests.patch(url, data=data, headers=header_dict)
	return {'code':response.status_code, 'body':response.content}
