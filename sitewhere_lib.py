import json
import os
import requests
import urllib
import copy
import sys

class My_SiteWhere_Request_Manager

	def __init__(self, swurl, ten_token)

	
	def nuovo_medico(self, data):

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

