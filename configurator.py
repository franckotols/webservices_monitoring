import sys
import os
from os import listdir
import requests
import urllib
import json

class PlatformConfigurator:
	def __init__(self):
		pass

	def connect(self, addr):
		params={"client":"configurator"}
		sec=urllib.urlencode(params)
		try:
			s=requests.Session()
			r=s.post(addr,params=sec)
			return [r.content, r.status_code]
		except:
			return ["No connection","bad"]

	def send_command_simple(self, addr, cmd):
		params={"command_simple":cmd}
		sec=urllib.urlencode(params)
		s=requests.Session()
		r=s.post(addr,params=sec)
		return [r.content, r.status_code]

	def send_command_mongo(self, addr, cmd, db="-"):
		params={"command_mongo":cmd, "db":db}
		sec=urllib.urlencode(params)
		s=requests.Session()
		r=s.post(addr,params=sec)
		return [r.content, r.status_code]

	def send_reset_specs(self, addr, uu, up, uf, ul, st, sn, sd, si, slo, sla, sz, tt, tid, tn, tim, tgt, tgn, tgd, tgi):
		params={"command_sitewhere":"reset","uu":uu, "up":up, "uf":uf, "ul":ul, "st":st, "sn":sn, "sd":sd, "si":si, "slo":slo, "sla":sla, "sz":sz, "tt":tt, "tid":tid, "tn":tn, "tim":tim, "tgt":tgt, "tgn":tgn, "tgd":tgd, "tgi":tgi}
		sec=urllib.urlencode(params)
		s=requests.Session()
		r=s.post(addr,params=sec)
		return [r.content, r.status_code]

	def get_category_assets_list (self, addr):
		params={"command_health_server":"get_asset_list"}
		sec=urllib.urlencode(params)
		s=requests.Session()
		r=s.post(addr,params=sec)
		return [r.content, r.status_code]

	def update_category_assets_list(self, addr, specs_str):
		params=json.loads(specs_str)
		params['command_health_server']="update_asset_list"
		sec=urllib.urlencode(params)
		s=requests.Session()
		r=s.post(addr,params=sec)
		return [r.content, r.status_code]

	def send_ihealth_codes(self, addr, msg):
		params={"ihealth_codes":msg}
		sec=urllib.urlencode(params)
		s=requests.Session()
		r=s.post(addr,params=sec)
		return [r.content, r.status_code]

class ConfiguratorClient:

	def __init__(self):
		self.gestore_richieste=PlatformConfigurator()
		self.initial_variables()
		self.first_visualization()

	def initial_variables(self):
		self.addr=None
		self.host=None
		self.sitewhere_is_running=None
		self.broker_is_running=None
		self.mongo_is_running=None
		self.health_server_is_running=None
		self.sitewhere_port=None
		self.broker_port=None
		self.mongo_port=None
		self.sitewhere_status=None
		self.options_menu_a=[
							"START\tSiteWhere (does also: 2, 3)",
							"START\tMongoDB",
							"START\tBroker",
							"START\tHealth Server Application",
							"STOP\tSiteWhere",
							"STOP\tMongoDB (does also: 5)",
							"STOP\tBroker (does also: 5)",
							"STOP\tHealth Server Application",
							"SHOW\tall MongoDB DataBases",
							"CANC\tone MongoDB DataBase (does also: 5)",
							"CANC\tall MongoDB DataBases (does also: 5)",
							"RESET\tSitewhere Initial Configuration (does also: 5, 8, 2)",
							"EDIT\tSitewhere Category Assets (does also: 8)",
							"SET\tiHealth Application Codes (does also: 8)"
							]
		self.reset_sitewhere_config_file_name="RESET_SITEWHERE_CONFIG.txt"
		self.add_category_assets_config_file_name="CATEGORY_ASSETS_CONFIG.txt"
		self.reset_sitewhere_config_file_content='''// Configuration File for SiteWhere

## User Information
User.Username =
User.Password =
User.First_Name =
User.Last_Name =

## Site Information
Site.Token = IOTREMOTEDISEASESMONITORING_site_token
Site.Name = IoT Remote Diseases Monitoring
Site.Description = An IoT Data Processing System for Remote chronic metabolic diseases Analysis and Monitoring
Site.Image_URL = http://wheelhousecollective.com/wp-content/uploads/2010/07/hero_HealthInterlink_remote-patient-monitoring5.jpg
Site.Longitude = 45.064347
Site.Latitude = 7.659114
Site.Zoom = 15

## Tenant Information
Tenant.Token = IoT_Smart_Health_tenant_token
Tenant.ID = IoT_Smart_Health_tenant_id
Tenant.Name = PatientRemoteMonitoring
Tenant.Image_URL = data:image/jpeg;base64,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

## Tenant Group Information
TenantGroup.Token = Group_of_Tenants_token
TenantGroup.Name = IoT_Telemedicine_Platforms
TenantGroup.Description = Group of Tenants concerning the Telemedicine and Patients Remote Monitoring
TenantGroup.Image_URL = http://ehealth.intersog.com/wp-content/uploads/ehealth/2015/12/shutterstock_312305699-2-1325x590.jpg'''
		self.ihealth_codes_config_file_name='''iHealth_CODES_CONFIG.txt'''
		self.ihealth_codes_config_file_content='''# This is the configuration file for the iHealth Application
#
# Example:
# ============================================================
# Client ID 2295*************************622
# Client Secret 8277*************************5f1
# Redirect Domain https://theRedirectDomain.com
#
# OpenApiActivity 	SC: 7e59*************************7da
# SV: 0d20*************************0b7
# OpenApiBG 	SC: 7e59*************************7da
# SV: ec00*************************273
# OpenApiBP 	SC: 7e59*************************7da
# SV: cf6b*************************fac
# OpenApiFood 	SC: 7e59*************************7da
# SV: 6c89*************************85c
# OpenApiSleep 	SC: 7e59*************************7da
# SV: 8823*************************53a
# OpenApiSpO2 	SC: 7e59*************************7da
# SV: 683c*************************3ef
# OpenApiSport 	SC: 7e59*************************7da
# SV: 50a8*************************676
# OpenApiUserInfo 	SC: 7e59*************************7da
# SV: 74dd*************************891
# OpenApiWeight 	SC: 7e59*************************7da
# SV: ec49*************************17d
# ============================================================

Client ID 
Client Secret 
Redirect Domain 

OpenApiActivity 	SC: 
SV: 
OpenApiBG 	SC: 
SV: 
OpenApiBP 	SC: 
SV: 
OpenApiFood 	SC: 
SV: 
OpenApiSleep 	SC: 
SV: 
OpenApiSpO2 	SC: 
SV: 
OpenApiSport 	SC: 
SV: 
OpenApiUserInfo 	SC: 
SV: 
OpenApiWeight 	SC: 
SV: '''

	def first_visualization(self):
		print ("\n"*100)
		addr_default="http://giupe.webfactional.com/config"
		code=None
		exit_a=False
		while (code!=200):
			if (exit_a is True):
				sys.exit(0)
			self.addr=raw_input("\nType the complete address of the remote host\nand the mount point of the configuration application.\n\tExample:\n\t"+addr_default+"\n\nPress ENTER without typing anything to set\nthe address specified in the example.\n")
			if (self.addr==""):
				self.addr=addr_default
			[msg,code]=self.gestore_richieste.connect(self.addr)
			if (code!=200):
				print ("\nCode: "+str(code)+"\n"+msg)
				retry=raw_input("\nError.\nPress ENTER to retry.\nType 'exit' and press ENTER to exit.\n")
				if (retry.upper()=="EXIT"):
					exit_a=True
		self.menu_a(msg)

	def update_connection(self):
		[msg,code]=self.gestore_richieste.connect(self.addr)
		if (code!=200):
			print ("\nCode: "+str(code)+"\n"+msg)
			retry=raw_input("\nAn Error occurred in comunication with the Configuration Application Server.\nPress ENTER to retry.\nType 'exit' and press ENTER to exit.\n")
			if (retry.upper()=="EXIT"):
				pass
			else:
				self.menu_a()
		else:
			self.menu_a(msg)

	def menu_a(self,msg=None):
		if (msg is None):
			self.update_connection()
		else:
			if ("//" in self.addr):
				self.host=(((self.addr).split("//"))[0])+"//"+(((((self.addr).split("//"))[1]).split("/"))[0])
			else:
				self.host=((self.addr).split("/"))[0]
			try:
				msg_obj=json.loads(msg)
				self.sitewhere_is_running=False
				if (msg_obj['sitewhere']=="on"):
					self.sitewhere_is_running=True
				self.mongo_is_running=False
				if (msg_obj['mongo']=="on"):
					self.mongo_is_running=True
				self.broker_is_running=False
				if (msg_obj['broker']=="on"):
					self.broker_is_running=True
				self.health_server_is_running=False
				if (msg_obj['health']=="on"):
					self.health_server_is_running=True
				self.sitewhere_port=msg_obj['sitewhere_port']
				self.mongo_port=msg_obj['mongo_port']
				self.broker_port=msg_obj['broker_port']
				self.sitewhere_status=msg_obj['sitewhere_status']
				self.draw_menu_a()
			except:
				print ("\nError. Wrong Remote Host.")
				raw_input("Press ENTER to continue.\n")
				print ("\n"*100)
				self.first_visualization()

	def draw_menu_a(self):
		print ("\n"*100)
		print ("\n\tRemote Host: "+self.host)
		if (self.health_server_is_running is True):
			print("\n\tHealth Server:\tRUNNING")
		else:
			print("\n\tHealth Server:\tSTOPPED")
		if (self.sitewhere_is_running is True):
			if (self.sitewhere_status=="ready"):
				print ("\tSiteWhere:\tRUNNING\t\tREADY")
			else:
				print ("\tSiteWhere:\tRUNNING\t\tNOT READY (it may take up to 1 minutes to get ready)")
		else:
			print ("\tSiteWhere:\tSTOPPED")
		if (self.mongo_is_running is True):
			print ("\tMongoDB:\tRUNNING\t\tport="+self.mongo_port)
		else:
			print ("\tMongoDB:\tSTOPPED\t\tport="+self.mongo_port)
		if (self.broker_is_running is True):
			print ("\tBroker:\t\tRUNNING\t\tport="+self.broker_port)
		else:
			print ("\tBroker:\t\tSTOPPED\t\tport="+self.broker_port)
		print ("\n\n\tSelect an option typing the relative number and press ENTER.\n\tType 'exit' and press ENTER to exit.\n\tPress ENTER without typing anything to reload informations.\n")
		for n in range(len(self.options_menu_a)):
			print ("\t"+str(n+1)+"\t- "+self.options_menu_a[n])
		sel=raw_input()
		if ((sel.upper()!="EXIT") and (sel!="")):
			self.detect_operation(sel)
		if (sel==""):
			self.menu_a()

	def detect_operation(self, sel):
		try:
			sel=(int(sel))-1
			operation=self.options_menu_a[sel]
		except:
			operation=None
			raw_input("\nWrong Input. Press ENTER to continue.\n")
			self.menu_a()
		if (operation):
			print ("\nREQUEST:\t"+operation)
			if ("START" in operation):
				if ("SiteWhere" in operation):
					self.start_sitewhere()
				if ("MongoDB" in operation):
					self.start_mongo()
				if ("Broker" in operation):
					self.start_broker()
				if ("Application" in operation):
					self.start_health_app()
			if ("STOP" in operation):
				if ("SiteWhere" in operation):
					self.stop_sitewhere()
				if ("MongoDB" in operation):
					self.stop_mongo()
				if ("Broker" in operation):
					self.stop_broker()
				if ("Application" in operation):
					self.stop_health_app()
			if ("SHOW" in operation):
				self.show_mongo_dbs()
			if ("CANC" in operation):
				if ("one" in operation):
					self.delete_mongo_db()
				if ("all" in operation):
					self.delete_mongo_dbs()
			if ("RESET" in operation):
				self.reset_sitewhere()
			if ("EDIT" in operation):
				self.add_category_assets()
			if ("SET" in operation):
				self.set_ihealth_codes()

	def start_sitewhere(self):
		[msg,code]=self.gestore_richieste.send_command_simple(self.addr, "start_sitewhere")
		print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
		raw_input("\nPress ENTER to continue.\n")
		self.menu_a()

	def start_mongo(self):
		[msg,code]=self.gestore_richieste.send_command_simple(self.addr, "start_mongo")
		print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
		raw_input("\nPress ENTER to continue.\n")
		self.menu_a()

	def start_broker(self):
		[msg,code]=self.gestore_richieste.send_command_simple(self.addr, "start_broker")
		print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
		raw_input("\nPress ENTER to continue.\n")
		self.menu_a()

	def start_health_app(self):
		[msg,code]=self.gestore_richieste.send_command_simple(self.addr, "start_health")
		print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
		raw_input("\nPress ENTER to continue.\n")
		self.menu_a()

	def stop_sitewhere(self):
		[msg,code]=self.gestore_richieste.send_command_simple(self.addr, "stop_sitewhere")
		print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
		raw_input("\nPress ENTER to continue.\n")
		self.menu_a()

	def stop_mongo(self):
		[msg,code]=self.gestore_richieste.send_command_simple(self.addr, "stop_mongo")
		print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
		raw_input("\nPress ENTER to continue.\n")
		self.menu_a()

	def stop_broker(self):
		[msg,code]=self.gestore_richieste.send_command_simple(self.addr, "stop_broker")
		print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
		raw_input("\nPress ENTER to continue.\n")
		self.menu_a()

	def stop_health_app(self):
		[msg,code]=self.gestore_richieste.send_command_simple(self.addr, "stop_health")
		print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
		raw_input("\nPress ENTER to continue.\n")
		self.menu_a()

	def show_mongo_dbs(self):
		[msg,code]=self.gestore_richieste.send_command_mongo(self.addr, "show_dbs")
		print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
		raw_input("\nPress ENTER to continue.\n")
		self.menu_a()

	def delete_mongo_db(self):
		[msg,code]=self.gestore_richieste.send_command_mongo(self.addr, "list_dbs")
		print ("\nRESPONSE:\tCode:\t"+str(code))
		if (code!=200):
			print("\t\t"+(msg.replace("\n","\n\t\t")))
			raw_input("\nPress ENTER to continue.\n")
		else:
			dbs_list=json.loads(msg)
			loop=True
			while (loop):
				print ("\n\t\tWhich DataBase do you want to remove?")
				for i in range(len(dbs_list)):
					print ("\t\t"+str(i+1)+"\t- "+dbs_list[str(i)])
				print ("\n\t\tType the number relative to the DataBase you want to remove and press ENTER.\n\t\tPress ENTER without typing anything to go back to the main menu.\n")
				sel=raw_input()
				db=None
				if (sel!=""):
					try:
						db=dbs_list[str(int(sel)-1)]
						loop=False
					except:
						raw_input("\nWrong Input. Press ENTER to continue.\n")
				else:
					loop=False
			if (db is not None):
				[msg,code]=self.gestore_richieste.send_command_mongo(self.addr, "remove_db", db)
				print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
				raw_input("\nPress ENTER to continue.\n")
			else:
				pass
		self.menu_a()

	def delete_mongo_dbs(self):
		[msg,code]=self.gestore_richieste.send_command_mongo(self.addr, "list_dbs")
		print ("\nRESPONSE:\tCode:\t"+str(code))
		if (code!=200):
			print("\t\t"+(msg.replace("\n","\n\t\t")))
			raw_input("\nPress ENTER to continue.\n")
		else:
			dbs_list=json.loads(msg)
			loop=True
			while (loop):
				print ("\n\t\tAre you sure you want remove all these DataBases?")
				for i in range(len(dbs_list)):
					print ("\t\t\t"+dbs_list[str(i)])
				print ("\n\t\tType YES or No, and press ENTER.\n\t\tPress ENTER without typing anything to go back to the main menu.\n")
				confirm=False
				sel=raw_input()
				if (sel!=""):
					if ((sel.upper()=="YES") or (sel.upper()=="Y")):
						loop=False
						confirm=True
					elif ((sel.upper()=="NO") or (sel.upper()=="N")):
						loop=False
						raw_input("\nNo DataBases have been removed.\nPress ENTER to continue.\n")
					else:
						raw_input("\nWrong Input. Press ENTER to continue.\n")
				else:
					loop=False
			if (confirm is True):
				[msg,code]=self.gestore_richieste.send_command_mongo(self.addr, "remove_all", "-")
				print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
				raw_input("\nPress ENTER to continue.\n")
			else:
				pass
		self.menu_a()

	def reset_sitewhere(self, fname=None):
		if (fname is None):
			fname=self.reset_sitewhere_config_file_name
		print ("\nSelect an option and press ENTER,\nor press ENTER without typing anything to go back to the main menu.")
		print ("\t1\t- I have already a configuration file.")
		sel=raw_input ("\t2\t- I don't have a configuration file. I want it to be generated.\n")
		while ((sel!="1")and(sel!="2")and(sel!="")):
			print ("\nWrong input")
			print ("\nSelect an option and press ENTER,\n or press ENTER without typing anything to go back to the main menu.")
			print ("\t1\t- I have already a configuration file.")
			sel=raw_input ("\t2\t- I don't have a configuration file. I want it to be generated.\n")
		if (sel=="2"):
			self.generate_file("reset")
		elif (sel=="1"):
			sel_good=False
			while (sel_good is False):
				print ("\nType the name of the configuration file and press ENTER.")
				print ("Press ENTER without typing anything to use the file '"+fname+"'.")
				print ("Type 'exit' and press ENTER to go back to the main menu.")
				sel_f_name=raw_input()
				if (sel_f_name==""):
					sel_f_name=fname
				if (sel_f_name.upper()=="EXIT"):
					sel_good=True
				else:
					try:
						f=open(sel_f_name,"r")
						f_content=f.readlines()
						f.close()
						sel_good=True
						self.read_config_reset(f_content)
					except:
						print ("\nThe file '"+sel_f_name+"' does not exist.\nPress ENTER to continue.")
						sel_good=False
						raw_input()
		else:
			self.menu_a()

	def add_category_assets(self, fname=None):
		if (fname is None):
			self.generate_file("add")
		else:
			sel_good=False
			while (sel_good is False):
				print ("\nType the name of the configuration file and press ENTER.")
				print ("Press ENTER without typing anything to use the file '"+fname+"'.")
				print ("Type 'exit' and press ENTER to go back to the main menu.")
				sel_f_name=raw_input()
				if (sel_f_name==""):
					sel_f_name=fname
				if (sel_f_name.upper()=="EXIT"):
					sel_good=True
				else:
					try:
						f=open(sel_f_name,"r")
						f_content=f.readlines()
						f.close()
						sel_good=True
						self.read_config_add_assets(f_content)
					except:
						print ("\nThe file '"+sel_f_name+"' does not exist.\nPress ENTER to continue.")
						sel_good=False
						raw_input()
			self.menu_a()

	def read_config_add_assets (self, f_content):
		specs={}
		replacer=""
		for i in range(len(f_content)):
			line=f_content[i]
			if ("delete_other_assets" in line):
				value=(line.split("="))[1]
				value=value.replace("\n","")
				value=value.replace(" ","")
				value=value.replace("\t","")
				specs['delete_other_assets']=value
			if ("#" in line):
				value=line.replace("\n","")
				if ((len(value))>=1):
					while (value[0]==" "):
						value=value[1:(len(value))]
						if ((len(value))<1):
							break
				if ((len(value))>=1):
					while (value[-1]==" "):
						value=value[0:((len(value))-1)]
						if ((len(value))<1):
							break
				replacer=value
			if ((line.replace(" ","")).startswith("ID")):
				current_replacer=replacer+"_-_ID"
				value=(line.split("="))[1]
				value=value.replace("\n","")
				if ((len(value))>=1):
					while (value[0]==" "):
						value=value[1:(len(value))]
						if ((len(value))<1):
							break
				if ((len(value))>=1):
					while (value[-1]==" "):
						value=value[0:((len(value))-1)]
						if ((len(value))<1):
							break
				specs[current_replacer]=value
			if ((line.replace(" ","")).startswith("NAME")):
				current_replacer=replacer+"_-_NAME"
				value=(line.split("="))[1]
				value=value.replace("\n","")
				if ((len(value))>=1):
					while (value[0]==" "):
						value=value[1:(len(value))]
						if ((len(value))<1):
							break
				if ((len(value))>=1):
					while (value[-1]==" "):
						value=value[0:((len(value))-1)]
						if ((len(value))<1):
							break
				specs[current_replacer]=value
			if ((line.replace(" ","")).startswith("TYPE")):
				current_replacer=replacer+"_-_TYPE"
				value=(line.split("="))[1]
				value=value.replace("\n","")
				if ((len(value))>=1):
					while (value[0]==" "):
						value=value[1:(len(value))]
						if ((len(value))<1):
							break
				if ((len(value))>=1):
					while (value[-1]==" "):
						value=value[0:((len(value))-1)]
						if ((len(value))<1):
							break
				specs[current_replacer]=value
		specs_str=json.dumps(specs)
		[msg,code]=self.gestore_richieste.update_category_assets_list(self.addr,specs_str)
		print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
		raw_input("\nPress ENTER to continue.\n")
		self.menu_a()

	def generate_file(self, tipo):
		if (tipo=="reset"):
			f_name=self.reset_sitewhere_config_file_name
		if (tipo=="add"):
			f_name=self.add_category_assets_config_file_name
		if (tipo=="ihealth_codes"):
			f_name=self.ihealth_codes_config_file_name
		cwd = os.getcwd()
		file_list=listdir(cwd)
		loop=True
		while (loop is True):
			if (f_name in file_list):
				print ("\nThere is already a file named\n\t'"+f_name+"'\nin the folder\n\t'"+cwd+"'")
				replace=raw_input("\nDo you want to replace it?\t(Yes/No)\n")
				while ((replace.upper()!="N")and(replace.upper()!="Y")and(replace.upper()!="NO")and(replace.upper()!="YES")):
					print ("\nWrong input.\nThere is already a file named\n\t'"+f_name+"'\nin the folder\n\t'"+cwd+"'")
					replace=raw_input("\nDo you want to replace it?\t(Yes/No)\n")
				if ((replace.upper()=="NO")or(replace.upper()=="N")):
					loop_two=True
					while (loop_two is True):
						f_name=raw_input("\nType a new name for the configuration file.\n")
						if (f_name in file_list):
							loop_two=False
						else:
							if (f_name!=""):
								try:
									f=open(f_name,"w")
									f.close()
									os.remove(f_name)
									loop_two=False
								except:
									print ("\nInvalid file name.\n")
							else:
								print ("\nInvalid file name.\n")
				else:
					loop=False
			else:
				loop=False

		if (tipo=="add"):
			[ans,code]=self.gestore_richieste.get_category_assets_list(self.addr)
			if (code==200):
				content=self.generate_asset_content(ans)
			else:
				print ("\nError in connecting the configurator server\nPress ENTER to continue.")
				raw_input()
				self.menu_a()
		if (tipo=="reset"):
			content=self.reset_sitewhere_config_file_content
		if (tipo=="ihealth_codes"):
			content=self.ihealth_codes_config_file_content
		f=open(f_name,"w")
		f.write(content)
		f.close()
		if (tipo=="add"):
			print ("\nThe configuration file\n\t'"+f_name+"'\nhas been generated!\nFile path:\t"+cwd)
			print ("\nEdit it now before continuing.")
			raw_input("\nPress ENTER to continue.\n")
			self.add_category_assets(f_name)
		if (tipo=="reset"):
			print ("\nThe configuration file\n\t'"+f_name+"'\nhas been generated!\nFile path:\t"+cwd)
			print ("\nEdit it now before continuing.")
			raw_input("\nPress ENTER to continue.\n")
			self.reset_sitewhere(f_name)
		if (tipo=="ihealth_codes"):
			print ("\nThe configuration file\n\t'"+f_name+"'\nhas been generated!\nFile path:\t"+cwd)
			print ("\nEdit it now before continuing.")
			raw_input("\nPress ENTER to continue.\n")
			self.set_ihealth_codes(f_name)

	def generate_asset_content(self, assets):
		msg="// Configuration File for SiteWhere Category Assets.\n"
		msg=msg+"\n// Choose if you want to delete all the other Category Assets not listed here. ( YES / NO )\n"
		msg=msg+"delete_other_assets = YES\n\n"
		msg=msg+assets
		return (msg)

	def extract_var (self, l):
		elems=l.split("=")
		if ((len(elems))>1):
			var=elems[1]
		else:
			var=""
		if ((len(var))>1):
			while (var[0]==" "):
				var=var[1:(len(var))]
				if ((len(var))<=1):
					break
		return (var)

	def read_config_reset(self, f_content):
		var_set=0
		error=False
		err_msg=""

		uu=None
		up=None
		uf=None
		ul=None
		st=None
		sn=None
		sd=None
		si=None
		slo=None
		sla=None
		sz=None
		tt=None
		tid=None
		tn=None
		tim=None
		tgt=None
		tgn=None
		tgd=None
		tgi=None

		for i in range(len(f_content)):
			line=f_content[i]
			if ((len(line))>1):
				while (((len(line))>1) and (((line[-1])=="\n")or((line[-1])==" "))):
					while ((line[-1])=="\n"):
						line=line[0:((len(line))-1)]
						if ((len(line))<=1):
							break
					if ((len(line))<=1):
						break
					while ((line[-1])==" "):
						line=line[0:((len(line))-1)]
						if ((len(line))<=1):
							break
					if ((len(line))<=1):
						break
			if (line.startswith("#")):
				pass
			if ("#" in line):
				ind=line.find("#")
				line=line[0:ind]
			if ((len(line))>1):
				while (((len(line))>1) and (((line[0])==" ")or((line[-1])==" "))):
					while ((line[-1])==" "):
						line=line[0:((len(line))-1)]
						if ((len(line))<=1):
							break
					if ((len(line))<=1):
						break
					while ((line[0])==" "):
						line=line[1:(len(line))]
						if ((len(line))<=1):
							break
					if ((len(line))<=1):
						break
			if ((line.startswith("User.Username")) and(uu is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide User.Username"
				else:
					uu=value
					var_set=var_set+1
			if ((line.startswith("User.Password")) and(up is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide User.Password"
				else:
					up=value
					var_set=var_set+1
			if ((line.startswith("User.First_Name")) and(uf is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide User.First_Name"
				else:
					uf=value
					var_set=var_set+1
			if ((line.startswith("User.Last_Name")) and(ul is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide User.Last_Name"
				else:
					ul=value
					var_set=var_set+1
			if ((line.startswith("Site.Token")) and(st is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide Site.Token"
				else:
					st=value
					var_set=var_set+1
			if ((line.startswith("Site.Name")) and(sn is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide Site.Name"
				else:
					sn=value
					var_set=var_set+1
			if ((line.startswith("Site.Description")) and(sd is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide Site.Description"
				else:
					sd=value
					var_set=var_set+1
			if ((line.startswith("Site.Image_URL")) and(si is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide Site.Image_URL"
				else:
					si=value
					var_set=var_set+1
			if ((line.startswith("Site.Longitude")) and(slo is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide Site.Longitude"
				else:
					slo=value
					var_set=var_set+1
			if ((line.startswith("Site.Latitude")) and(sla is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide Site.Latitude"
				else:
					sla=value
					var_set=var_set+1
			if ((line.startswith("Site.Zoom")) and(sz is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide Site.Zoom"
				else:
					sz=value
					var_set=var_set+1
			if ((line.startswith("Tenant.Token")) and(tt is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide Tenant.Token"
				else:
					tt=value
					var_set=var_set+1
			if ((line.startswith("Tenant.ID")) and(tid is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide Tenant.ID"
				else:
					tid=value
					var_set=var_set+1
			if ((line.startswith("Tenant.Name")) and(tn is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide Tenant.Name"
				else:
					tn=value
					var_set=var_set+1
			if ((line.startswith("Tenant.Image_URL")) and(tim is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide Tenant.Image_URL"
				else:
					tim=value
					var_set=var_set+1

			if ((line.startswith("TenantGroup.Token")) and(tgt is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide TenantGroup.Token"
				else:
					tgt=value
					var_set=var_set+1
			if ((line.startswith("TenantGroup.Name")) and(tgn is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide TenantGroup.Name"
				else:
					tgn=value
					var_set=var_set+1
			if ((line.startswith("TenantGroup.Description")) and(tgd is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide TenantGroup.Description"
				else:
					tgd=value
					var_set=var_set+1
			if ((line.startswith("TenantGroup.Image_URL")) and(tgi is None)):
				value=self.extract_var(line)
				if (value==""):
					err_msg=err_msg+"\nYou must provide TenantGroup.Image_URL"
				else:
					tgi=value
					var_set=var_set+1

		if (var_set!=19):
			error=True
			print ("\nError in the configuration file.")
			print (err_msg)

		if (error is False):
			[msg,code]=self.gestore_richieste.send_reset_specs(self.addr, uu, up, uf, ul, st, sn, sd, si, slo, sla, sz, tt, tid, tn, tim, tgt, tgn, tgd, tgi)
			print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
			raw_input("\nPress ENTER to continue.\n")
			self.menu_a()

		else:
			raw_input("\nPress ENTER to continue.\n")
			self.menu_a()

	def set_ihealth_codes(self,fname=None):
		if (fname is None):
			fname=self.ihealth_codes_config_file_name
		print ("\nSelect an option and press ENTER,\nor press ENTER without typing anything to go back to the main menu.")
		print ("\t1\t- I have already a configuration file.")
		sel=raw_input ("\t2\t- I don't have a configuration file. I want it to be generated.\n")
		while ((sel!="1")and(sel!="2")and(sel!="")):
			print ("\nWrong input")
			print ("\nSelect an option and press ENTER,\n or press ENTER without typing anything to go back to the main menu.")
			print ("\t1\t- I have already a configuration file.")
			sel=raw_input ("\t2\t- I don't have a configuration file. I want it to be generated.\n")
		if (sel=="2"):
			self.generate_file("ihealth_codes")
		elif (sel=="1"):
			sel_good=False
			while (sel_good is False):
				print ("\nType the name of the configuration file and press ENTER.")
				print ("Press ENTER without typing anything to use the file '"+fname+"'.")
				print ("Type 'exit' and press ENTER to go back to the main menu.")
				sel_f_name=raw_input()
				if (sel_f_name==""):
					sel_f_name=fname
				if (sel_f_name.upper()=="EXIT"):
					sel_good=True
				else:
					try:
						f=open(sel_f_name,"r")
						f_content=f.readlines()
						f.close()
						sel_good=True
						self.read_ihealth_codes_config(f_content)
					except:
						print ("\nThe file '"+sel_f_name+"' does not exist.\nPress ENTER to continue.")
						sel_good=False
						raw_input()
		else:
			self.menu_a()

	def read_ihealth_codes_config(self, f_content):
		codes=""
		for i in range(len(f_content)):
			line=f_content[i]
			if ((line=="\n")or((len(line))<=1)):
				pass
			else:
				while (line[0]==" "):
					line=line[1:(len(line))]
					if ((len(line))<=1):
						break
				if (line.startswith("#")):
					pass
				else:
					codes=codes+line
		[msg,code]=self.gestore_richieste.send_ihealth_codes(self.addr, codes)
		print ("\nRESPONSE:\tCode:\t"+str(code)+"\n\t\t"+(msg.replace("\n","\n\t\t")))
		raw_input("\nPress ENTER to continue.\n")
		self.menu_a()

if __name__=='__main__':
	try:
		ConfiguratorClient()
	except KeyboardInterrupt:
		print ("\n\nProgram terminated by user keyboard interrupt.\n\n\n")
		sys.exit(0)