#! /usr/bin/python

from api_func.api_func import *
from api_helpers.cw_abstract import *
import pandas
import json
import sys
from io import StringIO
import argparse
from pprint import *

# AccessId  = 'tZ3u4e8k8y2M3ttevFj6'
# AccessKey = 'Xe5~e4P%9kErB(98Ri89h5]CJ4j~w}Dy)wGJ6k%4'
# Company   = 'bcservice'

# cw_api_id  = 'SfefZokssi9JFFuK'
# cw_api_key = 'EOjLXH5wVI9krM32'
# cw_company = 'logicmonitor_f'
# cw_site    = 'staging.connectwisedev.com'

# group_id = 70

#########################
# CLI ARGUMENT HANDLING #
#########################

parser=argparse.ArgumentParser()

parser.add_argument('-file', help='Path to file containing API credentials')
parser.add_argument('-id', help='The ID of a LogicMonitor device group whose subgroups correspond to Connectwise Configuration Types')

args = parser.parse_args()

###################
# PARSE API CREDS #
###################

key_file_path = args.file
file = open(key_file_path, 'r')
file_text = file.read()

key_file_json = json.loads(file_text)
AccessId = key_file_json['lm_id']
AccessKey = key_file_json['lm_key']
Company = key_file_json['lm_company']

cw_api_id  = key_file_json['cw_id']
cw_api_key = key_file_json['cw_key']
cw_company = key_file_json['cw_company']
cw_site    = key_file_json['cw_site']

group_id = args.id

###################################
# GET ALL DEVICES WITH DS APPLIED #
###################################

# Build type dict
type_dict = type_sync(AccessId, AccessKey, Company, group_id, cw_api_id, cw_api_key, cw_company, cw_site)
company_dict = company_sync(AccessId, AccessKey, Company, cw_api_id, cw_api_key, cw_company, cw_site)

# Request Info
resourcePath = '/device/devices'
queryParams  = '?size=1000'
data         = ''

thing = LM_GET(AccessId, AccessKey, Company, resourcePath, queryParams, data)

devices = json.loads(thing['body'])['data']['items']

device_array = {}
for item in devices:
	
	device_name  = item['name']
	system_props = item['systemProperties']
	auto_props   = item['autoProperties']
	custom_props = item['customProperties']
	inherited_props = item['inheritedProperties']

	device_array[f'{device_name}'] = {}

	# Properties coming from competing API objects defined below
	company = ''
	for prop in system_props:
		if(prop['name'] == 'system.ips'):
			first_ip = prop['value'].split(',')[0]
			device_array[f'{device_name}']['ipAddress'] = first_ip
		elif(prop['name'] == 'system.sysinfo'):
			os_type = prop['value'][:250]
			device_array[f'{device_name}']['osType'] = os_type
		elif(prop['name'] == 'system.uptime'):
			device_array[f'{device_name}']['uptime'] = prop['value']
		elif(prop['name'] == 'system.model'):
			model = prop['value'][:50]
			device_array[f'{device_name}']['modelNumber'] = model
	for prop in auto_props:
		if('serial' in prop['name']):
			device_array[f'{device_name}']['serialNumber'] = prop['value']
		if('model' in prop['name']):
			model = prop['value'][:50]
			device_array[f'{device_name}']['modelNumber'] = model
	for prop in custom_props:
		if(prop['name'] == 'location'):
			location = prop['value']
		if(prop['name'] == 'company'):
			company = prop['value']
	for prop in inherited_props:
		if(prop['name'] == 'company'):
			company = prop['value']

	########
	# TYPE #
	########

	# Let's figure out best Configuration Type to use
	# Initialize array of host groups and check which 'Device by Type' group we're in
	host_group_string = item['hostGroupIds']
	host_group_array = host_group_string.split(',')
	# I just love this trick!
	host_group_array = [int(x) for x in host_group_array]

	# Initialize an array to hold all 'Device by Type' groups that this device is a member of
	return_type_array = []
	for key, value in type_dict.items():
		# Let's exclude the Collectors group
		if(key != 'Collectors'):
			if(value['lm_id'] in host_group_array):
				return_type_array.append(key)
	# Every device must have a configuration type, so append 'Misc' if it's missing
	if(return_type_array == []):
		return_type_array.append('Misc')
	# Prioritize type alphabetically, then look up ID and NAME
	device_array[f'{device_name}']['type'] = {'id': type_dict[return_type_array[0]]['cw_id'],
	                                          'name': return_type_array[0]}

	###########
	# COMPANY #
	###########

	# All devices must be POSTed with a reference to a company in CW, thus the 'Unknown'
	if(company == ''):
		company = 'Unknown'
	device_array[f'{device_name}']['company'] = {'id': company_dict[company]['cw_id'],
	                                             'name': company,
	                                             'identifier': company_dict[company]['cw_identifier']}

	########
	# NAME #
	########

	device_array[f'{device_name}']['name'] = device_name

#############################
# POST/PATCH CONFIGURATIONS #
#############################

for key, value in device_array.items():
	get_body = get_cw_config_by_name(cw_api_id, cw_api_key, cw_company, cw_site, key)['body'].decode()
	if(get_body == '[]'):
		answer = post_cw_configuration(cw_api_id, cw_api_key, cw_company, cw_site, value)
		if(answer['code'] == 200 or answer['code'] == 201):
			print(f'Record for {key} successfully created')
		else:
			print(f'Unable to create record for {key} with response code {answer["code"]}')
			second_attempt = post_cw_configuration(cw_api_id, cw_api_key, cw_company, cw_site, value)
			print(f'Second attempt has produced response code {second_attempt["code"]}')
			print(f'Response Body')
			print(f'=============')
			print(second_attempt['body'])
	else:
		get_json = json.loads(get_body)
		get_id = get_json[0]['id']

		patch_dict = patch_cw_configuration(cw_api_id, cw_api_key, cw_company, cw_site, value, get_id)
		if(patch_dict['code'] == 200 or answer['code'] == 201):
			print(f'Record for {key} successfully updated')
		else:
			print(f'Unable to update record for {key} with response code {answer["code"]}')
			second_attempt = post_cw_configuration(cw_api_id, cw_api_key, cw_company, cw_site, value)
			print(f'Second attempt has produced response code {second_attempt["code"]}')
			print(f'Response Body')
			print(f'=============')
			print(second_attempt['body'])