import random
import requests
import string 
import cherrypy
import json
import urllib
import urllib2
import operator
from sys import argv
import pymongo
from pymongo import MongoClient
from pymongo import Connection





class TestMongo(object):
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
	
		pass

	def POST (self, * uri, ** params):

		pass

	def PUT (self, * uri, ** params): 
		pass

	def DELETE (self, * uri, ** params):
		pass

if __name__ == '__main__': 
	
	# conf = {
	# 	'/': {
	# 		'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
	# 		'tools.sessions.on': True, 
	# 	}
	# }
	# cherrypy.tree.mount (RegistrationServer(),	'/registration',	conf)
	# cherrypy.tree.mount (AuthenticationServer(),	'/authentication',	conf)
	# cherrypy.tree.mount (DiseaseServer(),	'/diseases',	conf)
	# cherrypy.tree.mount (SearchPatientServer(),	'/searchPatient',	conf)
	# cherrypy.server.socket_host = '192.168.173.1'
	# cherrypy.config.update({'server.socket_port':9090})
	# cherrypy.engine.start()	
	# cherrypy.engine.block()

	# url = "http://localhost:27017/sitewhere"
	# s=requests.Session()
	# r = s.get(url)
	# result = r.content
	# print result #It prints "It looks like you are trying to access MongoDB over HTTP on the native driver port."

	#client = MongoClient('localhost', 27017)
	#db = client['testdb'] # Retriving an existing databes inside MongoDB. (Alternative command: "db = client.test_database") . If doesn't exist it is automatically created
	
	con = Connection()

	db = con['tenant-PATIENT_LIST_tenant_id']
	assignments = db['assignments']
	

	docu = assignments.find()

	for k in docu:
		print "\n\n"
		print k["token"]
