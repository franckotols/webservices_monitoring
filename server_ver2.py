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

class WebService(object):
	exposed = True

	def __init__(self):

		self.id = id
		
		self.url = "http://localhost:8080/sitewhere/api"
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = 'PATIENT_LIST_tenant_token'
		self.tenant_pat_id="PATIENT_LIST_tenant_id"
		self.tenant_pat_name="PatientRemoteMonitoring"
		self.tenant_pat_logo="data:image/jpeg;base64,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"

		self.auth=('franckotols', '000000')

		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		
		#ASSET LISTA MEDICI
		self.asset_med_id="lista_medici_asset_ID"
		self.asset_med_name="Lista Medici"

		
		
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

		if uri[0] == "diseases":
			con = MongoClient()
			db = con['utils']
			collection = db.diseases #e' la collection
			#docu = spec.find() find non va bene perche' restituisce un oggetto pymongo.cursor.cursos
			docu = collection.find_one() #restituisce il dizionario 
			target = docu["diseases"]
			mydict = {"diseases": target}
			return json.dumps(mydict)
			
	def POST (self, * uri, ** params):
		#copiato da giuseppe
		def toglispazi_startend(temp):
			temp=str(temp)
			if (len(temp)!=0):
				if (temp[-1]==" "):
					temp=temp[0:(len(temp))-1]
			if (len(temp)!=0):
				if (temp[0]==" "):
					temp=temp[1:(len(temp))]
			return (temp)

		if uri[0] = "registration":
			#per testare con postman
			#data = cherrypy.request.body.read()
			data=str(params['new_user_data'])
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

			nome=toglispazi_startend(nome)
			cognome=toglispazi_startend(cognome)
			user_password = toglispazi_startend(user_password)
			email=toglispazi_startend(email)
			phone=toglispazi_startend(phone)			
			
			imm_url="https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcQB4dVacA67gn_f0CQ1YMZ-cqDucluN1pPoXnEGR1NCa4rutI76"
			if (sesso=="Female"):
				imm_url="https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcSeMhLE4mlN1K4KrmWh9e_qkKS46K5_F4I9zAPXoJH_3zQawLLycg"
			nome_alpha_only="".join([i for i in nome if i.isalpha()])
			cognome_alpha_only="".join([i for i in cognome if i.isalpha()])
			
			##NB lo username inserito dall'utente e' diverso da quello creato per sitewhere, in modo che sia piu' 
			##facile per l'utente, una volta registrato, ricordarsi il proprio username
			
			pat_username=(nome_alpha_only+"_"+cognome_alpha_only).lower()
			pat_id=(nome_alpha_only+"-"+cognome_alpha_only).lower()
			pat_name=nome.upper()+" "+cognome.upper()
			nascita = giorno+"/"+mese+"/"+anno

			propert = {"name":nome, "last name":cognome, "password":user_password, "sex":sesso, "specializzazione":spec,"birthdate":nascita, "phone":phone}
			new_person_param={"roles":[""], "userName":pat_username, "emailAddress":email, "id":pat_id, "imageUrl":imm_url, "properties":propert, "name":pat_name}
			new_person_param_str=json.dumps(new_person_param)
			new_person_param_str=new_person_param_str.replace(": ",":")

			headers = {'content-type': 'application/json', 'X-SiteWhere-Tenant':self.tenant_token}
			post_person_url=self.url+"/assets/categories/"+self.asset_med_id+"/persons"
			

			s=requests.Session()
			#url per la GET, da sistemare
			get_url = self.url+"/assets/categories/lista_medici_asset_ID/assets"
			r = s.get(get_url, headers=headers, auth=self.auth)
			result = r.content
			dixt = json.loads(result)
			medici = dixt['results']
			index = 0
			for i in range(0,(len(medici))):
				if pat_username == medici[i]["userName"] or email == medici[i]["emailAddress"]:
					index = index + 1
			if index == 0:
				r=s.post(post_person_url,data=new_person_param_str, headers=headers, auth=self.auth)
				if r.status_code == 200:
					return "Registration successful"
			else:
				#codice messo a caso
				raise cherrypy.HTTPError(400, "Utente gia' registrato")

		elif uri[0] == "authentication":
			print params
			username = params["Username"]
			password = params["Password"]
			username = toglispazi_startend(username)
			password = toglispazi_startend(password)

			s=requests.Session()
			#url per la GET, da sistemare
			get_url = self.url+"/assets/categories/lista_medici_asset_ID/assets"
			headers = {'content-type': 'application/json', 'X-SiteWhere-Tenant':self.tenant_token}
			r = s.get(get_url, headers=headers, auth=self.auth)
			result = r.content
			dixt = json.loads(result)
			medici = dixt['results']
			flag = False

			for i in range(0,(len(medici))):
				if username == medici[i]["emailAddress"] and password == medici[i]["properties"]["password"]:
					flag = True
					break

			if flag == True:
				return "login_succesful"
			else:
				raise cherrypy.HTTPError(400, "wrong_params")

		elif uri[0] == "searchPatient":
			print params		
			search_name = params['patient_name']
			search_diseases = params['diseases']
			print "*********"
			print search_diseases			
			
			selected = []			

			link_req = "/assets/categories/PATIENT_LIST_asset_id/assets"
			url_def = self.url+link_req
			sessione = requests.Session()
			r = sessione.get(url_def, headers=self.headers, auth=self.auth)
			result = r.content
			dixt = json.loads(result)
			for i in range(0,len(dixt['results'])):		
				first_name = dixt['results'][i]['properties']['name']
				last_name = dixt['results'][i]['properties']['last name']
				user_diseases = dixt['results'][i]['properties']['user_disease']
				name = first_name+" "+last_name
				user_diseases = user_diseases.split(", ")
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

				#if search_name in name and user_disease in search_diseases:
					#selected.append(dixt['results'][i])
			
			#print selected
			#return json.dumps(selected)
				
		

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
	cherrypy.tree.mount (WebService(),	'/',	conf)
	cherrypy.server.socket_host = '192.168.173.1'
	cherrypy.config.update({'server.socket_port':9090})
	cherrypy.engine.start()	
	cherrypy.engine.block()
