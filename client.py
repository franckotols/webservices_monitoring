import json
import urllib2
import urllib 



if __name__ == '__main__':

	url_or = 'http://localhost:9090/' 


	print "....."
	print "Simple Client to make requests to SiteWhere (localhost:8080)"
	print "....."
	print "Insert comand "
	print "1 = New asset person - POST REQUEST"
	print "2 = Create New Asset Category - POST REQUEST"
	# print "3 = "
	# print "4 = "
	# print "5 = "
	# print "6 = "
	# print "7 = "
	print "'exit' for quit program"

	command = "default"
	while command!= "exit":

		command = raw_input("Comand: ")
		if command == "1":

			type_req = raw_input("Type of request: ")
			values = {"type":type_req}

			data = urllib.urlencode(values)
			# url = url_or+"?"+data
			# print "Request to: " + url
			req = urllib2.Request(url_or,data)
			
			try:
				response = urllib2.urlopen(req)
				resp = response.read()
			except urllib2.HTTPError, error:
				resp = error.read()

			#resp2 = json.loads(resp)

			print resp

		#elif command == "2":
