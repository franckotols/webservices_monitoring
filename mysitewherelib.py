#----------------------------------------------------------------------------------------------
# Sitewhere library for cherrypy web services. Features:
# - Sending POST and GET requests for send and receive data, using request python library
# - error management
#----------------------------------------------------------------------------------------------

import random
import requests
import string 
import json
import operator
from sys import argv
import cherrypy


class SitewhereManager(object):

	def __init__(self, url, tenant_token, auth):

		self.id = id
		
		self.url = url
		self.tenant_token = tenant_token
		self.auth= auth
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token, "content-type":"application/json"}


	def get_sites(self):
		s=requests.Session()
		get_url = self.url+"/sites"
		try:
			r = s.get(get_url, headers=self.headers, auth=self.auth)
			result = r.content
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def get_assets_categories(self):
		s=requests.Session()
		get_url = self.url+"/assets/categories"
		try:
			r = s.get(get_url, headers=self.headers, auth=self.auth)
			result = r.content
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def get_assets_categories_by_id(self, category_id):
		s=requests.Session()
		get_url = self.url+"/assets/categories/"+category_id
		try:
			r = s.get(get_url, headers=self.headers, auth=self.auth)
			result = r.content
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def get_assets_categoryID_assets(self, category_id):
		s=requests.Session()
		get_url = self.url+"/assets/categories/"+category_id+"/assets"
		try:
			r = s.get(get_url, headers=self.headers, auth=self.auth)
			result = r.content
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def get_assets_categoryID_assetID(self, category_id, asset_id):
		s=requests.Session()
		get_url = self.url+"/assets/categories/"+category_id+"/assets/"+asset_id
		try:
			r = s.get(get_url, headers=self.headers, auth=self.auth)
			result = r.content
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def get_assignments_in_site(self,site_token):
		s=requests.Session()
		get_url = self.url+"/sites/"+site_token+"/assignments"
		try:
			r = s.get(get_url, headers=self.headers, auth=self.auth)
			result = r.content
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"
		

	def get_assignements(self, assign_token):
		s=requests.Session()
		get_url = self.url+"/assignments/"+assign_token
		try:
			r = s.get(get_url, headers=self.headers, auth=self.auth)
			result = r.content
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def get_assignment_associated_with_asset(self,asset_module_id,asset_id):
		s=requests.Session()
		get_url = self.url+"/assets/modules/"+asset_module_id+"/assets/"+asset_id+"/assignments"
		try:
			r = s.get(get_url, headers=self.headers, auth=self.auth)
			result = r.content
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def get_meaurements_by_assignment_token(self, assign_token):
		s=requests.Session()
		get_url = self.url+"/assignments/"+assign_token+"/measurements"
		try:
			r = s.get(get_url, headers=self.headers, auth=self.auth)
			result = r.content
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def get_alerts_for_sites(self, site_token):
		s=requests.Session()
		get_url = self.url+"/sites/"+site_token+"/alerts"
		try:
			r = s.get(get_url, headers=self.headers, auth=self.auth)
			result = r.content
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def post_new_site(self, name, description, image_url):
		post_url=self.url+"/sites"
		print post_url
		data = {
			"name": name,
			"description": description,
			"imageUrl": imageUrl,
			"map":{
				"type":"mapquest",
				"metadata":{}
			},
			"metadata":{}	
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		try:
			r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
			result = r.text
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

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
		try:
			r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
			result = r.text
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

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
		try:
			r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
			result = r.text
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

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
		try:
			r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
			result = r.text
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

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
		try:
			r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
			result = r.text
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def post_app_asset_device(self,id_category_devices):
		post_url=self.url+"/assets/categories/"+id_category_devices+"/hardware"
		print post_url
		data = {
			"id": "PHYSICIAN_APPLICATION_ASSET_ID",
			"name": "Monitoring App Android",
			"imageUrl": "http://clok.contrarium.net/images/c/ce/Android.png",
			"properties": {"type":"hardware"},
			"sku": "MED-APP",
			"description": "Applicazione software utilizzata dal medico per il monitoraggio dei parametri dei pazienti, in grado di inviare notifiche."
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		try:
			r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
			result = r.text
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def post_new_person_asset(self, id_category_persons, id_person, name, image_url, properties, username, email):
		post_url=self.url+"/assets/categories/"+id_category_persons+"/persons"
		print post_url
		data = {
			"id": id_person,
			"name": name,
			"imageUrl": image_url,
			"properties": properties,
			"userName": username,
			"emailAddress": email,
			"roles":[""]
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		try:
			r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
			result = r.text
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"


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
		try:
			r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
			result = r.text
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

##########################################################################################################
# PARTE DELLA LIBRERIA UTILE PER L'INIZIALIZZAZIONE DELL'ASSET E DELLA SPECIFICATION PER L'APPLICAZIONE 
# DEL MEDICO
##########################################################################################################

	def init_asset_specification(self,id_category_devices,asset_id,specification_token):
		url_asset=self.url+"/assets/categories/"+id_category_devices+"/hardware"
		data_asset = {
			"id": asset_id,
			"name": "Monitoring App Android",
			"imageUrl": "http://clok.contrarium.net/images/c/ce/Android.png",
			"properties": {"type":"hardware"},
			"sku": "MED-APP",
			"description": "Applicazione software utilizzata dal medico per il monitoraggio dei parametri dei pazienti, in grado di inviare notifiche."
		}
		url_spec=self.url+"/specifications"
		data_specification = {
			"name" : "Physician App Specification",
			"assetModuleId" : id_category_devices,
			"assetId" : asset_id,
			"containerPolicy" : "Standalone",
			"token":specification_token
		}

		data_asset = json.dumps(data_asset, indent=4, sort_keys=True)
		data_asset = str(data_asset)
		r_asset = requests.post(url_asset, data=data_asset, headers=self.headers, auth=self.auth)

		data_specification = json.dumps(data_specification, indent=4, sort_keys=True)
		data_specification = str(data_specification)
		r_specification = requests.post(url_spec, data=data_specification, headers=self.headers, auth=self.auth)

	def create_command(self,specification_token):
		post_url = self.url+"/specifications/"+specification_token+"/commands"
		data = {
			"name": "comm_physician"
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)

		

	def post_device(self, hardwareId, siteToken, specificationToken, comments):
		post_url=self.url+"/devices"
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
		try:
			r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
			result = r.text
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def post_assignment(self, deviceHardwareId, assetModuleId, assetId, metadata):
		#assetModuleId is the id of the asset which you assign the device, isn't the asset id of the devices
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
		try:
			r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
			result = r.text
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

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
		try:
			r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
			result = r.text
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		except:
			return "error_string"

	def send_alert_assign_token(self, assign_token, message, alert_type, metadata):
		post_url = self.url+"/assignments/"+assign_token+"/alerts"
		data = {
			"eventDate" : "",
			"message": message,
			"type": alert_type,
			"metadata": metadata
		}
		data = json.dumps(data, indent=4, sort_keys=True)
		
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		if r.status_code == 200:
			result = r.text
			result = json.loads(result)
			result = json.dumps(result, indent=4, sort_keys=True)
			return result
		else:
			return "error_string"

	