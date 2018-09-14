#! /usr/bin/python

from api_func.api_func import *
import pandas
import json
import sys
from io import StringIO
import argparse
from pprint import *

AccessId  = 'tZ3u4e8k8y2M3ttevFj6'
AccessKey = 'Xe5~e4P%9kErB(98Ri89h5]CJ4j~w}Dy)wGJ6k%4'
Company   = 'bcservice'

###################################
# GET ALL DEVICES WITH DS APPLIED #
###################################

# Request Info
resourcePath = '/device/devices'
queryParams  ='?size=1000'
data         = ''

thing = LM_GET(AccessId, AccessKey, Company, resourcePath, queryParams, data)

lm_response = json.loads(thing['body'])
devices = lm_response['data']['items']

device_array = {}
for item in devices:

	device_name  = item['name']
	system_props = item['systemProperties']
	auto_props   = item['autoProperties']
	custom_props = item['customProperties']

	device_array[f'{device_name}'] = {}

	# Properties coming from competing API objects defined below
	location = ''
	for prop in system_props:
		if(prop['name'] == 'system.ips'):
			device_array[f'{device_name}']['ips'] = prop['value']
		elif(prop['name'] == 'system.sysinfo'):
			device_array[f'{device_name}']['sysinfo'] = prop['value']
		elif(prop['name'] == 'system.uptime'):
			device_array[f'{device_name}']['uptime'] = prop['value']		
	for prop in auto_props:
		if('serial' in prop['name']):
			device_array[f'{device_name}']['serialNumber'] = prop['value']
		if('model' in prop['name']):
			device_array[f'{device_name}']['modelNumber'] = prop['value']
		if(prop['name'] == 'auto.location'):
			location = prop['value']
	for prop in custom_props:
		if(prop['name'] == 'location'):
			location = prop['value']

	# Set potentially competing device properties
	device_array[f'{device_name}']['location'] = location
	device_array[f'{device_name}']['company'] = 'bcservice'

pprint(device_array)