import random
import string 
import cherrypy
import json
import urllib,urllib2
import requests


class WebServer(object):
	exposed = True

	def __init__(self):
		pass
		
	def GET (self, *uri, **params):
		pass

	def POST (self, * uri, ** params):

		if params['type'] == "post":

			url_or = "http://admin:password@localhost:8080/sitewhere/api/assets/categories/"

			category_id = "fs-patients"

			url = url_or+category_id+"/"+"person"

			print "Request to: "+url

			new_person = {
				"id" : "ant123",
				"name" : "Antanio Proccheddu",
				"imageUrl" : "https://pbs.twimg.com/profile_images/2820092226/5f472909a284640231c9463fcce57374_400x400.jpeg",
				"properties" : {
					"phone.number" : "777-555-1212"
					},
				"userName" : "Antanio",
				"emailAddress" : "antanio@demoserver.com",
				"roles" : [ "dev" ]
				}

			#headers = {"content-type":"application/json"}

			# user_agent = "Chrome/49.0.2623.87"
			# headers = {'User-Agent':user_agent}
			#data = urllib.urlencode(new_person)
			# print data

			data = json.dumps(new_person)
			data=data.replace(": ",":")
			headers = {"content-type":"application/json","X-SiteWhere-Tenant":"sitewhere1234567890"}

			s=requests.Session()
			r=s.post(url,data=data,headers=headers)
			print r.status_code
			print url

			return r.content
			
			# #head = urllib.urlencode(headers)

			# req = urllib2.Request(url,data,headers)
			# try:
			# response = urllib2.urlopen(req)
			# resp = response.read()
			# except urllib2.HTTPError, error:
			# resp = error.read()
			
			# return json.loads(resp)
			# return "post request"

		else:
			return "this is not a post request"

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
	cherrypy.tree.mount (WebServer(),	'/',	conf)
	cherrypy.config.update({'server.socket_port':9090})
	cherrypy.engine.start()	
	cherrypy.engine.block()