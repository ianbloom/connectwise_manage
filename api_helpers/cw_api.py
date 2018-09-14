#! /usr/bin/python

from api_func import *
import pandas
import json
import sys
from io import StringIO
import argparse
from pprint import *
import base64
import requests

###########
# HELPERS #
###########

def header_build(_company, _api_id, _api_key):
	# Initialize header_dict and populate with header values
	header_dict = {}
	header_dict['Content-Type'] = 'application/json'

	# Build and encode API token for header
	token = f'{_company}+{_api_id}:{_api_key}'
	# For whatever reason, the string must first be encoded as a bytes-type object, then 64 encoded, then decode
	encoded_token = (base64.b64encode(token.encode())).decode()
	header_dict['Authorization'] = f'Basic {encoded_token}'

	return header_dict

###########
# GETTERS #
###########

def get_cw_config_list(_api_id, _api_key, _company, _connectwise_site):
	# Build request URL
	url = f'https://{_connectwise_site}/v4_6_release/apis/3.0/company/configurations'

	# Build header dictionary
	header_dict = header_build(_company, _api_id, _api_key)

	# Data is empty for this GET
	data = ''

	response = requests.get(url, data=data, headers=header_dict)

	return_dict = {'code':response.status_code,
				   'body':response.content}

	return return_dict

def get_cw_company_list(_api_id, _api_key, _company, _connectwise_site):
	# Build request URL
	url = f'https://{_connectwise_site}/v4_6_release/apis/3.0/company/companies'

	# Build header dictionary
	header_dict = header_build(_company, _api_id, _api_key)

	# Data is empty for this GET
	data = ''

	response = requests.get(url, data=data, headers=header_dict)

	return_dict = {'code':response.status_code,
				   'body':response.content}

	return return_dict

def get_cw_type_list(_api_id, _api_key, _company, _connectwise_site):
	# Build request URL
	url = f'https://{_connectwise_site}/v4_6_release/apis/3.0/company/companies/types'

	# Build header dictionary
	header_dict = header_build(_company, _api_id, _api_key)

	# Data is empty for this GET
	data = ''

	response = requests.get(url, data=data, headers=header_dict)

	return_dict = {'code':response.status_code,
				   'body':response.content}

	return return_dict

###########
# POSTERS #
###########

