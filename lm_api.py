#! /usr/bin/python

import requests
import json
import hashlib
import base64
import time
import hmac

def LM_GET(_lm_id, _lm_key, _lm_account, _resource_path, _query_params, _data):
	url = 'https://'+ _lm_account +'.logicmonitor.com/santaba/rest' + _resource_path + _query_params

	#Get current time in milliseconds
	epoch = str(int(time.time() * 1000))

	#Concatenate Request details
	requestVars = 'GET' + epoch + _data + _resource_path

	# Construct signature
	authCode = hmac.new(_lm_key.encode(),msg=requestVars.encode(),digestmod=hashlib.sha256).hexdigest()
	signature = base64.b64encode(authCode.encode())

	#Construct headers
	auth = 'LMv1 ' + _lm_id + ':' + signature.decode() + ':' + epoch
	headers = {'Content-Type':'multipart/form-data','Authorization':auth,}

	#Make request
	response = requests.get(url, data=_data, headers=headers)

	return_dict = {'code':response.status_code,
				   'body':response.content}

	return return_dict

def LM_POST(_lm_id, _lm_key, _lm_account, _resource_path, _query_params, _data):
	url = 'https://'+ _lm_account +'.logicmonitor.com/santaba/rest' + _resource_path + _query_params

	#Get current time in milliseconds
	epoch = str(int(time.time() * 1000))

	#Concatenate Request details
	requestVars = 'POST' + epoch + _data + _resource_path

	# Construct signature
	authCode = hmac.new(_lm_key.encode(),msg=requestVars.encode(),digestmod=hashlib.sha256).hexdigest()
	signature = base64.b64encode(authCode.encode())

	#Construct headers
	auth = 'LMv1 ' + _lm_id + ':' + signature.decode() + ':' + epoch
	headers = {'Content-Type':'application/json','Authorization':auth}

	#Make request
	response = requests.post(url, data=_data, headers=headers)

	return_dict = {'code':response.status_code,
				   'body':response.content}

	return return_dict

def LM_PATCH(_lm_id, _lm_key, _lm_account, _resource_path, _query_params, _data):
	url = 'https://'+ _lm_account +'.logicmonitor.com/santaba/rest' + _resource_path + _query_params

	#Get current time in milliseconds
	epoch = str(int(time.time() * 1000))

	#Concatenate Request details
	requestVars = 'PATCH' + epoch + _data + _resource_path

	# Construct signature
	authCode = hmac.new(_lm_key.encode(),msg=requestVars.encode(),digestmod=hashlib.sha256).hexdigest()
	signature = base64.b64encode(authCode.encode())

	#Construct headers
	auth = 'LMv1 ' + _lm_id + ':' + signature.decode() + ':' + epoch
	headers = {'Content-Type':'application/json','Authorization':auth,'X-version':'2'}

	#Make request
	response = requests.patch(url, data=_data, headers=headers)

	return_dict = {'code':response.status_code,
				   'body':response.content}

	return return_dict

def LM_PUT(_lm_id, _lm_key, _lm_account, _resource_path, _query_params, _data):
	url = 'https://'+ _lm_account +'.logicmonitor.com/santaba/rest' + _resource_path + _query_params

	#Get current time in milliseconds
	epoch = str(int(time.time() * 1000))

	#Concatenate Request details
	requestVars = 'PUT' + epoch + _data + _resource_path

	# Construct signature
	authCode = hmac.new(_lm_key.encode(),msg=requestVars.encode(),digestmod=hashlib.sha256).hexdigest()
	signature = base64.b64encode(authCode.encode())

	#Construct headers
	auth = 'LMv1 ' + _lm_id + ':' + signature.decode() + ':' + epoch
	headers = {'Content-Type':'application/json','Authorization':auth}

	#Make request
	response = requests.put(url, data=_data, headers=headers)

	return_dict = {'code':response.status_code,
				   'body':response.content}

	return return_dict