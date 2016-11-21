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
