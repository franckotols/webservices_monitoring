import random
import requests
import string 
import json
import operator
from sys import argv


class testSitewhere(object):

	def __init__(self, url, tenant_token, auth):

		self.id = id
		
		self.url = url
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = tenant_token
		self.auth= auth

		#Interno a Sitewhere, non c'e' bisogno di inserirlo come parametro, e' sempre lo stesso
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token, "content-type":"application/json"}


	def get_sites(self):
		s=requests.Session()
		get_url = self.url+"/sites"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_assets_categories(self):
		s=requests.Session()
		get_url = self.url+"/assets/categories"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_assets_categories_by_id(self, category_id):
		s=requests.Session()
		get_url = self.url+"/assets/categories/"+category_id
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_assets_categoryID_assets(self, category_id):
		s=requests.Session()
		get_url = self.url+"/assets/categories/"+category_id+"/assets"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_assets_categoryID_assetID(self, category_id, asset_id):
		s=requests.Session()
		get_url = self.url+"/assets/categories/"+category_id+"/assets/"+asset_id
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_assignement(self, assign_token):
		s=requests.Session()
		get_url = self.url+"/assignments/"+assign_token
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_meaurements_by_assignment_token(self, assign_token):
		s=requests.Session()
		get_url = self.url+"/assignments/"+assign_token"/measurements"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_alerts_for_sites(self, site_token):
		s=requests.Session()
		get_url = self.url+"/sites/"+site_token+"/alerts"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_hardware_asset_category(self, name, id_asset_category):
		post_url=self.url+"/assets/categories"
		print post_url
		data = {
			"name": name,
			"id": id_asset_category,
			"assetType": "Hardware"
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_device_asset_category(self, name, id_asset_category):
		post_url=self.url+"/assets/categories"
		print post_url
		data = {
			"name":name,
			"id": id_asset_category,
			"assetType": "Device"
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_person_asset_category(self, name, id_asset_category):
		post_url=self.url+"/assets/categories"
		print post_url
		data = {
			"name":name,
			"id": id_asset_category,
			"assetType": "Person"
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_hardware_device_asset(self, id_category_devices, id_asset_device, name, image_url, properties, sku, description):
		post_url=self.url+"/assets/categories/"+id_category_devices+"/hardware"
		print post_url
		data = {
			"id": id_asset_device,
			"name": name,
			"imageUrl": image_url,
			"properties": properties,
			"sku": sku,
			"description": description
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_specification(self, name, asset_module_id, asset_id):
		post_url=self.url+"/specifications"
		print post_url
		data = {
			"name" : name,
			"assetModuleId" : asset_module_id,
			"assetId" : asset_id,
			"containerPolicy" : "Standalone"
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_device(self, hardwareId, siteToken, specificationToken, comments):
		post_url=self.url+"/device"
		print post_url
		data = {
			"hardwareId" : hardwareId,
			"siteToken" : siteToken,
			"specificationToken" : specificationToken,
			"comments" : comments
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_assignment(self, deviceHardwareId, assetModuleId, assetId, metadata):
		post_url=self.url+"/assignments"
		print post_url
		data = {
			"deviceHardwareId" : deviceHardwareId,
			"assignmentType" : "Associated",
			"assetModuleId" : assetModuleId,
			"assetId" : assetId,
			"metadata": metadata
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def send_measurement(self, assign_token, measurements, metadata):
		post_url=self.url+"/assignments/"+assign_token+"/measurements"
		print post_url
		
		data = {
			"eventDate" : "",
			"measurements" : measurements,
			"metadata": metadata
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def send_alert_assign_token(self, assign_token, message, alert_type):
		post_url = self.url+"/assignments/"+assign_token+"/alerts"
		data = {
			"eventDate" : "",
			"message": message,
			"type": alert_type
		}
		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)

	