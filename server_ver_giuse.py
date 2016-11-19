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
from bson.objectid import ObjectId
from mysitewherelib import SitewhereManager
import datetime
import math

class RegistrationServer(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]

	#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary

		
		
	def GET (self, *uri, **params):

		if uri[0] == "specializzazioni":
			#posso scrivere anche con=Connection()
			con = MongoClient()
			db = con['utils']
			collection = db.specializzazioni #e' la collection
			#docu = spec.find() find non va bene perche' restituisce un oggetto pymongo.cursor.cursos
			docu = collection.find_one() #restituisce il dizionario 
			target = docu["specializzazioni"]
			mydict = {"specializzazioni": target}
			return json.dumps(mydict)
			
	def POST (self, * uri, ** params):
		
		#funzione toglispazi di Giuseppe
		def toglispazi_startend(temp):
			temp=str(temp)
			if (len(temp)!=0):
				if (temp[-1]==" "):
					temp=temp[0:(len(temp))-1]
			if (len(temp)!=0):
				if (temp[0]==" "):
					temp=temp[1:(len(temp))]
			return (temp)

		#--------------------------------------------------------------------------------------------------
		# Prima elaborazione parametri che arrivano dalla App
		#--------------------------------------------------------------------------------------------------
		data=str(params['new_user_data'])
		#elaborazione dei params
		data_obj=json.loads(data)
		nome=data_obj['first_name']
		cognome=data_obj['last_name']
		user_password = data_obj['password']
		sesso=data_obj['sex']
		spec = data_obj['specializzazione']
		giorno=str(data_obj['day'])
		mese=str(data_obj['month'])
		anno=str(data_obj['year'])
		email=data_obj['email']
		phone=data_obj['phone']
		#Funzione toglispazi
		nome=toglispazi_startend(nome)
		cognome=toglispazi_startend(cognome)
		user_password = toglispazi_startend(user_password)
		email=toglispazi_startend(email)
		phone=toglispazi_startend(phone)
		imm_url="https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcQB4dVacA67gn_f0CQ1YMZ-cqDucluN1pPoXnEGR1NCa4rutI76"
		if (sesso=="Female"):
			imm_url="https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcSeMhLE4mlN1K4KrmWh9e_qkKS46K5_F4I9zAPXoJH_3zQawLLycg"
		
		#--------------------------------------------------------------------------------------------------
		# Adattamento parametri per la registrazione del medico su sitewhere
		#--------------------------------------------------------------------------------------------------
		nome_alpha_only="".join([i for i in nome if i.isalpha()])
		cognome_alpha_only="".join([i for i in cognome if i.isalpha()])
		med_username=(nome_alpha_only+"_"+cognome_alpha_only).lower()
		med_id=(nome_alpha_only+"-"+cognome_alpha_only).lower()+"-"+giorno+mese+anno
		med_name=nome.upper()+" "+cognome.upper()
		nascita = giorno+"/"+mese+"/"+anno
		hardware_id = med_id+"-Android-App"
		metadata = {}
		comments = "Monitoring APP: "+med_name
		properties = {"name":nome, "last name":cognome, "password":user_password, "sex":sesso, "specializzazione":spec,"birthdate":nascita, "phone":phone}
		
		#---------------------------------------------------------------------------------------------------
		# GET REQUEST TO: http://localhost:8080/sitewhere/api/assets/categories/lista_medici_asset_ID/assets
		#---------------------------------------------------------------------------------------------------
		lista_medici = self.mySitewhere.get_assets_categoryID_assets(self.asset_med_id)
		print lista_medici
		if lista_medici != "error_string":
			dixt = json.loads(lista_medici)
			medici = dixt['results']
			index = 0
			count = 0
			for i in range(0,(len(medici))):
				if med_username == medici[i]["userName"] or email == medici[i]["emailAddress"]:
					index = index + 1
			if index == 0:
				#--------------------------------------------------------------------------------------------------
				# POST REQUEST: Registrazione del medico, del device e dell'assignment tra medico e device
				#--------------------------------------------------------------------------------------------------
				#questa funzione serve per creare la prima volta l'asset e la specification relativi all'applicazione del medico
				#se esistono gia' non dovrebbe succedere niente
				self.mySitewhere.init_asset_specification(self.device_asset_id,self.asset_app_id,self.app_specification_token)
				self.mySitewhere.create_command(self.app_specification_token)
				nuovo_medico = self.mySitewhere.post_new_person_asset(self.asset_med_id, med_id, med_name, imm_url, properties, med_username, email)
				print nuovo_medico
				if nuovo_medico != "error_string":					
					count = count+1
					nuovo_device = self.mySitewhere.post_device(hardware_id, self.med_site_token, self.app_specification_token, comments)
					print nuovo_device
					if nuovo_device != "error_string":
						count = count+1
						nuovo_assignment = self.mySitewhere.post_assignment(hardware_id, self.asset_med_id, med_id, metadata)
						print nuovo_assignment
						if nuovo_assignment != "error_string":
							count=count+1
				#--------------------------------------------------------------------------------------------------
				# POST REQUEST: Se tutti e tre i passi sono andati a buon fine....
				#--------------------------------------------------------------------------------------------------			
				if count == 3:
					return "Registration successful"
				else:
					raise cherrypy.HTTPError(400, "something_wrong")
			else:
				#codice messo a caso
				raise cherrypy.HTTPError(400, "utente_registrato")
		else:
			raise cherrypy.HTTPError(400, "something_wrong")
		

	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass


class AuthenticationServer(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]

	#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):

		pass

	def POST (self, * uri, ** params):

		def toglispazi_startend(temp):
			temp=str(temp)
			if (len(temp)!=0):
				if (temp[-1]==" "):
					temp=temp[0:(len(temp))-1]
			if (len(temp)!=0):
				if (temp[0]==" "):
					temp=temp[1:(len(temp))]
			return (temp)
		print params


		username = params["Username"]
		password = params["Password"]
		username = toglispazi_startend(username)
		password = toglispazi_startend(password)
		physician_id = ""
		
		#---------------------------------------------------------------------------------------------------
		# GET REQUEST TO: http://localhost:8080/sitewhere/api/assets/categories/lista_medici_asset_ID/assets
		#---------------------------------------------------------------------------------------------------
		lista_medici = self.mySitewhere.get_assets_categoryID_assets(self.asset_med_id)
		print lista_medici
		if lista_medici != "error_string":
			dixt = json.loads(lista_medici)
			medici = dixt['results']
			flag = False

			for i in range(0,(len(medici))):
				if username == medici[i]["emailAddress"] and password == medici[i]["properties"]["password"]:
					physician_id = medici[i]["id"]
					print physician_id
					flag = True
					break


			if flag == True:
				response = json.dumps({"results":{"status":"login_succesful", "physician_id":physician_id}})
				return response
				#
			else:
				raise cherrypy.HTTPError(400, "wrong_params")
		else:
			raise cherrypy.HTTPError(400, "no_server")

	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass


class DiseaseServer(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]

	#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary

		
		
	def GET (self, *uri, **params):

		con = MongoClient()
		db = con[self.db_utils]
		collection = db.diseases #e' la collection
		#docu = spec.find() find non va bene perche' restituisce un oggetto pymongo.cursor.cursos
		docu = collection.find_one() #restituisce il dizionario 
		target = docu["diseases"]
		mydict = {"diseases": target}
		return json.dumps(mydict)
	

	def POST (self, * uri, ** params):

		pass

	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass


class SearchPatientServer(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]

	#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):
		pass

	def POST (self, * uri, ** params):
		print params
		
		search_name = params['patient_name']
		search_diseases = params['diseases']
		print "*********"
		print search_diseases
		

		selected = []
		
		#---------------------------------------------------------------------------------------------------
		# GET REQUEST TO: http://localhost:8080/sitewhere/api/assets/categories/PATIENT_LIST_asset_id/assets
		#---------------------------------------------------------------------------------------------------
		lista_pazienti = self.mySitewhere.get_assets_categoryID_assets(self.asset_pat_id)
		print lista_pazienti
		if lista_pazienti != "error_string":
			dixt = json.loads(lista_pazienti)
			for i in range(0,len(dixt['results'])):

				
				first_name = dixt['results'][i]['properties']['name']
				last_name = dixt['results'][i]['properties']['last name']
				str_diseases = dixt['results'][i]['properties']['diseases']
				diseases = json.loads(str_diseases)
				user_diseases = diseases["diseases_list"]
				#print json.dumps(user_diseases)
				
				name = first_name+" "+last_name
				#user_diseases = user_diseases.split(", ")
				print "*************"
				#print name
				#print user_diseases
				count = 0
				for k in range(0,len(user_diseases)):
					#print user_diseases[k]
					if user_diseases[k] in search_diseases:
						count = count+1
				
				#NON SO SE LA RICERCA FATTA IN QUESTO MODO
				#PER VEDERE SE FUNZIONA IL NUMERO DI PAZIENTI DEVE ESSERE ALTO
				#E CI DEVONO ESSERE ANCHE PAZIENTI CON LO STESSO NOME MA CON MALATTIE DIVERSE
				if count > 0 and len(search_name)==0:
					selected.append(dixt["results"][i])
				elif search_name in name and len(search_name)>0:
					selected.append(dixt["results"][i])
				elif search_name in name and count > 0 and len(search_name)>0:
					selected.append(dixt["results"][i])

			if len(selected) > 0:
				#print selected
				#print json.dumps(selected, indent=4, sort_keys=True)
				server_response = { "server_response": selected }
				server_response = json.dumps(server_response)
				#print server_response
				return server_response
			else:
				raise cherrypy.HTTPError(400, "no_selected")
		else:
			raise cherrypy.HTTPError(400, "no_server")

	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass

#---------------------------------------------------------------------------------------------------
# Classe per la gestione delle notifiche
# La classe gestisce gli alarms di Sitewhere come notifiche
# La GET prende gli alerts dei pazienti e li rende disponibili per il medico
# La POST crea un alert del medico, che altro non e' se non un messaggio per il paziente
#---------------------------------------------------------------------------------------------------
class Notifications(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]

		#giupe
		self.addr_alerts = self.my_dict["giupe"]["addr_alerts"]

	#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):
		# #------------------------------------------------------------------------------------------------------
		# # API di Giuseppe - La GET mi permette di scegliere tra allarmi visti o non visti
		# #------------------------------------------------------------------------------------------------------
		print params
		true_params = {"specs":{}}
		true_params.update(params)
		print true_params
		values = []
		#params={"physician_ID":"francesco-tolu-1881989", "api":"get_alerts_read_and_notread", "specs":{}}
		addr=self.addr_alerts
		sec=urllib.urlencode(true_params)
		######################################################################
		# Richiesta per sia gli allarmi letti e quelli non letti
		######################################################################
		if params["api"] == "get_alerts_read_and_notread":
			s=requests.Session()
			r=s.get(addr,params=sec, verify=False)
			print r.status_code
			if r.status_code==200:
				my_dict = json.loads(r.content)
				print json.dumps(my_dict, indent=4, sort_keys=True)
				read_alerts = my_dict["read"]
				not_read_alerts = my_dict["not_read"]
				#print json.dumps(read_alerts, indent=4, sort_keys=True)
				print "************************************************"
				#print json.dumps(not_read_alerts, indent=4, sort_keys=True)
				for i in range(0,len(not_read_alerts)):
					patient_name = not_read_alerts[i]["assetName"]
					event_date = not_read_alerts[i]["eventDate"]
					#elaborazione della data
					date_str = event_date.split("T")
					day_of_year = date_str[0]
					date_str2 = date_str[1]
					date_str2 = date_str2.split(".")
					time_of_day = date_str2[0]
					date = day_of_year+" "+time_of_day
					alert_id = not_read_alerts[i]["id"]
					alert_type = not_read_alerts[i]["type"]
					message = not_read_alerts[i]["message"]
					asset_id = not_read_alerts[i]["assetId"]
					assignment_token = not_read_alerts[i]["deviceAssignmentToken"]
					data = {
						"assetId": asset_id,
						"assetName": patient_name,
						"deviceAssignmentToken":assignment_token,
						"id":alert_id,
						"status":"false",
						"type":alert_type,
						"eventDate":date,
						"message":message
					}
					values.append(data)
				for i in range(0,len(read_alerts)):
					patient_name = read_alerts[i]["assetName"]
					event_date = read_alerts[i]["eventDate"]
					#elaborazione della data
					date_str = event_date.split("T")
					day_of_year = date_str[0]
					date_str2 = date_str[1]
					date_str2 = date_str2.split(".")
					time_of_day = date_str2[0]
					date = day_of_year+" "+time_of_day
					alert_id = read_alerts[i]["id"]
					alert_type = read_alerts[i]["type"]
					message = read_alerts[i]["message"]
					asset_id = read_alerts[i]["assetId"]
					assignment_token = read_alerts[i]["deviceAssignmentToken"]
					data = {
						"assetId": asset_id,
						"assetName": patient_name,
						"deviceAssignmentToken":assignment_token,
						"id":alert_id,
						"status":"true",
						"type":alert_type,
						"eventDate":date,
						"message":message
					}
					values.append(data)
				if len(values)>0:
					response = json.dumps({"results":values},indent=4, sort_keys=True)
					#print response
					return response
				else:
					raise cherrypy.HTTPError(400,"no_values")
			else:
				raise cherrypy.HTTPError(400,"error")
		######################################################################
		# Richiesta per avere gli allarmi non letti
		######################################################################
		if params["api"] == "get_list_of_not_read_alerts":
			s=requests.Session()
			r=s.get(addr,params=sec, verify=False)
			print r.status_code
			if r.status_code==200:
				my_dict = json.loads(r.content)
				print json.dumps(my_dict, indent=4, sort_keys=True)
				not_read_alerts = my_dict["not_read_alerts_list"]
				#print json.dumps(read_alerts, indent=4, sort_keys=True)
				print "************************************************"
				#print json.dumps(not_read_alerts, indent=4, sort_keys=True)
				for i in range(0,len(not_read_alerts)):
					patient_name = not_read_alerts[i]["assetName"]
					event_date = not_read_alerts[i]["eventDate"]
					#elaborazione della data
					date_str = event_date.split("T")
					day_of_year = date_str[0]
					date_str2 = date_str[1]
					date_str2 = date_str2.split(".")
					time_of_day = date_str2[0]
					date = day_of_year+" "+time_of_day
					alert_id = not_read_alerts[i]["id"]
					alert_type = not_read_alerts[i]["type"]
					message = not_read_alerts[i]["message"]
					asset_id = not_read_alerts[i]["assetId"]
					assignment_token = not_read_alerts[i]["deviceAssignmentToken"]
					data = {
						"assetId": asset_id,
						"assetName": patient_name,
						"deviceAssignmentToken":assignment_token,
						"id":alert_id,
						"status":"false",
						"type":alert_type,
						"eventDate":date,
						"message":message
					}
					values.append(data)
				if len(values)>0:
					response = json.dumps({"results":values},indent=4, sort_keys=True)
					#print response
					return response
				else:
					raise cherrypy.HTTPError(400,"no_values_not_read")
		else:
			raise cherrypy.HTTPError(400,"error")

				# for i in range(0,len(r)):
				# 	asset_id = r_dict[i]["assetId"]
				# 	asset_name = r_dict[i]["assetName"]
				# 	assignment_token = r_dict[i]["deviceAssignmentToken"]
				# 	alert_id = r_dict[i]["id"]

	def POST (self, * uri, ** params):
		# #------------------------------------------------------------------------------------------------------
		# # API di Giuseppe - La POST mi permette di cambiare lo stato di una notifica
		# # la richiesta (che e' una PUT al server di giuseppe) deve mandare questi parametri 
		# # params={"physician_ID":"francesco-tolu-1881989", "api":"change_alert_status", "specs":{"alert_id": "581cb277e4b07909421c69e3", "new_status": "not_read"}}
		# #------------------------------------------------------------------------------------------------------
		print params
		new_status = ""
		true_params = {"api":"change_alert_status","specs":{}}
		true_params.update({"physician_ID":str(params["physician_id"])})
		print type(true_params["physician_ID"])
		# if params["alert_status"]=="checked":
		# 	new_status = "not_read"
		# if params["alert_status"]=="not_checked":
		# 	new_status = "read"
		true_params["specs"].update({"alert_id": str(params["alert_id"]), "new_status": "switch"})
		print true_params
		addr=self.addr_alerts
		sec=urllib.urlencode(true_params)
		s=requests.Session()
		r=s.put(addr,params=sec, verify=False)
		print r.status_code
		
		if r.status_code == 200:
			return "good_request"
			print ("STATUS CODE:\t"+str(r.status_code))
			print ("\nMESSAGE:\t"+str(r.content))
		else:
			raise cherrypy.HTTPError(400,"error")
		# print ("STATUS CODE:\t"+str(r.status_code))
		# print ("\nMESSAGE:\t"+str(r.content))
		
				

	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass

#------------------------------------------------------------------------------------------------------------------------
# Classe di Test per leggere i dati relativi alla pressione
# La classe completa dovra' gestire poi tutte le letture su tutti i measurements e anche diario clinico e esami del sangue
# Nella post deve essere ricevuto come params anche l'intervallo di tempo che si vuole esplorare
#------------------------------------------------------------------------------------------------------------------------
class MeanValuesParametersWebService(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]

	#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):		
		pass
			
	def POST (self, * uri, ** params):

		def calcola_media(json_response):
			array = []
			dictionary = json.loads(json_response)
			entries = dictionary["entries"]
			if len(entries)>0:
				for j in range(0,len(entries)):
					value = entries[j]["value"]
					array.append(value)
				mean = float(sum(array)/len(array))
			else:
				return "-"
				

		dev_id = ""
		response_of_server = {}


		pat_id = params["id_pat"]
		print pat_id
		print self.asset_pat_id
		devices_ids = [
			"iHealt_OpenApiWeight_"+pat_id+"_REAL_DEVICE_ID",
			"iHealt_OpenApiSpO2_"+pat_id+"_REAL_DEVICE_ID",
			"iHealt_OpenApiBP_"+pat_id+"_REAL_DEVICE_ID",
			"iHealt_OpenApiBG_"+pat_id+"_REAL_DEVICE_ID",
			"iHealt_VirtualApiHeart_"+pat_id+"_REAL_DEVICE_ID"
		]
		
		####################################
		# GESTIONE DELLA DATA - ultimo mese
		####################################
		end_date_format_1st = datetime.date.today()
		margin = datetime.timedelta(days=31)
		end_date_1st = end_date_format_1st.strftime("%Y-%m-%d")
		end_date_1st_string = end_date_1st+"T00:00:00.000+0000"
		start_date_1st=end_date_format_1st-margin
		start_date_1st = start_date_1st.strftime("%Y-%m-%d")
		start_date_1st_string = start_date_1st+"T00:00:00.000+0000"
		####################################
		# GESTIONE DELLA DATA - ultimo mese
		####################################
		end_date_format_2nd = end_date_format_1st-margin
		end_date_2nd = end_date_format_2nd.strftime("%Y-%m-%d")
		end_date_2nd_string = end_date_2nd+"T00:00:00.000+0000"
		start_date_2nd=end_date_format_2nd-margin
		start_date_2nd = start_date_2nd.strftime("%Y-%m-%d")
		start_date_2nd_string = start_date_2nd+"T00:00:00.000+0000"

		
		#ricerca degli assignment token
		json_resp = self.mySitewhere.get_assignment_associated_with_asset(self.asset_pat_id,pat_id)
		#print json_resp
		if json_resp != "error_string":
			mydict = json.loads(json_resp)
			results = mydict["results"]
			if len(results)>0:
			#va a prendere gli assignments relativi ai parametri
				for k in range(0,len(results)):
					#fa un check su tutti gli assignment e poi va a prendere quelli di interesse
					if results[k]["deviceHardwareId"] in devices_ids:
						#check su ogni device di interesse
						if results[k]["deviceHardwareId"] == "iHealt_OpenApiBP_"+pat_id+"_REAL_DEVICE_ID":
							token = results[k]["token"]
							systolic_1st = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"systolic",start_date_1st_string,end_date_1st_string)
							mean_systolic_1st = calcola_media(systolic_1st)
							systolic_2nd = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"systolic",start_date_2nd_string,end_date_2nd_string)
							mean_systolic_2nd = calcola_media(systolic_2nd)
							response_of_server.update({"systolic":{"1st_month":mean_systolic_1st,"2nd_month":mean_systolic_2nd}})
							diastolic_1st = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"diastolic",start_date_1st_string,end_date_1st_string)
							mean_diastolic_1st = calcola_media(diastolic_1st)
							diastolic_2nd = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"diastolic",start_date_2nd_string,end_date_2nd_string)
							mean_diastolic_2nd = calcola_media(diastolic_2nd)
							response_of_server.update({"diastolic":{"1st_month":mean_diastolic_1st,"2nd_month":mean_diastolic_2nd}})
						elif results[k]["deviceHardwareId"] == "iHealt_OpenApiBG_"+pat_id+"_REAL_DEVICE_ID":
							token = results[k]["token"]
							meas = self.mySitewhere.get_meaurements_by_assignment_token(token)
							#NB DA CAMBIARE
							response_of_server.update({"glicemia":{"1st_month":10000,"2nd_month":10000}})
							#NON CI SONO MISURE DI GLUCOSIO PER ORA						
						elif results[k]["deviceHardwareId"] == "iHealt_OpenApiSpO2_"+pat_id+"_REAL_DEVICE_ID":
							token = results[k]["token"]
							#per il check delle key dei valori
							#meas = self.mySitewhere.get_meaurements_by_assignment_token(token)
							#print meas
							blood_oxygen_1st = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"blood_oxygen_value",start_date_1st_string,end_date_1st_string)
							mean_blood_oxygen_1st = calcola_media(blood_oxygen_1st)
							blood_oxygen_2nd = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"blood_oxygen_value",start_date_2nd_string,end_date_2nd_string)
							mean_blood_oxygen_2nd = calcola_media(blood_oxygen_2nd)
							response_of_server.update({"blood_oxygen":{"1st_month":mean_blood_oxygen_1st,"2nd_month":mean_blood_oxygen_2nd}})
						elif results[k]["deviceHardwareId"] == "iHealt_VirtualApiHeart_"+pat_id+"_REAL_DEVICE_ID":
							token = results[k]["token"]
							#meas = self.mySitewhere.get_meaurements_by_assignment_token(token)
							#print meas
							heart_rate_1st = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"heart_rate",start_date_1st_string,end_date_1st_string)
							mean_heart_rate_1st = calcola_media(heart_rate_1st)
							heart_rate_2nd = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"heart_rate",start_date_2nd_string,end_date_2nd_string)
							mean_heart_rate_2nd = calcola_media(heart_rate_2nd)
							response_of_server.update({"heart_rate":{"1st_month":mean_heart_rate_1st,"2nd_month":mean_heart_rate_2nd}})
						elif results[k]["deviceHardwareId"] == "iHealt_OpenApiWeight_"+pat_id+"_REAL_DEVICE_ID":
							token = results[k]["token"]
							#meas = self.mySitewhere.get_meaurements_by_assignment_token(token)
							#print meas
							#peso
							weight_1st = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"weight",start_date_1st_string,end_date_1st_string)
							mean_weight_1st = calcola_media(weight_1st)
							weight_2nd = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"weight",start_date_2nd_string,end_date_2nd_string)
							mean_weight_2nd = calcola_media(weight_2nd)
							response_of_server.update({"weight":{"1st_month":mean_weight_1st,"2nd_month":mean_weight_2nd}})
							#bmi
							BMI_1st = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"BMI",start_date_1st_string,end_date_1st_string)
							mean_BMI_1st = calcola_media(BMI_1st)
							BMI_2nd = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"BMI",start_date_2nd_string,end_date_2nd_string)
							mean_BMI_2nd = calcola_media(BMI_2nd)
							response_of_server.update({"BMI":{"1st_month":mean_BMI_1st,"2nd_month":mean_BMI_2nd}})
							#massa magra
							fat_level_1st = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"fat_level",start_date_1st_string,end_date_1st_string)
							mean_fat_level_1st = calcola_media(fat_level_1st)
							fat_level_2nd = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"fat_level",start_date_2nd_string,end_date_2nd_string)
							mean_fat_level_2nd = calcola_media(fat_level_2nd)
							response_of_server.update({"fat_level":{"1st_month":mean_fat_level_1st,"2nd_month":mean_fat_level_2nd}})
							#grasso corporeo
							body_fat_1st = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"body_fat",start_date_1st_string,end_date_1st_string)
							mean_body_fat_1st = calcola_media(body_fat_1st)
							body_fat_2nd = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"body_fat",start_date_2nd_string,end_date_2nd_string)
							mean_body_fat_2nd = calcola_media(body_fat_2nd)
							response_of_server.update({"body_fat":{"1st_month":mean_body_fat_1st,"2nd_month":mean_body_fat_2nd}})
							#acqua corporea
							body_water_1st = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"body_water",start_date_1st_string,end_date_1st_string)
							mean_body_water_1st = calcola_media(body_water_1st)
							body_water_2nd = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"body_water",start_date_2nd_string,end_date_2nd_string)
							mean_body_water_2nd = calcola_media(body_water_2nd)
							response_of_server.update({"body_water":{"1st_month":mean_body_water_1st,"2nd_month":mean_body_water_2nd}})
							#massa muscolare
							muscle_weight_1st = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"muscle_weight",start_date_1st_string,end_date_1st_string)
							mean_muscle_weight_1st = calcola_media(muscle_weight_1st)
							muscle_weight_2nd = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"muscle_weight",start_date_2nd_string,end_date_2nd_string)
							mean_muscle_weight_2nd = calcola_media(muscle_weight_2nd)
							response_of_server.update({"muscle_weight":{"1st_month":mean_muscle_weight_1st,"2nd_month":mean_muscle_weight_2nd}})
							#massa ossea
							bone_value_1st = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"bone_value",start_date_1st_string,end_date_1st_string)
							mean_bone_value_1st = calcola_media(bone_value_1st)
							bone_value_2nd = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"bone_value",start_date_2nd_string,end_date_2nd_string)
							mean_bone_value_2nd = calcola_media(bone_value_2nd)
							response_of_server.update({"bone_value":{"1st_month":mean_bone_value_1st,"2nd_month":mean_bone_value_2nd}})


				print json.dumps({"results":response_of_server},indent=4, sort_keys=True)
				return json.dumps({"results":response_of_server})
			else:
				raise cherrypy.HTTPError(400,"no_device")
		else:
			raise cherrypy.HTTPError(400,"error")
		

	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass


class PointValuesParametersWebService(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]

	#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):		
		pass
			
	def POST (self, * uri, ** params):
		def trova_valori_puntuali(json_response):
			array = []
			dictionary = json.loads(json_response)
			entries = dictionary["entries"]
			if len(entries)>0:
				for j in range(0,len(entries)):
					value = entries[j]["value"]
					date_str = entries[j]["measurementDate"]
					date_str = date_str.split("T")
					day_of_year = date_str[0]
					date_str2 = date_str[1]
					date_str2 = date_str2.split(".")
					date_str2 = date_str2[0].split(":")
					time_of_day = date_str2[0]+":"+date_str2[1]
					object_dict = {"value":value,"measurementDate":time_of_day}
					array.append(object_dict)
				return array
			else:
				return {}

		print params

		response_of_server = {}

		dev_id=""
		pat_id = params["id_pat"]
		print pat_id
		print self.asset_pat_id
		devices_ids = [
			"iHealt_OpenApiWeight_"+pat_id+"_REAL_DEVICE_ID",
			"iHealt_OpenApiSpO2_"+pat_id+"_REAL_DEVICE_ID",
			"iHealt_OpenApiBP_"+pat_id+"_REAL_DEVICE_ID",
			"iHealt_OpenApiBG_"+pat_id+"_REAL_DEVICE_ID",
			"iHealt_VirtualApiHeart_"+pat_id+"_REAL_DEVICE_ID"
		]
		
		date_str = params["date"]
		values = {}

		if date_str != "":
			#print date_str
			###### Per cercare i valori delle misure relative a una giornata cerco nell'intervallo
			###### temporale tra le 00:00 del giorno cercato e le 00:00 del giorno dopo
			from_date_object = datetime.datetime.strptime(date_str, '%d-%m-%Y')
			margin = datetime.timedelta(days = 1)
			to_date_object = from_date_object+margin
			#print from_date_object
			#print to_date_object
			from_date_str = datetime.datetime.strftime(from_date_object,'%Y-%m-%d')+"T00:00:00.000+0000"
			to_date_str = datetime.datetime.strftime(to_date_object,'%Y-%m-%d')+"T00:00:00.000+0000"
			print from_date_str
			print to_date_str

			#ricerca degli assignment token
			json_resp = self.mySitewhere.get_assignment_associated_with_asset(self.asset_pat_id,pat_id)
			#print json_resp
			if json_resp != "error_string":
				mydict = json.loads(json_resp)
				results = mydict["results"]
				if len(results)>0:
					#va a prendere gli assignments relativi ai parametri
					for k in range(0,len(results)):
						#fa un check su tutti gli assignment e poi va a prendere quelli di interesse
						if results[k]["deviceHardwareId"] in devices_ids:
							#check su ogni device di interesse
							if results[k]["deviceHardwareId"] == "iHealt_OpenApiBP_"+pat_id+"_REAL_DEVICE_ID":
								token = results[k]["token"]
								valori_sist = []
								valori_diast = []
								systolic = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"systolic",from_date_str,to_date_str)
								diastolic = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"diastolic",from_date_str,to_date_str)
								valori_sist = trova_valori_puntuali(systolic)
								valori_diast = trova_valori_puntuali(diastolic)
								values.update({"systolic":valori_sist,"diastolic":valori_diast})
														
					# 		elif results[k]["deviceHardwareId"] == "iHealt_OpenApiBG_"+pat_id+"_REAL_DEVICE_ID":
					# 			token = results[k]["token"]
					# 			meas = self.mySitewhere.get_meaurements_by_assignment_token(token)
					# 			print meas
					# 			#NON CI SONO MISURE DI GLUCOSIO PER ORA						
							elif results[k]["deviceHardwareId"] == "iHealt_OpenApiSpO2_"+pat_id+"_REAL_DEVICE_ID":
								token = results[k]["token"]
								valori_spo2 = []
								blood_oxygen = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"blood_oxygen_value",from_date_str,to_date_str)
								valori_spo2 = trova_valori_puntuali(blood_oxygen)
								values.update({"spo2":valori_spo2})
							elif results[k]["deviceHardwareId"] == "iHealt_VirtualApiHeart_"+pat_id+"_REAL_DEVICE_ID":
								token = results[k]["token"]
								valori_hr = []
								heart_rate = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"heart_rate",from_date_str,to_date_str)
								valori_hr = trova_valori_puntuali(heart_rate)
								values.update({"heart_rate":valori_hr})
					# 		elif results[k]["deviceHardwareId"] == "iHealt_OpenApiWeight_"+pat_id+"_REAL_DEVICE_ID":
					# 			token = results[k]["token"]
					# 			#meas = self.mySitewhere.get_meaurements_by_assignment_token(token)
					# 			#print meas
					# 			#peso
					# 			weight = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"weight",from_date_str_string,to_date_str_string)
					# 			#bmi
					# 			BMI = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"BMI",from_date_str_string,to_date_str_string)
					# 			#massa magra
					# 			fat_level = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"fat_level",from_date_str_string,to_date_str_string)
					# 			#grasso corporeo
					# 			body_fat = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"body_fat",from_date_str_string,to_date_str_string)
					# 			#acqua corporea
					# 			body_water = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"body_water",from_date_str_string,to_date_str_string)
					# 			#massa muscolare
					# 			muscle_weight = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"muscle_weight",from_date_str_string,to_date_str_string)
					# 			#massa ossea
					# 			bone_value = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,"bone_value",from_date_str_string,to_date_str_string)					
					# return json.dumps(response_of_server)
					print json.dumps(values,indent=4, sort_keys=True)
					return json.dumps(values)

				else:
					raise cherrypy.HTTPError(400,"no_device")
			else:
				raise cherrypy.HTTPError(400,"error")
		else:
			raise cherrypy.HTTPError(400,"no_date")


	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass


#------------------------------------------------------------------------------------------------------------------------
# Classe di Test mandare i dati utili per i grafici
#------------------------------------------------------------------------------------------------------------------------
class GraphParametersWebService(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]

	#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):
		pass
			
	def POST (self, * uri, ** params):
		def trova_valori(json_response):
			array = []
			dictionary = json.loads(json_response)
			entries = dictionary["entries"]
			if len(entries)>0:
				for j in range(0,len(entries)):
					value = entries[j]["value"]
					date_str = entries[j]["measurementDate"]
					date_str = date_str.split("T")
					day_of_year = date_str[0]
					date_str2 = date_str[1]
					date_str2 = date_str2.split(".")
					time_of_day = date_str2[0]
					date = day_of_year+" "+time_of_day
					object_dict = {"value":value,"measurementDate":date}
					array.append(object_dict)
				return array
			else:
				return {}

				


		values = []
		#initialization
		dev_id = ""
		print params
		pat_id = params["id_pat"]
		parametro = params["param_id"]
		interval_duration = params["interval_duration"]
		#check on the parameter for choosing the device
		if parametro=="systolic" or parametro == "diastolic":
			dev_id = "iHealt_OpenApiBP_"+pat_id+"_REAL_DEVICE_ID"
		#non ci sono valori di glucosio per il momento, quindi le chiavi non le conosco
		elif parametro == "glic":
			dev_id = "iHealt_OpenApiBG_"+pat_id+"_REAL_DEVICE_ID"
		elif parametro == "blood_oxygen_value":
			dev_id = "iHealt_OpenApiSpO2_"+pat_id+"_REAL_DEVICE_ID"
		elif parametro == "weight":
			dev_id = "iHealt_OpenApiWeight_"+pat_id+"_REAL_DEVICE_ID"
		elif parametro == "heart_rate":
			dev_id = "iHealt_VirtualApiHeart_"+pat_id+"_REAL_DEVICE_ID"
		########################################
		# GESTIONE DELLA DATA
		########################################
		if interval_duration=="one_week":
			days = 7
		elif interval_duration == "two_weeks":
			days = 15
		elif interval_duration == "one_month":
			days = 30
		elif interval_duration == "two_months":
			days = 60
		margin = datetime.timedelta(days = days)
		end_date_format = datetime.date.today()
		end_date = end_date_format.strftime("%Y-%m-%d")
		end_date_string = end_date+"T00:00:00.000+0000"
		start_date_format=end_date_format-margin
		start_date = start_date_format.strftime("%Y-%m-%d")
		start_date_string = start_date+"T00:00:00.000+0000"
		print start_date_string
		print end_date_string

		#iddevices
		devices_ids = [
			"iHealt_OpenApiWeight_"+pat_id+"_REAL_DEVICE_ID",
			"iHealt_OpenApiSpO2_"+pat_id+"_REAL_DEVICE_ID",
			"iHealt_OpenApiBP_"+pat_id+"_REAL_DEVICE_ID",
			"iHealt_OpenApiBG_"+pat_id+"_REAL_DEVICE_ID",
			"iHealt_VirtualApiHeart_"+pat_id+"_REAL_DEVICE_ID"
		]

		#Se il dev id e' vuoto vuol dire che quel paziente non ha ancora associati i device iHealth
		
		#ricerca degli assignment token
		json_resp = self.mySitewhere.get_assignment_associated_with_asset(self.asset_pat_id,pat_id)
		#print json_resp
		if json_resp != "error_string":
			mydict = json.loads(json_resp)
			results = mydict["results"]
			if len(results>0):
				#va a prendere gli assignments relativi ai parametri
				for k in range(0,len(results)):
					#fa un check su tutti gli assignment e poi va a prendere quelli di interesse
					if results[k]["deviceHardwareId"] in devices_ids:
						#check su ogni device di interesse
						if results[k]["deviceHardwareId"] == dev_id:
							token = results[k]["token"]							
							sitewhere_response = self.mySitewhere.get_measurements_series_by_assignment_token_measurementID(token,parametro,start_date_string,end_date_string)
							#print sitewhere_response
							values = trova_valori(sitewhere_response)
							break
				if values != "empty":
					results = {"results":values}
					print json.dumps(results, indent=4, sort_keys=True)
					print len(values)
					return json.dumps(results)
				else:
					raise cherrypy.HTTPError(400,"empty")
			else:
				raise cherrypy.HTTPError(400,"no_device")
		else:
			raise cherrypy.HTTPError(400,"error")
	
		
							

	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass

class PhysicianMessageManagerWebService(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]

		#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):
		pass
				
		
	def POST (self, * uri, ** params):
		
		print params
		pat_id = params["pat_id"]		
		message = params["message"]
		physician_id = params["physician_id"]
		metadata = {"patient_id":pat_id,"is_message":"yes"}
		alert_type = "phy-message"
		assignment_token = ""

		#RICERCA DELL'ASSIGNMENT TOKEN
		dev_phy_id = physician_id+"-Android-App"
		assignments_for_phy_sitewhere = self.mySitewhere.get_assignment_associated_with_asset(self.asset_med_id,physician_id)
		if assignments_for_phy_sitewhere != "error_string":
			dixt = json.loads(assignments_for_phy_sitewhere)
			assignment_list = dixt['results']
			flag = False
			for i in range(0,(len(assignment_list))):
				if assignment_list[i]["deviceHardwareId"]==dev_phy_id:
					assignment_token = assignment_list[i]["token"]
					flag = True
					break
			#INVIO DELL'ALERT A SITEWHERE DOPO AVER RICEVUTO UN MESSAGGIO COME STRINGA DALL'APPLICAZIONE
			request = self.mySitewhere.send_alert_assign_token(assignment_token, message, alert_type, metadata)
			if request != "error_string":
				print request
				return "good request"
			else:
				raise cherrypy.HTTPError(400,"error")
		else:
				raise cherrypy.HTTPError(400,"error")
				
	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass

#----------------------------------------------------------------------------------------------------------------------------
# Classe per la gestione dei dati del diario clinico.
# La POST riceve come parametri l'id del paziente e la data in cui si vuole vedere il diario clinico. L'id del diario
# clinico del paziente viene creato in automatico perche' si presume sia sempre lo stesso, ovvero id-paziente-diario-clinico.
# SE FOSSE SU SITEWHERE -> Una volta ricevuti i parametri nella POST viene richiamata una GET a sitewhere per ottenere tutti gli assignments fatti per
# quel site, e si va a cercare il token dell'assignment che ha come hardwareID il diario clinico e come assetID quello del 
# paziente(deve essere uguale a quello ricevuto come param). Una volta trovato il token ci sara' un ulteriore GET, questa 
# volta per cercare i measurements che stanno sotto quel token e che sono stati fatti in quella data passata nei params.
# Questo stesso iter dovrebbe essere seguito per i dati relativi agli esami del sangue. 
# SICCOME NON E' SU SITEWHERE -> si va direttamente a interrogare mongo
#----------------------------------------------------------------------------------------------------------------------------

class DiaryDpWebService(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_dialysis_diary = self.my_dict["mongo"]["db_dialysis_diary"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]


		#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):
		pass
		
	def POST (self, * uri, ** params):

		print params
		pat_id = params["pat_id"] #da mandare con l'applicazione
		values = []
		#VALUTARE SE E' UTILE UN PARAMETRO PER DISCRIMINARE TRA DIALISI PERITONEALE E EMODIALISI. Credo che sia la 
		client = MongoClient()
		client = MongoClient('localhost', 27017)
		db = client[self.db_dialysis_diary]
		collection = db['dp_diaries']
		#events = collection.find()
		measurements_dp = collection.find({'userId':pat_id})
		print measurements_dp
		for k in measurements_dp:
			print "*************"
			#print k
			#print k["request"]["eventDate"]
			#print k["request"]["measurements"]
			date_str = k["request"]["eventDate"]
			#print date_str
			measurements = k["request"]["measurements"]
			#DATA IN UN FORMATO COMODO DA LEGGERE
			date_str = date_str.split("T")
			day_of_year = date_str[0]
			date_str2 = date_str[1]
			date_str2 = date_str2.split(".")
			time_of_day = date_str2[0]
			date = day_of_year+" "+time_of_day
			json_object = {"eventDate":date,"measurements":measurements}
			values.append(json_object)
		values = values[::-1]
		if len(values)>0:
			response = {"results":values}
			print json.dumps(response,indent=4, sort_keys=True)
			return json.dumps(response)
		else:
			raise cherrypy.HTTPError(400,"no_values")

		


			
	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass


##########################################################################################################
#GESTIONE DEL DIARIO CLINICO DELL'EMODIALISI
#########################################################################################################
class DiaryEMOWebService(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_dialysis_diary = self.my_dict["mongo"]["db_dialysis_diary"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]


		#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):
		pass
				
		
	def POST (self, * uri, ** params):

		print params
		pat_id = params["pat_id"] #da mandare con l'applicazione
		values = []
		#VALUTARE SE E' UTILE UN PARAMETRO PER DISCRIMINARE TRA DIALISI PERITONEALE E EMODIALISI. Credo che sia la 
		client = MongoClient()
		client = MongoClient('localhost', 27017)
		db = client[self.db_dialysis_diary]
		collection = db['dp_diaries']
		#events = collection.find()
		measurements_dp = collection.find({'userId':pat_id})
		print measurements_dp
		for k in measurements_dp:
			print "*************"
			#print k
			#print k["request"]["eventDate"]
			#print k["request"]["measurements"]
			date_str = k["request"]["eventDate"]
			#print date_str
			measurements = k["request"]["measurements"]
			#DATA IN UN FORMATO COMODO DA LEGGERE
			date_str = date_str.split("T")
			day_of_year = date_str[0]
			date_str2 = date_str[1]
			date_str2 = date_str2.split(".")
			time_of_day = date_str2[0]
			date = day_of_year+" "+time_of_day
			json_object = {"eventDate":date,"measurements":measurements}
			values.append(json_object)
		if len(values)>0:
			response = {"results":values}
			print json.dumps(response)
			return json.dumps(response)
		else:
			raise cherrypy.HTTPError(400,"no_values")
		
		


			
	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass


#----------------------------------------------------------------------------------------------------------------------------
# Classe di Test per la gestione dei dati degli esami del sangue
# GET utilizzata per il test
# la POST prendera' come params l'id del paziente e la data
#----------------------------------------------------------------------------------------------------------------------------

class BloodAnalysisWebServices(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_dialysis_diary = self.my_dict["mongo"]["db_dialysis_diary"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]


		#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):
		pass
				
		
	def POST (self, * uri, ** params):

		print params
		pat_id = params["pat_id"] #da mandare con l'applicazione
		values = []
		client = MongoClient()
		client = MongoClient('localhost', 27017)
		db = client[self.db_dialysis_diary]
		collection = db['blood_test_diaries']
		#events = collection.find()
		measurements_dp = collection.find({'userId':pat_id})
		print measurements_dp
		for k in measurements_dp:
			print "*************"
			value_object = []
			date_str = k["request"]["eventDate"]
			measurements = k["request"]["measurements"]
			#iterazione key-value
			for key in measurements.keys():
				print str(key)
				print measurements[key]
				key_value = {"key": str(key),"value":str(measurements[key])}
				value_object.append(key_value)
			#DATA IN UN FORMATO COMODO DA LEGGERE
			date_str = date_str.split("T")
			day_of_year = date_str[0]
			date_str2 = date_str[1]
			date_str2 = date_str2.split(".")
			time_of_day = date_str2[0]
			date = day_of_year+" "+time_of_day
			json_object = {"eventDate":date,"measurements":value_object}
			
			values.append(json_object)
		values = values[::-1]
		if len(values)>0:
			response = {"results":values}
			print json.dumps(response, indent=4, sort_keys=True)
			return json.dumps(response)
		else:
			raise cherrypy.HTTPError(400,"no_values")
			
	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass

class UrinAnalysisProvider(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_dialysis_diary = self.my_dict["mongo"]["db_dialysis_diary"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]


		#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):
		#GET PER IL TESTING
		pass
		
	def POST (self, * uri, ** params):


		values = []

		print params
		pat_id = params["pat_id"] #da mandare con l'applicazione
		client = MongoClient()
		client = MongoClient('localhost', 27017)
		db = client["urinanalysis"] #valore da mettere nel conf
		collection = db[pat_id]
		analysis = collection.find()
		for k in analysis:
			measurements = k["measurements"]
			print k["measurements"]["blo"]
			manufacturer = k["manufacturer"]
			date = k["date"]
			item = {"measurements":measurements, "date":str(date),"manufacturer":manufacturer}
			values.append(item)
		values = values[::-1]
		if len(values)>0:
			response = {"results":values}
			print json.dumps(response)
			return json.dumps(response)
		else:
			raise cherrypy.HTTPError(400,"no_values")

		


			
	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass

####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################
####################################################################################################################################################################
# TEST SERVER PER IL CORRETTO FUNZIONAMENTO DEI PARAMETRI ##########################################################################################################

class TESTSERVERPARAMETRI(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.auth=(self.my_dict["sitewhere"]["auth"]["username"], self.my_dict["sitewhere"]["auth"]["password"])

		#In realta' la riga sotto non e' necessaria perche' e' inclusa in ogni metodo della classe SitewhereManager
		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.mySitewhere = SitewhereManager(self.url, self.tenant_token, self.auth)

		#SITES
		self.pat_site_token = self.my_dict["sitewhere"]["sites"]["pat_site_token"]
		self.med_site_token = self.my_dict["sitewhere"]["sites"]["med_site_token"]
		

		#ASSET DEVICE
		self.device_asset_id = self.my_dict["sitewhere"]["assets"]["device_asset_id"]

		#ASSET MEDICI PROPERTIES
		self.asset_med_id= self.my_dict["sitewhere"]["assets"]["med_asset_id"]
		self.asset_med_name= self.my_dict["sitewhere"]["assets"]["med_asset_name"]
		self.asset_app_id= self.my_dict["sitewhere"]["assets"]["app_asset_id"]
		self.app_specification_token = self.my_dict["sitewhere"]["tokens"]["app_specification_token"]

		#ASSET PAZIENTI PROPERTIES
		self.asset_pat_id= self.my_dict["sitewhere"]["assets"]["pat_asset_id"]
		self.asset_pat_name= self.my_dict["sitewhere"]["assets"]["pat_asset_name"]

		

		#DataBase
		self.db_sitewhere = self.my_dict["mongo"]["db_sitewhere"]
		self.db_dialysis_diary = self.my_dict["mongo"]["db_dialysis_diary"]
		self.db_utils = self.my_dict["mongo"]["db_utils"]


		#To read config_file
	def get_config_file(self):
		myfile = open("config2.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):
		#GET PER IL TESTING
		pass
		
	def POST (self, * uri, ** params):
		print params
		if uri[0] == "grafico":
			values = [
				{
					"measurementDate":"2016-11-14",
					"value":123
					},
				{
					"measurementDate":"2016-11-13",
					"value":126
					},
				{
					"measurementDate":"2016-11-12",
					"value":132
					},
				{
					"measurementDate":"2016-11-11",
					"value":123
					},
				
				{
					"measurementDate":"2016-11-10",
					"value":118
					},
				{
					"measurementDate":"2016-11-9",
					"value":123
					},
				{
					"measurementDate":"2016-11-8",
					"value":126
					},
				{
					"measurementDate":"2016-11-7",
					"value":132
					},
				{
					"measurementDate":"2016-11-6",
					"value":120
					},
				{
					"measurementDate":"2016-11-5",
					"value":118
					},

				{
					"measurementDate":"2016-11-4",
					"value":123
					},
				{
					"measurementDate":"2016-11-3",
					"value":126
					},
				{
					"measurementDate":"2016-11-2",
					"value":132
					},
				{
					"measurementDate":"2016-11-1",
					"value":120
					},
				{
					"measurementDate":"2016-10-27",
					"value":118
					},
				{
					"measurementDate":"2016-10-24",
					"value":123
					},
				{
					"measurementDate":"2016-10-22",
					"value":126
					},
				{
					"measurementDate":"2016-10-4",
					"value":132
					},
				{
					"measurementDate":"2016-10-3",
					"value":120
					},
				{
					"measurementDate":"2016-10-2",
					"value":118
					}
			]
			print json.dumps({"results":values})
			return json.dumps({"results":values})
			

		elif uri[0] == "valori_medi":
			data ={	"BMI": {
							"1st_month": "43",
							"2nd_month": "-"
						},
						"blood_oxygen": {
							"1st_month": "43",
							 "2nd_month": "-"
						},
						"body_fat": {
							"1st_month": "43",
							"2nd_month": "-"
						},
						"body_water": {
							"1st_month": "43",
							"2nd_month": "-"
						},
						"bone_value": {
							"1st_month": "43",
							"2nd_month": "-"
						},
						"diastolic": {
							"1st_month": "43",
							"2nd_month": "-"
						},
						"fat_level": {
							"1st_month": "43",
							"2nd_month": "-"
						},
						"glicemia": {
							"1st_month": "10000",
							"2nd_month": "10000"
						},
						"heart_rate": {
							"1st_month": "43",
							"2nd_month": "-"
						},
						"muscle_weight": {
							"1st_month": "43",
							"2nd_month": "-"
						},
				        "systolic": {
							"1st_month": "43",
							"2nd_month": "-"
						},
						"weight": {
							"1st_month": "43",
							"2nd_month": "-"
						}
					}
				
			print json.dumps(data,indent=4, sort_keys=True)
			return json.dumps(data)
		

	def PUT (self, * uri, ** params):
		pass

	def DELETE (self, * uri, ** params):
		pass




if __name__ == '__main__': 
	
	conf = {
		'/': {
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
			'tools.sessions.on': True, 
		}
	}
	cherrypy.tree.mount (RegistrationServer(),	'/registration',	conf)
	cherrypy.tree.mount (AuthenticationServer(),	'/authentication',	conf)
	cherrypy.tree.mount (DiseaseServer(),	'/diseases',	conf)
	cherrypy.tree.mount (SearchPatientServer(),	'/searchPatient',	conf)
	cherrypy.tree.mount (Notifications(), '/notifications', conf)
	cherrypy.tree.mount (MeanValuesParametersWebService(), '/api/parameters/meanvalues', conf)
	cherrypy.tree.mount (PointValuesParametersWebService(), '/api/parameters/pointvalues', conf)
	cherrypy.tree.mount (GraphParametersWebService(), 'api/parameters/graphs', conf)
	cherrypy.tree.mount (DiaryDpWebService(), '/api/diaryDp', conf)	
	cherrypy.tree.mount (UrinAnalysisProvider(), '/api/urinanalysis',conf)
	cherrypy.tree.mount (BloodAnalysisWebServices(), '/api/bloodanalysis',conf)
	cherrypy.tree.mount (PhysicianMessageManagerWebService(), '/api/messagefromphysician',conf)
	###########################################################################################
	cherrypy.tree.mount (TESTSERVERPARAMETRI(),'/test_parametri',conf)
	cherrypy.server.socket_host = '192.168.137.1'
	cherrypy.config.update({'server.socket_port':9090})
	cherrypy.engine.start()	
	cherrypy.engine.block()
