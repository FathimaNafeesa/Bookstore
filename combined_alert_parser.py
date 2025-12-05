import ast
import json

# SEVERITY MAPPING
severity_map = {
    "1": "Critical",
    "2": "High",
    "3": "Medium",
    "4": "Low",
    "5": "Low"
}

# Parse Alert
output_data = {}

# Parse severity (SNow only accepts low, medium, high or critical as severity)
# If severity is INFORMATIONAL, set it to Low
snowSeverity = ""
udmEvent = action_inputs.get("udmEvent", "")

try:
    snowSeverity = action_inputs.get("severity", "")
    udmEvent = json.loads(udmEvent)
    if snowSeverity == "":
        snowSeverity = udmEvent["securityResult"][0]["severity"]
    if snowSeverity.upper() == "INFORMATIONAL":
        snowSeverity = "Low"
except:
    pass

# EXTRA TRY FOR INFORMATIONAL -> LOW
try:
    if snowSeverity.upper() == "INFORMATIONAL":
        snowSeverity = "Low"
except:
    pass

# MISSING SEVERITY FROM CHRONICLE FOR SPECIFIC ALERTS
try:
    alert_name = action_inputs.get("name", "")
    if alert_name == "suspicious_rundll32_activity":
        snowSeverity = "Medium"
    elif alert_name == "rundll32_internet_connection":
        snowSeverity = "Low"
except:
    pass

# Apply severity mapping
severity = snowSeverity

try:
    severity = severity_map[snowSeverity]
except:
    pass

# Validate severity
if len(severity) <= 1:
    severity = "Low"

if severity not in ["Low", "Medium", "High", "Critical"]:
    severity = "Low"

output_data['snowSeverity'] = severity

# Parse alert description
udmEvent = action_inputs.get("udmEvent", "")
rawLog = action_inputs.get("rawLog", "")
description = action_inputs.get("description", "")

try:
    udmEvent = json.loads(udmEvent)
    description = udmEvent["securityResult"][0]["description"]
except:
    pass

output_data['description'] = description

# Parse alert name
alertName = action_inputs.get("name", "")

try:
    udmEvent = json.loads(action_inputs.get("udmEvent", ""))
    # Try ruleName first, fall back to summary
    try:
        alertName = udmEvent["securityResult"][0]["ruleName"]
    except:
        alertName = udmEvent["securityResult"][0]["summary"]
except:
    pass

output_data["alertName"] = alertName

# Parse event-link
uris = action_inputs.get("uri", "")
parsed_uri = "not available"

try:
    # Handle different URI patterns
    for uri in uris:
        # Transform knf- URIs to ndr1-
        if uri.startswith("https://knf-"):
            parsed_uri = uri.split("://")[0] + "://ndr1-" + uri.split("://")[-1]
            break
        # Accept ndr1- and helaba-europe URIs as-is
        elif uri.startswith("https://ndr1-") or uri.startswith("https://helaba-europe"):
            parsed_uri = uri
            break
except:
    # If uris is a single string (not iterable), use it directly
    try:
        if isinstance(uris, str):
            parsed_uri = uris
    except:
        pass

output_data['eventLink'] = parsed_uri

sw_outputs.append(output_data)
