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

class RegistrationServer(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.tenant_id=self.my_dict["sitewhere"]["tenant_id"]
		self.tenant_name=self.my_dict["sitewhere"]["tenant_name"]
		self.tenant_logo=self.my_dict["sitewhere"]["tenant_logo"]
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
		myfile = open("config.json","r")
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
		self.tenant_id=self.my_dict["sitewhere"]["tenant_id"]
		self.tenant_name=self.my_dict["sitewhere"]["tenant_name"]
		self.tenant_logo=self.my_dict["sitewhere"]["tenant_logo"]
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
		myfile = open("config.json","r")
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
		
		#---------------------------------------------------------------------------------------------------
		# GET REQUEST TO: http://localhost:8080/sitewhere/api/assets/categories/lista_medici_asset_ID/assets
		#---------------------------------------------------------------------------------------------------
		lista_medici = self.mySitewhere.get_assets_categoryID_assets(self.asset_med_id)
		#print lista_medici
		if lista_medici != "error_string":
			dixt = json.loads(lista_medici)
			medici = dixt['results']
			flag = False

			for i in range(0,(len(medici))):
				if username == medici[i]["emailAddress"] and password == medici[i]["properties"]["password"]:
					flag = True
					break

			if flag == True:
				return "login_succesful"
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
		self.tenant_id=self.my_dict["sitewhere"]["tenant_id"]
		self.tenant_name=self.my_dict["sitewhere"]["tenant_name"]
		self.tenant_logo=self.my_dict["sitewhere"]["tenant_logo"]
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
		myfile = open("config.json","r")
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
		self.tenant_id=self.my_dict["sitewhere"]["tenant_id"]
		self.tenant_name=self.my_dict["sitewhere"]["tenant_name"]
		self.tenant_logo=self.my_dict["sitewhere"]["tenant_logo"]
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
		myfile = open("config.json","r")
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
				name = first_name+" "+last_name
				#user_diseases = user_diseases.split(", ")
				print "*************"
				print name
				print user_diseases
				count = 0
				for k in range(0,len(user_diseases)):
					print user_diseases[k]
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
		self.tenant_id=self.my_dict["sitewhere"]["tenant_id"]
		self.tenant_name=self.my_dict["sitewhere"]["tenant_name"]
		self.tenant_logo=self.my_dict["sitewhere"]["tenant_logo"]
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
		myfile = open("config.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):

		#------------------------------------------------------------------------------------------------------
		# GET REQUEST TO: http://localhost:8080/sitewhere/api/sites/de7397e2-3855-4f4f-a8fd-d4c7ccd67823/alerts
		#------------------------------------------------------------------------------------------------------
		notifiche = []
		request = self.mySitewhere.get_alerts_for_sites(self.pat_site_token)
		print request
		if request != "error_string":
			print request
			mydict = json.loads(request)
			#print mydict
			results = mydict["results"]
			for i in range(0,len(results)):
				asset_id = results[i]["assetId"]
				asset_name = results[i]["assetName"]
				assignment_token = results[i]["deviceAssignmentToken"]
				alert_id = results[i]["id"]
				if len(results[i]["metadata"])==0:
					alert_status = ""
				else:
					alert_status = results[i]["metadata"]["is_read"]
				alert_type = results[i]["type"]
				print alert_status
				print type(alert_status)
				#NB IL FORMATO DELLA DATA E' DA CAMBIARE
				event_date = results[i]["eventDate"]
				alert_message = results[i]["message"]
				data = {
					"assetId": asset_id,
					"assetName": asset_name,
					"deviceAssignmentToken":assignment_token,
					"id":alert_id,
					"status":alert_status,
					"type":alert_type,
					"eventDate":event_date,
					"message":alert_message
				}
				notifiche.append(data)
			response = json.dumps({"results":notifiche},indent=4, sort_keys=True)
			print response
			return response

			
		else:
			raise cherrypy.HTTPError(400, "Error")
			
		

	def POST (self, * uri, ** params):
		#---------------------------------------------------------------------------------------------------------
		#Parte per modificare lo stato di una notifica, cioe' se e' stata letta o no. Siccome e' impossibile 
		#modificare dati su sitewhere, per far si che lo stato di lettura della notifica venga salvato anche su 
		#sitewhere si utilizza un valore nei metadata con chiave 'is_read' e lo si modifica direttamente da mongo
		#---------------------------------------------------------------------------------------------------------
		print params
		alert_id = params["alert_id"]
		alert_status = params["alert_status"]
		client = MongoClient()
		client = MongoClient('localhost', 27017)
		db = client[self.db_sitewhere]
		collection = db['events']
		#events = collection.find()
		event = collection.find_one({'_id':ObjectId(str(alert_id))})
		#print event
		if alert_status == "checked":
			collection.update({'_id':ObjectId(str(alert_id))},{'$set': {'metadata.is_read':'true'}})
			print "*********"
			print event
					
		elif alert_status == "not_checked":
			collection.update({'_id':ObjectId(str(alert_id))},{'$set': {'metadata.is_read':'false'}})
			print "*************"
			print event
		else:
			pass
			
				

	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass

#------------------------------------------------------------------------------------------------------------------------
# Classe di Test per leggere i dati relativi alla pressione
# La classe completa dovra' gestire poi tutte le letture su tutti i measurements e anche diario clinico e esami del sangue
# Nella post deve essere ricevuto come params anche l'intervallo di tempo che si vuole esplorare
#------------------------------------------------------------------------------------------------------------------------
class TestParametri(object):
	exposed = True

	def __init__(self):

		self.id = id
		
		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.tenant_id=self.my_dict["sitewhere"]["tenant_id"]
		self.tenant_name=self.my_dict["sitewhere"]["tenant_name"]
		self.tenant_logo=self.my_dict["sitewhere"]["tenant_logo"]
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
		myfile = open("config.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):

		############################################
		# e' una get di prova
		# questo deve essere trasferito nella post
		############################################

		values = []

		today = datetime.date.today()
		margin = datetime.timedelta(days = 3) #questo 3 deve essere dato come params nella post

		con = MongoClient()
		db = con['tenant-'+self.tenant_pat_id]
		coll = db["assignments"] #e' la collection
		assignments = coll.find()
		pat_id = "rssgcm85c18c342q-giacomo-rossi"
		dev_id = "rssgcm85c18c342q-giacomo-rossi-test-pressione"
		token = ""
		for k in assignments:
			if k["assetId"] == pat_id and k["deviceHardwareId"] == dev_id:
				token = k["token"]
				break
		json_resp = self.mySitewhere.get_meaurements_by_assignment_token(token)
		mydict = json.loads(json_resp)
		measurements = mydict["results"]
		for j in range(0,len(measurements)):
			receiveDate = measurements[j]["receivedDate"]
			day_date = receiveDate.split("T")
			date = day_date[0]
			date = date.split("-")
			year = date[0]
			month = date[1]
			day = date[2]
			day_time = day_date[1]
			day_time = day_time.split(".")
			day_time = day_time[0]
			print day_time

			date_meas = datetime.date(int(year),int(month),int(day))
			receiveDate=str(date_meas)+" "+str(day_time)
			
			if date_meas >= (today-margin) and date_meas <= today: #da controllare questa riga
				pres = measurements[j]["measurements"]["test.pressione"]
				json_val = json.dumps({"receiveDate":receiveDate,"test.pressione":pres})
				values.append(json_val)
				print pres
				print json_val
				################################################################
				# bisogna poi fare la media dei valori di pressione selezionati
				################################################################
		return values
			
	def POST (self, * uri, ** params):

		if uri[0]=="valorimedi":

			tokens = []

			today = datetime.date.today()
			#processa l'intervallo su cui mediare
			mean_interval = params["mean_interval"]
			if mean_interval=="one_day":
				days = 1
			elif mean_interval == "three_days":
				days = 3
			elif mean_interval == "one_week":
				days = 7
			elif mean_interval == "three_weeks":
				days = 21
			elif mean_interval == "one_month":
				days = 30
			margin = datetime.timedelta(days = days)

			#si va a generare gli id dei devices che sono standard
			pat_id = params["id_pat"]
			devices_ids = [
				"iHealt_OpenApiWeight_"+pat_id+"_REAL_DEVICE_ID",
				"iHealt_OpenApiSpO2_"+pat_id+"_REAL_DEVICE_ID",
				"iHealt_OpenApiBP_"+pat_id+"_REAL_DEVICE_ID",
				"iHealt_OpenApiBG_"+pat_id+"_REAL_DEVICE_ID"
			]
			#chiede gli assignment di quello specifico paziente
			#si potrebbe fare anche con i roles
			json_resp = self.mySitewhere.get_assignment_associated_with_asset(self.asset_pat_id,pat_id)
			if json_resp != "error_string":
				mydict = json.loads(json_resp)
				results = mydict["results"]
				#va a prendere gli assignments relativi ai parametri
				#ci saranno anche quelli per il diario clinico, esami del sangue e test urine
				for k in range(0,len(results)):
					if results[k]["deviceHardwareId"] in devices_ids:
						#se il device id e' nei selezionati allora lo prende e gli accoppia l'assignment token
						tokens.append({"device_id":results[k]["deviceHardwareId"],"assignment_token":results[k]["token"]})
				
				#queste tre righe non servono perche deve prendere anche i dati prima
				response = json.dumps(tokens,indent=4, sort_keys=True)
				print response
				return response
			else:
				raise cherrypy.HTTPError(400, "error")



	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass


#----------------------------------------------------------------------------------------------------------------------------
# Classe di Test per la gestione dei dati del diario clinico.
# La POST riceve come parametri l'id del paziente e la data in cui si vuole vedere il diario clinico. L'id del diario
# clinico del paziente viene creato in automatico perche' si presume sia sempre lo stesso, ovvero id-paziente-diario-clinico.
# SE FOSSE SU SITEWHERE -> Una volta ricevuti i parametri nella POST viene richiamata una GET a sitewhere per ottenere tutti gli assignments fatti per
# quel site, e si va a cercare il token dell'assignment che ha come hardwareID il diario clinico e come assetID quello del 
# paziente(deve essere uguale a quello ricevuto come param). Una volta trovato il token ci sara' un ulteriore GET, questa 
# volta per cercare i measurements che stanno sotto quel token e che sono stati fatti in quella data passata nei params.
# Questo stesso iter dovrebbe essere seguito per i dati relativi agli esami del sangue. 
# SICCOME NON E' SU SITEWHERE -> si va direttamente a interrogare mongo
#----------------------------------------------------------------------------------------------------------------------------

class TestDiarioClinico(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.tenant_id=self.my_dict["sitewhere"]["tenant_id"]
		self.tenant_name=self.my_dict["sitewhere"]["tenant_name"]
		self.tenant_logo=self.my_dict["sitewhere"]["tenant_logo"]
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
		myfile = open("config.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):
		#GET PER IL TESTING
		pat_id = "rssplo88c18c342q-paolo-rossi"
		client = MongoClient()
		client = MongoClient('localhost', 27017)
		db = client[self.db_dialysis_diary]
		collection = db['dp_diaries']
		#events = collection.find()
		measurements_dp = collection.find({'userId':pat_id})
		for k in measurements_dp:
			print "*************"
			print k["request"]["eventDate"]
			print k["request"]["measurements"]
				
		
	def POST (self, * uri, ** params):

		print params
		pat_id = params["pat_id"] #da mandare con l'applicazione
		#VALUTARE SE E' UTILE UN PARAMETRO PER DISCRIMINARE TRA DIALISI PERITONEALE E EMODIALISI. Credo che sia la 
		#cosa migliore, per non avere due servizi web del diario e uno degli esami del sangue
		client = MongoClient()
		client = MongoClient('localhost', 27017)
		db = client[self.db_dialysis_diary]
		collection = db['dp_diaries']
		#events = collection.find()
		event = collection.find({'userId':pat_id})

		


			
	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass

#----------------------------------------------------------------------------------------------------------------------------
# Classe di Test per la gestione dei dati degli esami del sangue
# GET utilizzata per il test
# la POST prendera' come params l'id del paziente e la data
#----------------------------------------------------------------------------------------------------------------------------

class TestEsamiSangue(object):
	exposed = True

	def __init__(self):

		self.id = id
		self.my_dict = self.get_config_file()
		
		self.url = self.my_dict["sitewhere"]["url"]
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = self.my_dict["sitewhere"]["tenant_token"]
		self.tenant_id=self.my_dict["sitewhere"]["tenant_id"]
		self.tenant_name=self.my_dict["sitewhere"]["tenant_name"]
		self.tenant_logo=self.my_dict["sitewhere"]["tenant_logo"]
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
		myfile = open("config.json","r")
		stringa = myfile.read()
		dictionary = json.loads(stringa)
		myfile.close()
		return dictionary
		
		
	def GET (self, *uri, **params):
		#GET PER IL TESTING
		pat_id = "rssplo88c18c342q-paolo-rossi"
		client = MongoClient()
		client = MongoClient('localhost', 27017)
		db = client[self.db_dialysis_diary]
		collection = db['blood_test_diaries']
		#events = collection.find()
		measurements_dp = collection.find({'userId':pat_id})
		for k in measurements_dp:
			print "*************"
			print k["request"]["eventDate"]
			print k["request"]["measurements"]
				
		
	def POST (self, * uri, ** params):

		print params
		pat_id = params["pat_id"] #da mandare con l'applicazione
		#VALUTARE SE E' UTILE UN PARAMETRO PER DISCRIMINARE TRA DIALISI PERITONEALE E EMODIALISI. Credo che sia la 
		#cosa migliore, per non avere due servizi web del diario e uno degli esami del sangue
		client = MongoClient()
		client = MongoClient('localhost', 27017)
		db = client[self.db_dialysis_diary]
		collection = db['blood_test_diaries']
		#events = collection.find()
		event = collection.find({'userId':pat_id})
			
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
	cherrypy.tree.mount (TestParametri(), '/parametri', conf)
	cherrypy.tree.mount (TestDiarioClinico(), '/diarioclinico', conf)
	cherrypy.tree.mount (TestEsamiSangue(), '/esamisangue', conf)
	cherrypy.server.socket_host = '192.168.137.1'
	cherrypy.config.update({'server.socket_port':9090})
	cherrypy.engine.start()	
	cherrypy.engine.block()
