import random
import requests
import string 
import cherrypy
import json
import urllib
import urllib2
import operator
from sys import argv
from pymongo import Connection, MongoClient
import pprint

class testSitewhere(object):

	def __init__(self):

		self.id = id
		
		self.url = "http://localhost:8080/sitewhere/api"
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = 'PATIENT_LIST_tenant_token'
		self.tenant_pat_id="PATIENT_LIST_tenant_id"
		self.tenant_pat_name="PatientRemoteMonitoring"
		self.tenant_pat_logo="data:image/jpeg;base64,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"
		self.auth=('franckotols', '000000')

		#NB E' MOLTO IMPORTANTE AGGIUNGERE IL content-type assegnango application/json NELLE RICHIESTE POST
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token, "content-type":"application/json"}

		
		#ASSET LISTA MEDICI
		self.asset_med_id="lista_medici_asset_ID"
		self.asset_med_name="Lista Medici"

		


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

	def get_assets_categories_by_id(self):
		s=requests.Session()
		get_url = self.url+"/assets/categories/lista_medici_asset_ID"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_assets_categoryID_assets(self):
		s=requests.Session()
		get_url = self.url+"/assets/categories/PATIENT_LIST_asset_id/assets"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_assets_categoryID_assetID(self):
		s=requests.Session()
		get_url = self.url+"/assets/categories/lista_medici_asset_ID/assets/chiara-tolu"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_assignement(self):
		s=requests.Session()
		get_url = self.url+"/assignments/fbf83dd6-d2a6-4a39-9265-d5f879945f57"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def send_measurement(self):
		post_url=self.url+"/assignments/fbf83dd6-d2a6-4a39-9265-d5f879945f57/measurements"
		print post_url
		dict_test = {"prova":"antani","ciao":"miao"}
		json_test = json.dumps(dict_test)
		metadata = str(json_test)
		
		data = {
			"eventDate" : "",
			"measurements" : {
				"test1" : 123,
				"test2" : 76
			},
			"metadata":{"situazione":"stabile","peso":"stabile"}
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_meaurements_by_assignment_token(self):
		s=requests.Session()
		get_url = self.url+"/assignments/7e4dda31-0c76-4234-a9ac-1f57cfa357ac/measurements"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_hardware_asset_category(self):
		post_url=self.url+"/assets/categories"
		print post_url
		data = {
			"name": "Hardware Manager",
			"id": "ifs-hardware",
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

	def post_device_asset_category(self):
		post_url=self.url+"/assets/categories"
		print post_url
		data = {
			"name": "Test Device",
			"id": "test-device",
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

	def post_hardware_device_asset(self):
		post_url=self.url+"/assets/categories/fs-devices/hardware"
		print post_url
		data = {
			"id": "2190",
			"name": "Esami del Sangue",
			"imageUrl": "http://www.laboratoriobalistreri.it/polopoly_fs/1.18133099.1406888453!/httpImage/img.jpg_gen/derivatives/landscape_490/img.jpg",
			"properties": {"type":"software"},
			"sku": "BLAN-SOFT",
			"description": "Software App for sending blood analysis"
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_specification(self):
		post_url=self.url+"/specifications"
		print post_url
		data = {
			"name" : "AppBloodAnalysis",
			"assetModuleId" : "fs-devices",
			"assetId" : "2190",
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

	def post_device(self):
		post_url=self.url+"/assignments"
		print post_url
		data = {
			"hardwareId" : "4242-3421",
			"siteToken" : "de7397e2-3855-4f4f-a8fd-d4c7ccd67823",
			"specificationToken" : "ab4e3b64-5504-4140-8713-38bf58e18391",
			"comments" : "Android App for sending blood analysis."
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_assignment(self):
		post_url=self.url+"/assignments"
		print post_url
		data = {
			"deviceHardwareId" : "4242-3421",
			"assignmentType" : "Associated",
			"assetModuleId" : "PATIENT_LIST_asset_id",
			"assetId" : "bncnnt60l44c342q-antonietta-bianchi",
			"metadata": {}
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def send_measurement_blood_analysis(self):
		post_url=self.url+"/assignments/7e4dda31-0c76-4234-a9ac-1f57cfa357ac/measurements"
		
		
		data = {
			"eventDate" : "",
			"measurements" : {
				"Creatinine": 34,
				"Creatinine": 23,
				"DiuresisVolume": 34,
				"ClarenceVolume": 45,
				"TotalProtein": 2,
				"Albumin": 6,
				"Calcium": 7,
				"Phosphorus": 67,
				"CompleteBloodCount(CBC)": 12,
				"ParathyroidHormone(PTH) ": 23,
				"Hemoglobin": 90,
				"Triglycerides": 87,
				"Cholesterol": 12
			}
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result
		

if __name__ == "__main__":

	test = testSitewhere()

	print "1 - get_sites"
	print "2 - get_assets_categories"
	print "3 - get_assets_categories_by_id"
	print "4 - get_assets_categoryID_assets"
	print "5 - get_assets_categoryID_assetID"
	print "6 - get_assignement"
	print "7 - send_measurement"
	print "8 - get_meaurements_by_assignment_token"
	print "9 - post_hardware_asset_category"
	print "10 - post_device_asset_category"
	print "11 - post_hardware_device_asset"
	print "12 - post_specification"
	print "13 - post_device"
	print "14 - post_assignment"
	print "15 - send_measurement_blood_analysis"
	
	while True:
		comm = raw_input("Insert command: ")
		if comm == "1":
			sites = test.get_sites()
			print sites 
		elif comm == "2":
			assets_categories = test.get_assets_categories()
			print assets_categories
		elif comm == "3":
			assets_categories_by_id = test.get_assets_categories_by_id()
			print assets_categories_by_id
		elif comm == "4":
			assets_categoriesID_assets = test.get_assets_categoryID_assets()
			print assets_categoriesID_assets
		elif comm == "5":
			assets_categoriesID_assetID = test.get_assets_categoryID_assetID()
			print assets_categoriesID_assetID
		elif comm == "6":
			assignment = test.get_assignement()
			print assignment
		elif comm == "7":
			post = test.send_measurement()
			print post
		elif comm == "8":
			measurements = test.get_meaurements_by_assignment_token()
			print measurements
			###############################
			# PER ACCEDERE AI METADATA    #
			###############################
			# dixt = json.loads(measurements)
			# mydixt = dixt["results"]
			# #print mydixt[0]["metadata"]
			# for k in range(0,len(mydixt)):
			# 	print json.dumps(mydixt[k]["metadata"])
		elif comm == "9":
			new_hardware_asset_category = test.post_hardware_asset_category()
			print new_hardware_asset_category
		elif comm == "10":
			new_device_asset_category = test.post_device_asset_category()
			print new_device_asset_category
		elif comm == "11":
			# id_asset = raw_input("Insert id asset device: ")
			# name = raw_input("Insert name: ")
			# image_url = raw_input("Insert image url: ")
			# sku = raw_input("Insert sku: ")
			# description = raw_input("Insert description: ")
			new_device = test.post_hardware_device_asset()
			print new_device
		elif comm == "12":
			new_specification = test.post_specification()
			print new_specification
		elif comm == "13":
			new_device = test.post_device()
			print new_device
		elif comm == "14":
			new_assignment = test.post_assignment()
			print new_assignment
		elif comm == "15":
			blood_analysis = test.send_measurement_blood_analysis()
			print blood_analysis

			
		

