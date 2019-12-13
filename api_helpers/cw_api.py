#! /usr/bin/python

# from api_func import *
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
#all of these functions need to be modified so that the body returned is a python list of objects, ready to use without further decode/json.loads needed.
def get_cw_config_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations'
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)
	data = ''
	response = requests.get(url, data=data, headers=header_dict)
	return {'code':response.status_code, 'items':response.content}

def get_cw_company_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	# Needs to return a list of company IDs from CW
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/companies'
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)
	data = ''
	response = requests.get(url, data=data, headers=header_dict)
	return {'code':response.status_code, 'items':response.content}

def get_cw_type_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
	# Needs to return a list of company IDs from CW
	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations/types'
	header_dict = header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId)
	data = ''
	response = requests.get(url, data=data, headers=header_dict)
	return {'code':response.status_code, 'items':response.content}

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
