#! /usr/bin/python
from api_helpers.cw_api import *
from api_helpers.lm_api import *
from api_helpers.lm_abstract import *
import json
from pprint import pprint

# Company sync should sync between lm and cw, and return a dictionary of possible company references
def company_sync(_lm_api_id, _lm_api_key, _lm_company, _cw_api_id, _cw_api_key, _cw_company, _cw_site, **kwargs):
	#get the LM types list
	lm_companies = get_lm_companies(_lm_api_id, _lm_api_key, _lm_company)
	for item in lm_companies.keys():
		get_result = get_cw_company_by_name(_cw_api_id, _cw_api_key, _cw_company, _cw_site, item)
		if get_result['code'] == 200 or get_result['code'] == 201:
			cw_companies = json.loads(get_result['body'].decode())
			if(cw_companies == []): #if CW doesn't have this company, let's create it in CW
				post_json = json.loads(post_cw_company_by_name(_cw_api_id, _cw_api_key, _cw_company, _cw_site, item)['body'].decode())
				#map the new company in CW to the LM company
				lm_companies[item]['cw_id'] = post_json['id']
				lm_companies[item]['cw_identifier'] = post_json['identifier']
			else: #if CW does have this company, mapt the CW ID/Identifier to the LM company
				lm_companies[item]['cw_id'] = cw_companies[0]['id']
				lm_companies[item]['cw_identifier'] = cw_companies[0]['identifier']
			return {"result": True, "items": lm_companies}
		else: return {"result": False, "items": get_result}

# Type sync should sync between lm and cw, and return a dictionary of possible type references
def type_sync(_lm_api_id, _lm_api_key, _lm_company, _group_id, _cw_api_id, _cw_api_key, _cw_company, _cw_site, **kwargs):
	#get the LM types list
	lm_types = get_lm_device_types(_lm_api_id, _lm_api_key, _lm_company, _group_id)
	for item in lm_types.keys():
		#see if CW has a type by this name
		get_result = get_cw_type_by_name(_cw_api_id, _cw_api_key, _cw_company, _cw_site, item)
		if get_result['code'] == 200 or get_result['code'] == 201:
			cw_types = json.loads(get_result['body'].decode())
			if(cw_types == []): #if CW doesn't have this type, let's create it in CW
				post_json = json.loads(post_cw_type_by_name(_cw_api_id, _cw_api_key, _cw_company, _cw_site, item)['body'].decode())
				#map the new type in CW to the LM type
				lm_types[item]['cw_id'] = post_json['id']
			else: #if CW does have this type, map the CW ID to the LM type
				lm_types[item]['cw_id'] = cw_types[0]['id']
			return {"result": True, "items": lm_types}
		else: return {"result": False, "items": get_result}
