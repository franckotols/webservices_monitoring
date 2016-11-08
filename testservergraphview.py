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

class TestServer(object):
	exposed = True

	def __init__(self):

		self.id = id		
		
	def GET (self, *uri, **params):

		vector = [

			["2016-1-12",
				12],
			["2016-1-13",
				13],
			["2016-1-14",
				11],
			["2016-1-16",
				10],
			["2016-1-17",
				12],
			["2016-1-18",
				14],
			["2016-1-19",
				12],
			["2016-1-20",
				17]
		]
		return json.dumps({"results":vector})
			
	def POST (self, * uri, ** params):
		
		pass

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
	cherrypy.tree.mount (TestServer(),	'/test',	conf)
	cherrypy.server.socket_host = '192.168.137.1'
	cherrypy.config.update({'server.socket_port':9090})
	cherrypy.engine.start()	
	cherrypy.engine.block()