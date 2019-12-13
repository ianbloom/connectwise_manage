#! /usr/bin/python

import requests
import json
import hashlib
import base64
import time
import hmac
from pprint import pprint

def LM_GET(_lm_id, _lm_key, _lm_account, _resource_path, _query_params = {}, _data = '', _query_size = 1000):
	items = []
	last_item_found = False
	status_code = 0
	_query_params['size'] = _query_size
	err_out = ""
	while not last_item_found:
		_query_params['offset'] = len(items)
		_query_params_string = "?" + "&".join([f"{k}={v}" for k,v in _query_params.items()])
		url = 'https://'+ _lm_account +'.logicmonitor.com/santaba/rest' + _resource_path + _query_params_string
		epoch = str(int(time.time() * 1000))
		requestVars = 'GET' + epoch + _data + _resource_path
		authCode = hmac.new(_lm_key.encode(),msg=requestVars.encode(),digestmod=hashlib.sha256).hexdigest()
		signature = base64.b64encode(authCode.encode())
		auth = 'LMv1 ' + _lm_id + ':' + signature.decode() + ':' + epoch
		headers = {'Content-Type':'multipart/form-data','Authorization':auth,}
		response = requests.get(url, data=_data, headers=headers)
		status_code = response.status_code
		current_call_result = json.loads(response.content)
		data = current_call_result['data']
		errmsg = current_call_result['errmsg']
		status = current_call_result['status']
		fetched_count = len(data['items'])
		fetched_items = data['items']
		items += fetched_items
		last_item_found = fetched_count < _query_size
		err_out += f"Call to {url} results:\n\tHTTP Response code: {status_code}\n\tError Message: {errmsg}\n\tStatus code: {status}\n\tItems fetched: {fetched_count}\n\tTotal items fetched: {len(items)}\n\tLast item found: {last_item_found}\n"
	return {'code':status_code, 'items':items, 'err_out': err_out}
