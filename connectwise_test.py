from api_helpers.lm_api import *
from api_helpers.cw_api import *
from api_helpers.lm_abstract import *
from pprint import pprint

cw_api_id  = 'SfefZokssi9JFFuK'
cw_api_key = 'EOjLXH5wVI9krM32'
cw_company = 'logicmonitor_f'
cw_site    = 'staging.connectwisedev.com'

lm_api_id  = 'tZ3u4e8k8y2M3ttevFj6'
lm_api_key = 'Xe5~e4P%9kErB(98Ri89h5]CJ4j~w}Dy)wGJ6k%4'
lm_company = 'bcservice'

group_id = 70

lm_device_types = get_lm_device_types(lm_api_id, lm_api_key, lm_company, group_id)

lm_companies = get_lm_companies(lm_api_id, lm_api_key, lm_company)

for item in lm_companies.keys():
	get_result = get_cw_company_by_name(cw_api_id, cw_api_key, cw_company, cw_site, item)
	response_body = get_result['body'].decode()
	json_body = json.loads(response_body)
	pprint(response_body)

	if(response_body == '[]' or json_body[0]['deletedFlag'] == True):
		final_body = post_cw_company_by_name(cw_api_id, cw_api_key, cw_company, cw_site, item)['body'].decode()
		final_json = json.loads(final_body)
		pprint(final_json)
		connect_id = final_json['id']

		lm_companies[item]['cw_id'] = connect_id
	else:
		final_json = json.loads(response_body)
		connect_id = final_json[0]['id']

		lm_companies[item]['cw_id'] = connect_id


pprint(lm_companies)