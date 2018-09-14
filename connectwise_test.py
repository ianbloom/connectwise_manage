from api_helpers.lm_api import *
from api_helpers.cw_api import *
from api_helpers.lm_abstract import *
from pprint import pprint

cw_api_id           = 'SfefZokssi9JFFuK'
cw_api_key          = 'EOjLXH5wVI9krM32'
cw_company          = 'logicmonitor_f'
cw_site = 'staging.connectwisedev.com'

lm_api_id  = 'tZ3u4e8k8y2M3ttevFj6'
lm_api_key = 'Xe5~e4P%9kErB(98Ri89h5]CJ4j~w}Dy)wGJ6k%4'
lm_company   = 'bcservice'

group_id = 70

# response_dict = get_cw_type_list(cw_api_id, cw_api_key, cw_company, cw_site)

# pprint(json.loads(response_dict['body']))

response_array = get_lm_device_types(lm_api_id, lm_api_key, lm_company, group_id)
pprint(response_array)