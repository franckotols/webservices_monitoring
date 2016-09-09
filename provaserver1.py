import random
import requests
import string 
import cherrypy
import json
import urllib
import urllib2
import operator
from sys import argv
#from sitewhere_lib import My_SiteWhere_Request_Manager

class Patient(object):
	
	def __init__(self, tax_code, address, phone_number):
		
		self.tax_code = tax_code
		self.address = address
		self.phone_number = phone_number

	def getTaxCode(self):
		return self.tax_code

class WebServer1(Patient):
	exposed = True

	def __init__(self):

		self.id = id
		
		self.url = "http://localhost:8080/sitewhere/api"
		#il tenant e' lo stesso creato da giuseppe
		self.tenant_token = 'PATIENT_LIST_tenant_token'
		self.tenant_pat_id="PATIENT_LIST_tenant_id"
		self.tenant_pat_name="PatientRemoteMonitoring"
		self.tenant_pat_logo="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxAQDxAQEBAPEA8OEA8PERAQERIRDw8PFRIWFhYRExMZHSkgGBomGxUVITEhJSkrLjouGB8zODMtNyktOisBCgoKDg0OGhAQGzclHyA3LS8rKy0rKy8tMC0tKy03LS0rKystLS0tKysuNzc3LS0wLS03Kzc3LTgvLS8rLTcrK//AABEIAIABigMBIgACEQEDEQH/xAAcAAEAAgMBAQEAAAAAAAAAAAAAAgQBAwUGBwj/xAA9EAACAQIEAQoEAwcDBQAAAAAAAQIDEQQSITGRBQYTIkFRUnGB0WGhorEyYpMHQoKSssHhFDNDFlNjwtL/xAAXAQEBAQEAAAAAAAAAAAAAAAAAAQID/8QAIREBAAMAAQQCAwAAAAAAAAAAAAECEQMhMUFhElEikaH/2gAMAwEAAhEDEQA/APuAAAAAAAAAAAAAAAAAAAAAAAABrq1VHKrNucsqStvlcu34RZsNOIptum1bqTcrNtXWSUd7fmAzHERd7vLl0lmssr7n8uKJqpG6WaN2rpXV2u9FKWEbk5NrNKSk0nKNmll6slqtEte3XTXSSwUskoNxaqauVtU8qjokkr6LXTyAtwqRe0ovfZp7W91xMKtDxR2vuttNfmuJWrYScm5XjCdoRVrtJLMm+zW05WXekV6/JellbKpykruTVm31cmy0bXoB0XViknmjZ7O6s/JmXNLdpb9q7NX9mUKsJZlJWbUZxtK9us4u/wBO3xKtTAScOjvFxWfWV25KVKULNecrgdmM07Wad1dWad13oi68NetF2TlZNN2RTqQlmjJWulKNndK0nF3+lFWGAapKF1dZru2jbpSp3+a4Add1YpXcopNXTbVmu/5riYdeC3nFdv4lscuODad7/hl1FeUbU7StG62ac36JI20MJaLWl+kU9HOL0pqGkt189NAOiqkb2ur2va6vbvsSKOHwTi43aeVqWa8k75MtlFWj/jSxeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEWzJCowFNXbfcTlBPdJ+auKcbIkBDoo+GPBDoY+GPBEwTIXZVauGjuox4I09HHwx4I6BXrUu1DINlX6OPhjwQ6OPhjwRMDINlBU4+FcETzW1MBlRbhIkV8PLTyN6AyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAjUqKKcpNRit29EjkYrnBTi7Ri5P4tQv6b8UcLnLy1NVZQfVhCTUe5taXueLxvKrdTq3k+6Or4IrOvpC5zxWtSjKMVvOMlUUV3u2yOxhq0aqjOElKElmTWzR81wlWuoSqzp1IQpwlNuSyyeWLdoxerbsel5rRlh8K4U5RqOM6lSOa6hkqVJTjTVtkk1FP4XBEvYA8zV53wh/uUKsX3K0lxRXfP7DLeFb+VkaeuB5KPP3CvaFZ3/I/YnU57UIq8qOJiu90ZpcWgPRvFQ2zdrjs91uiP8ArIXtmu9Nk3u7f3R5Z8/8L4K/6bC5/YXwV/02B6ice1bPUgedXPrDf9uv+mzH/WeGf/HiP02B6IHn487qD2p4j9P/ACWKPOCM/wAFDEPzjCK4uQHYpu0vMto5mEnOTvJKPck72Xn2s6UQJgwZAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANNPPFWm87160Y20vpePlZaX27DbGSeqafkSJWYxkAFQAAAGAABi5jMB4Lk1yji8bhm25U8ZVks23RVkq8WvhabXnFnolhkl+J+iSOJzjh0HK2FrqyhjaLw83/AOWhJzh6unUrfyHoJMqd3B5UTjLJJ3jNb96ejTI8yKt6Spyd3CDpP4ypSyP7Msc44dSM/DK3o17o4fNvE5MVUj2OqpLyqQX/ALOQTy9Ri8Cm9kVVyVHwrgdVSubIu2pGnjeVK06LlGlRemilTjmk/O2q8ijyZjK0s2ejXTukrwnDTzatxPfYibmus5O19pSj/S1chh5ZbuN9dNZOXC7ZNnUyPvq4eCwtOqpNKLcJZJWs7SsnbTTZouQ5Jj4VwKvJ9a3KmNpJJKWHweJdla9SUqtOUvNqnHgelpRKrlR5Jj4VwNseS4+FcDrpK3YjDsBzYcnRX7q4Fmnhktkjfn1trwNkWBClTsfLud37TcZhMfiMLQhg5QoOMU506spXcItptVEm033H1iJ+Z+dl3jcXlSeIxXKWMpwnO+WlShXlFWjrdtq12nZR0WugffOZHONco4OFeyjVi3SrQX4Y1opN5dX1WnGS+Ejvnwn9lfOOrg8ZTwdSVGVPGzSlGnvCo1aFVOy0ei7ra9mv3YDIAAAAARqTsr+XzdiRyuUeVIwk6eSrJqUG3ClVqJLSW8YtfC176liJnsk2isbMr7rfB8Jf/JKnVu7dtr9u3qitRrdJDP366qV462WlrrSz7GbISefZy6mnlmdm35WM6ROrINcacs2ZyesbZFbItb32vfs39DYIakABUAAAAAAAAAAAAAAjKmnr2960fFEgBC0ls0/PR8V7Hmp4p1uUKlCs6kaNGn1YQnOCz2jLNKUGm9HK3keoNc6MW02tU0/VWtfguBx5eKb5k9p6+/Tvw8sUmZmO8ZE/XtwuZvKE61OpGblJUqmWEp/jyv8Adk+1r+56Eg6UderHV3ei1dkrv0S4Do+5yXrf5PQvFS1KRWZ3PKc168l5tEZvhIwRyy716rX5MXl3L0evzR01ywZCRLN3xkvS/wBrkXJd9vNOP3GwZLncr8nQrxjnipSpSlUpN/u1ejnBSXpNlSjU6WjGS0cknr2SW9/VHZnZ7NPyaOd/pZRcrJWk83qVFDllZqFX4Rzfy9b+x4zA0pyxEZwTalGMW+xOEm1/U+B76eGlJNOyUk0+3RmcHyZCFrJaBMToRdkbMjLlOmjb0aCuXJ23IqaezT8mWK2H10bS9P7mvoH4pfT7AcvD8n25QqYlS/3MLRoOFtslWpNSv/G16HeUSGHopO9tX2lxIChiq00o5Un1lmTdnls9V8b2NTxj7jpVaKkrNf4KU8AvzfzS9wNFTFy0tG92k3faPa+B0aUdCtDCpd/q2/uXaYGXE/OP7RMFKjyliYJzpzhiKmKo1INqS6dqcrPuu9Gno097n6RscnlbkDC15KpXoUak4rKpVIRk8t72u1tq+IHyf9jfNeWJrrlHE16tVYKcqVCnLM49K4JueaT2ipLRLe3cfb0UsBRo0YKnSjTpwje0KUYxiru7tGPxLXSLsUn/AAtfcmrktgIZn2R4tL7XHW/KuMvYaYmVKuLWbLdpaWkouV/J7LVbvQsZH2yk/hovtqaKmEuoq6tBWjpK6XmpK5m3y8N0+O/kU8SrtLPJaauNrNtpK9kmnb/OqKOMw2IqVE6NVUlCsnUT3kujpW2vfRS021+B0KOGy6XunLO97uWm7bfcuAq4SEnme909o6tK3d8jXHa1essc1a26Q8njuVq9OFWUJ0JRpTmlF080o9d9Vu56/wD5P4F/Ua1gKemi0u9o7ve6sboUktvsl9jnx0tWZ227/HS/JFqRHxiJjesee2fpMAHVyAAAAAAAAAAAAAAAAAAAAAAAAAAAMGQwITinur+ZonRj4VwRYZFoGqjoL48X7ko0vi+LN+UyokxdlCMH4pfT7Esj8Uvp9iSRkYa0ypvxS+n2Nbpfmf0+xZaMWGGtMKb8T+n2Nqg/FL6fYkkSQw1HI/FL6fYx0b8Uvp9jYBhrV0Xxlxt9jKpL8380vc2AYbKHRR7k/PX7mVTitkl5JEwMg2UMplGQVGQYMgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMADBgyAI2FiQAwDIAwLAyBgyAAAAAyAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAf/Z"

		self.auth=('franckotols', '000000')

		self.headers = {'X-Sitewhere-Tenant': self.tenant_token}

		self.list_patient =[]

		#ASSET PATIENT_LIST
		# self.asset_pat_id="PATIENT_LIST_asset_id"
		# self.asset_pat_name="Patients List"
		
		#ASSET LISTA MEDICI
		self.asset_med_id="lista_medici_asset_ID"
		self.asset_med_name="Lista Medici"

		
		
	def GET (self, *uri, **params):

		if uri[0] == "categories":
			link_req = "/assets/categories"
			url_def = self.url+link_req
			headers = self.headers
			sessione = requests.Session()
			r = sessione.get(url_def, headers=headers, auth=self.auth)
			return r.content

		elif uri[0] == "patient_list":
			link_req = "/assets/categories/PATIENT_LIST_asset_id/assets"
			url_def = self.url+link_req
			headers = self.headers
			sessione = requests.Session()
			r = sessione.get(url_def, headers=headers, auth=self.auth)
			result = r.content
			dixt = json.loads(result)
			pazienti = dixt['results']
			
			
			for i in range(0,(len(pazienti))):
				tax_code = pazienti[i]["properties"]["TAX code"]
				address = pazienti[i]["properties"]["address"]
				phone = pazienti[i]["properties"]["phone"]
				paziente = Patient(tax_code, address, phone)
				tax = paziente.getTaxCode()
				print tax
				self.list_patient.append(paziente)
				#print self.list_patient[i]

			return result

		# elif uri[0] == "lista_medici":
		# 	link_req =  "/assets/categories/lista_medici_asset_ID/assets"
		# 	url_def = self.url+link_req
		# 	headers = {'X-Sitewhere-Tenant': self.tenant_token}
		# 	sessione = requests.Session()
		# 	r = sessione.get(url_def, headers=headers, auth=self.auth)
		# 	result = r.content


	def POST (self, * uri, ** params):
		#copiato da giuseppe

		data = cherrypy.request.body.read()

		data_obj=json.loads(data)
		nome=data_obj['first_name']
		cognome=data_obj['last_name']
		sesso=data_obj['sex']
		giorno=str(data_obj['day'])
		mese=str(data_obj['month'])
		anno=str(data_obj['year'])
		tax_code=data_obj['tax_code']
		email=data_obj['email']
		phone=data_obj['phone']
		city=data_obj['city']
		addr=data_obj['address']
		zip_code=data_obj['zip_code']
		# nome=toglispazi_startend(nome)
		# cognome=toglispazi_startend(cognome)
		# tax_code=toglispazi_startend(tax_code)
		# email=toglispazi_startend(email)
		# phone=toglispazi_startend(phone)
		# city=toglispazi_startend(city)
		# addr=toglispazi_startend(addr)
		# zip_code=toglispazi_startend(zip_code)

		#print ("\n\n\nNUOVO UTENTE:\nNome:\t\t\t"+nome+"\nCognome:\t\t"+cognome+"\nSesso:\t\t\t"+sesso+"\nData di nascita:\t"+giorno+"/"+mese+"/"+anno+"\nCodice fiscale:\t\t"+tax_code+"\ne-mail:\t\t\t"+email+"\nTelefono:\t\t"+phone+"\nCitta':\t\t\t"+city+"\nIndirizzo:\t\t"+addr+"\nCAP:\t\t\t"+zip_code+"\n")
		imm_url="https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcQB4dVacA67gn_f0CQ1YMZ-cqDucluN1pPoXnEGR1NCa4rutI76"
		if (sesso=="Female"):
			imm_url="https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcSeMhLE4mlN1K4KrmWh9e_qkKS46K5_F4I9zAPXoJH_3zQawLLycg"
		nome_alpha_only="".join([i for i in nome if i.isalpha()])
		cognome_alpha_only="".join([i for i in cognome if i.isalpha()])
		
		
		pat_username=(nome_alpha_only+"_"+cognome_alpha_only).lower()
		pat_id=(tax_code+"-"+nome_alpha_only+"-"+cognome_alpha_only).lower()
		pat_name=nome.upper()+" "+cognome.upper()
		nascita = giorno+"/"+mese+"/"+anno

		propert={"name":nome, "last name":cognome, "sex":sesso, "birthdate":nascita, "TAX code":tax_code, "phone":phone, "city":city, "address":addr, "ZIP code":zip_code}
		new_person_param={"roles":[""], "userName":pat_username, "emailAddress":email, "id":pat_id, "imageUrl":imm_url, "properties":propert, "name":pat_name}
		new_person_param_str=json.dumps(new_person_param)
		new_person_param_str=new_person_param_str.replace(": ",":")

		headers = {'content-type': 'application/json', 'X-SiteWhere-Tenant':self.tenant_token}
		post_person_url=self.url+"/assets/categories/"+self.asset_med_id+"/persons"
		s=requests.Session()
		r=s.post(post_person_url,data=new_person_param_str, headers=headers, auth=self.auth)
		print post_person_url
		print "***************"
		print (new_person_param_str)
		print (r.status_code)
		print (r.content)
		#return [r.status_code, r.content]

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
	cherrypy.tree.mount (WebServer1(),	'/',	conf)
	cherrypy.server.socket_host = '0.0.0.0'
	cherrypy.config.update({'server.socket_port':9090})
	cherrypy.engine.start()	
	cherrypy.engine.block()