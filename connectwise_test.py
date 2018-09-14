from api_helpers.lm_api import *
from api_helpers.cw_api import *

api_id           = 'SfefZokssi9JFFuK'
api_key          = 'EOjLXH5wVI9krM32'
company          = 'logicmonitor_f'
connectwise_site = 'staging.connectwisedev.com'

response_dict = get_cw_type_list(api_id, api_key, company, connectwise_site)

pprint(json.loads(response_dict['body']))