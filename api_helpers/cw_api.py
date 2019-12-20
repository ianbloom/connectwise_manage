# #! /usr/bin/python3
# import json
# import base64
# import requests
# from pprint import pprint
#
# ###########
# # HELPERS #
# ###########
# def header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId, addnlheaderitems = {}):
# 	header_dict = {}
# 	header_dict['Content-Type'] = 'application/json'
# 	header_dict['clientId'] = _cw_agentId
# 	token = f'{_cw_company}+{_cw_api_id}:{_cw_api_key}'
# 	encoded_token = (base64.b64encode(token.encode())).decode()
# 	header_dict['Authorization'] = f'Basic {encoded_token}'
# 	header_dict.update(addnlheaderitems)
# 	return header_dict
#
# ###########
# # GETTERS #
# ###########
# def get_cw_config_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
# 	query_size = 1000
# 	last_found = False
# 	devices = {}
# 	page = 1
# 	while not last_found:
# 		url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations?pagesize={query_size}&page={page}'
# 		response = requests.get(url, data="", headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
# 		this_call_devices = {}
# 		if response.status_code in (200, 201):
# 			for device in json.loads(response.content):
# 				this_call_devices[device['name']] = [device['id'], device['type']]
# 			links = {}
# 			if len(response.headers['Link']) > 0:
# 				for link in response.headers['Link'].split(","):
# 					links[link.split(";")[1]] = link.split(";")[0]
# 			last_found = ' rel="last"' not in links.keys()
# 			devices.update(this_call_devices)
# 			page += 1
# 		else:
# 			devices = response
# 	return {'code':response.status_code, 'items':devices}
#
# def get_cw_company_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
# 	query_size = 1000
# 	last_found = False
# 	companies = {}
# 	page = 1
# 	while not last_found:
# 		url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/companies?pagesize={query_size}&page={page}'
# 		response = requests.get(url, data="", headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
# 		this_call_companies = {}
# 		if response.status_code in (200, 201):
# 			for company in json.loads(response.content):
# 				this_call_companies[str(company['id'])] = {'id': company['id'],'name': company['name'],'identifier': company['identifier']}
# 			links = {}
# 			if len(response.headers['Link']) > 0:
# 				for link in response.headers['Link'].split(","):
# 					links[link.split(";")[1]] = link.split(";")[0]
# 			last_found = ' rel="last"' not in links.keys()
# 			companies.update(this_call_companies)
# 			page += 1
# 		else:
# 			companies = response.content
# 	return {'code':response.status_code, 'items':companies}
#
# def get_cw_type_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
# 	query_size = 1000
# 	last_found = False
# 	types = {}
# 	page = 1
# 	while not last_found:
# 		url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations/types?pagesize={query_size}&page={page}'
# 		response = requests.get(url, data="", headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
# 		this_call_types = {}
# 		if response.status_code in (200, 201):
# 			for type in json.loads(response.content):
# 				types[type['name']] = type['id']
# 			links = {}
# 			if len(response.headers['Link']) > 0:
# 				for link in response.headers['Link'].split(","):
# 					links[link.split(";")[1]] = link.split(";")[0]
# 			last_found = ' rel="last"' not in links.keys()
# 			types.update(this_call_types)
# 			page += 1
# 		else:
# 			types = response.content
# 	return {'code':response.status_code, 'items':types}
#
# def get_cw_manufacturer_list(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId):
# 	query_size = 1000
# 	last_found = False
# 	items = {}
# 	page = 1
# 	while not last_found:
# 		url = f'https://{_cw_site}/v4_6_release/apis/3.0/procurement/manufacturers?pagesize={query_size}&page={page}'
# 		response = requests.get(url, data="", headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
# 		this_call_items = {}
# 		if response.status_code in (200, 201):
# 			for item in json.loads(response.content):
# 				this_call_items[str(item['name'])] = {'id': item['id'],'name': item['name'],'inactiveFlag': item['inactiveFlag']}
# 			links = {}
# 			if len(response.headers['Link']) > 0:
# 				for link in response.headers['Link'].split(","):
# 					links[link.split(";")[1]] = link.split(";")[0]
# 			last_found = ' rel="last"' not in links.keys()
# 			items.update(this_call_items)
# 			page += 1
# 		else:
# 			items = response.content
# 	return {'code':response.status_code, 'items':items}
#
# ###########
# # POSTERS #
# ###########
# def post_cw_configuration(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId, _config_dict):
# 	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations'
# 	data = json.dumps(_config_dict)
# 	#something's incomplete in the _config_dict, not sure what.
# 	response = requests.post(url, data=data, headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
# 	return {'code':response.status_code, 'body':json.loads(response.content.decode())}
#
# ############
# # PATCHERS #
# ############
# def patch_cw_configuration(_cw_api_id, _cw_api_key, _cw_company, _cw_site, _cw_agentId, _config_dict, _config_id):
# 	url = f'https://{_cw_site}/v4_6_release/apis/3.0/company/configurations/{_config_id}'
# 	patch_array = []
# 	for key, value in _config_dict.items():
# 		patch_dict = {'op':'replace',
# 					  'path':key,
# 					  'value':value}
# 		patch_array.append(patch_dict)
# 	data = json.dumps(patch_array)
# 	response = requests.patch(url, data=data, headers=header_build(_cw_company, _cw_api_id, _cw_api_key, _cw_agentId))
# 	return {'code':response.status_code, 'body':response.content}
