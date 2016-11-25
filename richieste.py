import requests
import urllib
import json

#GET
#params={"physician_ID":"", "api":"get_current_variables_ranges_for_one_patient", "specs":{"patient_ID":"ptrgpp88l01c342z-giuseppe-petralia"}}

#PUT
params={"physician_ID":"", "api":"set_variable_range_for_one_patient", "specs":{"patient_ID":"ptrgpp88l01c342z-giuseppe-petralia", "variable":"systolic", "new_min":11, "new_max":200}}

#PUT
#params={"physician_ID":"", "api":"set_variable_range_for_all_patients", "specs":{"variable":"systolic", "new_min":100, "new_max":200}}

#GET
#params={"physician_ID":"francesco-tolu-1881989", "api":"get_patient_data", "specs":{"patient_ID":"ptrgpp88l01c342z-giuseppe-petralia", "from_day":"2016-11-12", "from_hour":"12:05"}}#, "till_day":"2016-10-31", "till_hour":"12:50"}}

#GET
#params={"physician_ID":"francesco-tolu-1881989", "api":"get_alerts_read_and_notread", "specs":{}}

#PUT
#params={"physician_ID":"francesco-tolu-1881989", "api":"change_alert_status", "specs":{"alert_id": "582bbfaae4b0fa9aad54638b", "new_status": "switch"}}

#GET
#params={"physician_ID":"francesco-tolu-1881989", "api":"get_alert_info_from_alert_id", "specs":{"alert_ID":"581cb277e4b07909421c69e3"}}

#GET
#params={"physician_ID":"francesco-tolu-1881989", "api":"get_list_of_not_read_alerts", "specs":{}}

#params={"physician_ID":"francesco-tolu-1881989", "api":"", "specs":{}}

addr="https://giupe.webfactional.com/health"
sec=urllib.urlencode(params)
s=requests.Session()
r=s.put(addr,params=sec, verify=False)
result=r.content
print r.content
try:
	result = json.loads(result)
	result = json.dumps(result, indent=4, sort_keys=True)
	print ("STATUS CODE:\t"+str(r.status_code))
	print ("\nMESSAGE:\t"+str(result))
except:
	pass