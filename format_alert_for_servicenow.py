import json
from datetime import datetime

#!#!#!#!#!##!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!# Custom DB WorkNotes and Description #!#!#!#!#!##!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#
import validators
import ipaddress
import ast
from pyjsonata import jsonata


################## Definitions ##################
def get_nested(data, keys):
	current = ''
	def replace_dots(value):
		try:
			ipaddress.ip_address(value)
			return str(value).replace(".", "[.]")
		except ValueError:
			if validators.domain(value):
				return value.replace(".", "[.]")
			if not (value.startswith('http://') or value.startswith('https://')):
				url_with_scheme = f'http://forced.{value}'
			else:
				url_with_scheme = value
			if validators.url(url_with_scheme):
				return url_with_scheme.replace(".", "[.]").replace('http://forced[.]','')
			else:
				return value.replace(".", "[.]")
			return str(value)
	current = jsonata(keys, data)
	if current == "undefined":
		return ""
	if isinstance(json.loads(current), list):
		current = ', '.join(map(str, list(set(json.loads(current)))))
	results = replace_dots(current.replace('\"', ''))
	return results
  
def get_nested_value(data, keys):
    for key in keys:
        if key['type'].lower() == 'path':
            result = get_nested(data, key['value'])
            if result == '':
                continue
            else:
                break
        elif key['type'].lower() == 'extract_domain_from_path':
            try:
            	result = get_nested(data, key['value']).split('@')[-1]
            except:
                result = ''
            if result == '':
                continue
            else:
                break
        else:
            result = key['value']
            break
    return result
################## End of Definitions ##################

################## Get DB Query Results from Input ##################
# Get the cursor execution results from input instead of querying the database
result = []
try:
    # Expecting the cursor results to be passed as an input parameter
    cursor_results = sw_context.inputs.get("cursor_results", "[]")
    if isinstance(cursor_results, str):
        result = json.loads(cursor_results)
    elif isinstance(cursor_results, list):
        result = cursor_results
    else:
        result = []
except Exception as e:
    print(f"Error parsing cursor_results: {e}")
    result = []

################## End of Get DB Query Results ##################

################## WN and Desc Creation ##################
work_notes = ''
description = ''
data = sw_context.inputs["current_addInfo"]

if len(result) > 0:
  tmp = result[0]
  try:
    wk_notes = ast.literal_eval(tmp['work_notes'])
    for element in wk_notes:
        work_notes += '\n' + element['title'] + ': ' + get_nested_value(data, element['source'])
  except:
    pass
  try:
    desc = ast.literal_eval(tmp['description'])
    description += 'Alert Description: ' + sw_context.inputs["description"] + '\n'
    for element in desc:
      try:
        val = get_nested_value(data, element['source'])
        if val != '':
          description += '\n' + element['title'] + ': ' + val
      except Exception as e:
        print(e)
    description += '\n\n' +'Event Link: ' + sw_context.inputs["event-link"]
  except Exception as e:
    pass
else:
  description = "{}\n\n{}".format(sw_context.inputs["description"], sw_context.inputs["event-link"])
################## End of WN and Desc Creation ##################
#!#!#!#!#!##!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!# End of Custom DB WorkNotes and Description #!#!#!#!#!##!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#


def parse_datetime(input_time):
  try:
    return datetime.strptime(input_time, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
  except ValueError:
    return datetime.strptime(input_time, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")


mitre_tactics_id = {
  "TA0001": "Initial Access",
  "TA0002": "Execution",
  "TA0003": "Persistence",
  "TA0004": "Privilege Escalation",
  "TA0005": "Defense Evasion",
  "TA0006": "Credential Access",
  "TA0007": "Discovery",
  "TA0008": "Lateral Movement",
  "TA0009": "Collection",
  "TA0010": "Exfiltration",
  "TA0011": "Command and Control",
  "TA0012": "Impact"
};
mitre_tactics =  {
  "InitialAccess": "Initial Access",
  "Execution": "Execution",
  "Persistence": "Persistence",
  "PrivilegeEscalation": "Privilege Escalation",
  "DefenseEvasion": "Defense Evasion",
  "CredentialAccess": "Credential Access",
  "Discovery": "Discovery",
  "LateralMovement": "Lateral Movement",
  "Collection": "Collection",
  "Exfiltration": "Exfiltration",
  "CommandAndControl": "Command and Control",
  "Impact": "Impact"
};

Additional_Info = {}
Additional_Info["indicators"] = sw_context.inputs["indicators"]


SNOW_ALERT = {}

SNOW_ALERT["u_title"] = sw_context.inputs["alert-name"]
SNOW_ALERT["classification"] = "Security"
SNOW_ALERT["description"] = description
SNOW_ALERT["u_company"] = sw_context.inputs["company"]
SNOW_ALERT["source"] = sw_context.inputs["alert-source"]
SNOW_ALERT["u_detection_time"] = parse_datetime(sw_context.inputs["detected-datetime"])
SNOW_ALERT["u_risk_score"] = sw_context.inputs["risk-score"]
SNOW_ALERT["severity"] = sw_context.inputs["severity"].lower()
SNOW_ALERT["u_event_link"] = sw_context.inputs["event-link"]
SNOW_ALERT["additional_info"] = Additional_Info
SNOW_ALERT["message_key"] = sw_context.inputs["tracking-id"]
#SNOW_ALERT[""] = sw_context.inputs[""];

sw_outputs.append({"snow-alert":SNOW_ALERT})
