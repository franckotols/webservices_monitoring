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
		
		self.url = "http://giupe.webfactional.com/sitewhere/api"
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = 'IoT_Smart_Health_tenant_token'
		self.auth=('giuseppe', 'francesco')

		#NB E' MOLTO IMPORTANTE AGGIUNGERE IL content-type assegnando application/json NELLE RICHIESTE POST
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
		post_url=self.url+"/assignments/f66646f2-489b-4aab-a41d-e7e0496da031/measurements"
		print post_url		
		data = {
			"eventDate" : "",
			"measurements" : {
				"test.pressione":108
			},
			"metadata":{}
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
		get_url = self.url+"/assignments/676066f6-478a-4882-84ae-dfd1b28cb4d7/measurements"
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

	def post_asset_category(self):
		post_url=self.url+"/assets/categories"
		print post_url
		data = {
			"name": "Lista Medici",
			"id": "lista_medici_asset_ID",
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

	def post_hardware_device_asset(self):
		post_url=self.url+"/assets/categories/PHYSICIAN_APPLICATION_asset_id/hardware"
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
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_specification(self):
		post_url=self.url+"/specifications"
		print post_url
		data = {
			"name" : "Physician App Specification",
			"assetModuleId" : "PHYSICIAN_APPLICATION_asset_id",
			"assetId" : "PHYSICIAN_APPLICATION_ASSET_ID",
			"containerPolicy" : "Standalone",
			"token":"Specification_token_physician_application"
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
		post_url=self.url+"/devices"
		print post_url
		data = {
			"hardwareId" : "iHealt_OpenApiBP_bncnnt60l44c342q-antonietta-bianchi_REAL_DEVICE_ID",
			"siteToken" : "bb105f8d-3150-41f5-b9d1-db04965668d3",
			"specificationToken" : "Specification_token_OpenApiBP",
			"comments" : "Dispositivo di test per la misura della pressione."
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
			"deviceHardwareId" : "iHealt_OpenApiBP_bncnnt60l44c342q-antonietta-bianchi_REAL_DEVICE_ID",
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

	def send_alert_assign_token(self):
		post_url = self.url+"/assignments/a85f0c26-1c7a-47d1-918d-b1f56254640e/alerts"
		data = {
			"eventDate" : "",
			"message": "Il paziente Giuseppe Petralia dovrebbe stare attento alle sue emorroidi",
			"type": "phy-message",
			"metadata":{
				"patient_id": "ptrgpp88l01c342z-giuseppe-petralia",
				"is_message": "yes"
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

	def get_alerts_for_sites(self):
		s=requests.Session()
		get_url = self.url+"/sites/bb105f8d-3150-41f5-b9d1-db04965668d3/alerts"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_nuovo_medico(self):
		post_url=self.url+"/assets/categories/lista_medici_asset_ID/persons"
		print post_url
		data = {
			"id": "nome-cognome-12091982",
			"name": "Nome Cognome",
			"imageUrl": "https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcQB4dVacA67gn_f0CQ1YMZ-cqDucluN1pPoXnEGR1NCa4rutI76",
			"properties": 
				{
					"name":"nome",
					"last name":"cognome",
					"password":"user_password",
					"sex":"sesso",
					"specializzazione":"spec",
					"birthdate":"nascita",
					"phone":"phone"
				},
			"userName": "nome_cognome",
			"emailAddress": "email@email.it",
			"roles":[""]
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_nuovo_paziente(self):
		post_url=self.url+"/assets/categories/PATIENT_LIST_asset_id/persons"
		print post_url
		data = {
			"id": "rssplo88c18c342q-paolo-rossi",
			"name": "PAOLO ROSSI",
			"imageUrl": "https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcQB4dVacA67gn_f0CQ1YMZ-cqDucluN1pPoXnEGR1NCa4rutI76",
			"properties": 
				{
					"TAX code":"rssplo88c18c342q",
					"name":"Paolo",
					"last name":"Rossi",
					"address":"corso Ferrucci 67",
					"city":"Torino",
					"sex":"Male",
					"user_disease":"{\"diseases_list\":[\"Dialisi Peritoneale\",\"Esami del sangue\"]}",
					"birthdate":"18/3/1985",
					"phone":"3331231543",
					"ZIP code":"10143"
				},
			"userName": "paolo_rossi",
			"emailAddress": "paolorossi@mail.com",
			"roles":[""]
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def post_new_site(self):
		post_url=self.url+"/sites"
		print post_url
		data = {
			"name": "Med Site",
			"description": "Sito ad utilizzo esclusivo dei medici. Qui vengono creati tutti gli assignments tra medico e device (in questo caso la app di raccolta dati) e generati gli alert diretti verso i pazienti, cioe' i messagi che vanno dal medico al paziente.",
			"imageUrl": "http://cdn5.acolore.com/disegni/colori/201101/8c797eb7255388bd8466c86ded4f2dbb.png",
			"map":{
				"type":"mapquest",
				"metadata":{}
			},
			"metadata":{}	
		}

		data = json.dumps(data, indent=4, sort_keys=True)
		data = str(data)
		print data
		r = requests.post(post_url, data=data, headers=self.headers, auth=self.auth)
		result = r.text
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_measurement_series(self):
		s=requests.Session()
		get_url = self.url+"/assignments/7e4dda31-0c76-4234-a9ac-1f57cfa357ac/measurements/series"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def send_measurement_diario_clinico(self):
		post_url=self.url+"/assignments/ 4249ec34-2731-4ee3-bc32-3a64996d1221/measurements"
		
		
		data = {
			"eventDate" : "",
			"measurements" : {
				"vol_1_discharge": 0,
				"total_UF": 0,
				"skippedCycles": 0,
				"lostTime": 0,
				"glucose150_bags": 12,
				"glucose250_bags": 13,
				"glucose350_bags": 34,
				"extran_bags": 45,
				"heparin_bags": 56,
				"insulin_bags": 65,
				"antibiotic_bags": 0,
				"totalVolume": 0,
				"loadingVolume": 1,
				"loadStopTime": 2,
				"dischargeTime": 33,
				"lastLoadingVolume": 0,
				"cyclesNumber": 0,
				"loadingVolume_TIDAL": 0,
				"stopTime_TIDAL": 0,
				"volumeUF_TIDAL": 3,
				"totalDischarge_nCycles_TIDAL": 0
			},
			"metadata":{
				"treatment_data": "15-9-2016",
				"treatment_startTime": "11:45",
				"treatment_endTime": "11:56",
				"nausea": "false",
				"vomit": "false",
				"diarrhea": "false",
				"dischargeProblems": "true"
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

	def get_assignmets_in_sites(self):
		s=requests.Session()
		get_url = self.url+"/sites/bb105f8d-3150-41f5-b9d1-db04965668d3/assignments"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
		result = json.loads(result)
		result = json.dumps(result, indent=4, sort_keys=True)
		return result

	def get_assignment_associated_with_asset(self):
		s=requests.Session()
		get_url = self.url+"/assets/modules/PATIENT_LIST_asset_id/assets/rssgcm85c18c342q-giacomo-rossi/assignments"
		r = s.get(get_url, headers=self.headers, auth=self.auth)
		result = r.content
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
	print "10 - post_asset_category"
	print "11 - post_hardware_device_asset"
	print "12 - post_specification"
	print "13 - post_device"
	print "14 - post_assignment"
	print "15 - send_measurement_blood_analysis"
	print "16 - send_alert_assign_token"
	print "17 - get_alerts_for_sites"
	print "18 - post_nuovo_medico"
	print "181 - post_nuovo_paziente"
	print "19 - post_new_site"
	print "20 - get measurements series"
	print "21 - send_measurement_diario_clinico"
	print "22 - get_assignmets_in_sites"
	print "23 - get_assignment_associated_with_asset"
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
		elif comm == "9":
			new_hardware_asset_category = test.post_hardware_asset_category()
			print new_hardware_asset_category
		elif comm == "10":
			new_device_asset_category = test.post_asset_category()
			print new_device_asset_category
		elif comm == "11":
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
		elif comm == "16":
			new_alert = test.send_alert_assign_token()
			print new_alert
		elif comm == "17":
			all_alerts = test.get_alerts_for_sites()
			print all_alerts
		elif comm == "18":
			nuovo_medico = test.post_nuovo_medico()
			print nuovo_medico
		elif comm == "181":
			nuovo_paziente = test.post_nuovo_paziente()
			print nuovo_paziente
		elif comm == "19":
			new_site = test.post_new_site()
			print new_site
		elif comm == "20":
			meas_series = test.get_measurement_series()
			print meas_series
		elif comm == "21":
			meas_diario = test.send_measurement_diario_clinico()
			print meas_diario
		elif comm == "22":
			assignments = test.get_assignmets_in_sites()
			print assignments
		elif comm == "23":
			assignments = test.get_assignment_associated_with_asset()
			print assignments

			
		


