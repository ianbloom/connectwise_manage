#! /usr/bin/python

# from api_func import *
import json
import base64
import requests

###########
# HELPERS #
###########

def header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId):
	# Initialize header_dict and populate with header values
	header_dict = {}
	header_dict['Content-Type'] = 'application/json'
	header_dict['clientID'] = _cw_agentId #not sure if this header name is correct

	# Build and encode API token for header
	token = f'{_cw_company}+{_cw_api_id}:{_cw_api_key}'
	# For whatever reason, the string must first be encoded as a bytes-type object, then 64 encoded, then decode
	encoded_token = (base64.b64encode(token.encode())).decode()
	header_dict['Authorization'] = f'Basic {encoded_token}'

	return header_dict

###########
# GETTERS #
###########

def get_cw_config_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations'
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)
	data = ''
	response = requests.get(url, data=data, headers=header_dict)
	return {'code':response.status_code, 'body':response.content}

def get_cw_company_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/companies'
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)
	data = ''
	response = requests.get(url, data=data, headers=header_dict)
	return {'code':response.status_code, 'body':response.content}

def get_cw_type_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations/types'
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)
	data = ''
	response = requests.get(url, data=data, headers=header_dict)
	return {'code':response.status_code, 'body':response.content}

###########
# POSTERS #
###########

def post_cw_configuration(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId, _config_dict):
	# Build request URL
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations'

	# Build header dictionary
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)

	# Data is a json string
	data = json.dumps(_config_dict)

	response = requests.post(url, data=data, headers=header_dict)

	return_dict = {'code':response.status_code,
				   'body':response.content}

	return return_dict

############
# PATCHERS #
############

def patch_cw_configuration(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId, _config_dict, _config_id):
	# Build request URL
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations/{_config_id}'

	# Build header dictionary
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)

	patch_array = []

	for key, value in _config_dict.items():
		patch_dict = {'op':'replace',
					  'path':key,
					  'value':value}
		patch_array.append(patch_dict)

	data = json.dumps(patch_array)

	response = requests.patch(url, data=data, headers=header_dict)

	return_dict = {'code':response.status_code,
				   'body':response.content}

	return return_dict
