#! /usr/bin/python

from api_helpers.cw_api import *
from api_helpers.lm_api import *
from api_helpers.lm_abstract import *
import json
from pprint import pprint

# Company sync should sync between lm and cw, and return a dictionary of possible company references
def company_sync(_lm_api_id, _lm_api_key, _lm_company, _cw_api_id, _cw_api_key, _cw_company, _cw_site):
	lm_companies = get_lm_companies(_lm_api_id, _lm_api_key, _lm_company)

	for item in lm_companies.keys():
		get_result = get_cw_company_by_name(_cw_api_id, _cw_api_key, _cw_company, _cw_site, item)
		response_body = get_result['body'].decode()
		json_body = json.loads(response_body)

		if(json_body == []):
			post_body = post_cw_company_by_name(_cw_api_id, _cw_api_key, _cw_company, _cw_site, item)['body'].decode()
			post_json = json.loads(post_body)
			connect_id = post_json['id']
			connect_identifier = post_json['identifier']

			lm_companies[item]['cw_id'] = connect_id
			lm_companies[item]['cw_identifier'] = connect_identifier
		else:
			connect_id = json_body[0]['id']
			connect_identifier = json_body[0]['identifier']

			lm_companies[item]['cw_id'] = connect_id
			lm_companies[item]['cw_identifier'] = connect_identifier

	return lm_companies
# Type sync should sync between lm and cw, and return a dictionary of possible type references
def type_sync(_lm_api_id, _lm_api_key, _lm_company, _group_id, _cw_api_id, _cw_api_key, _cw_company, _cw_site):
	lm_types = get_lm_device_types(_lm_api_id, _lm_api_key, _lm_company, _group_id)

	for item in lm_types.keys():
		get_result = get_cw_type_by_name(_cw_api_id, _cw_api_key, _cw_company, _cw_site, item)
		response_body = get_result['body'].decode()
		json_body = json.loads(response_body)

		if(json_body == []):
			post_body = post_cw_type_by_name(_cw_api_id, _cw_api_key, _cw_company, _cw_site, item)['body'].decode()
			post_json = json.loads(post_body)
			connect_id = post_json['id']

			lm_types[item]['cw_id'] = connect_id
		else:
			connect_id = json_body[0]['id']

			lm_types[item]['cw_id'] = connect_id

	return lm_types