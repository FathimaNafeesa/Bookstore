"""
Generic Whitelist Script - Input-Driven Approach
All customer-specific data comes from inputs - NO hardcoded logic
"""

import json
import requests
from datetime import datetime, timedelta

whitelist = "NO"

# =============================================================================
# 1. PARSE INPUTS (PROVIDED BY PLAYBOOK/CUSTOMER CONFIG)
# =============================================================================

# Parse JSON inputs safely
def safe_json_parse(input_str, default=None):
    try:
        if input_str:
            return json.loads(input_str) if isinstance(input_str, str) else input_str
    except:
        pass
    return default if default is not None else {}

# Get alert data from action_inputs
alert_data = action_inputs.get("alert", {})

# Parse rawlog and udmevent from alert data
rawLog = safe_json_parse(alert_data.get("cfs.rawlog"))
rawlog = safe_json_parse(alert_data.get("cfs.rawlog"))  # Same source, kept for compatibility
udmEvent = safe_json_parse(alert_data.get("cfs.udmevent"))

# Use whichever log is available
log_data = rawLog or rawlog

# Alert name from cfs.name
alert_name = alert_data.get("cfs.name")

# Customer ID (optional, for logging/debugging)
customer_id = alert_data.get("cfs.customer_id")

# =============================================================================
# 2. CUSTOMER-PROVIDED WHITELIST DATA (LISTS)
# =============================================================================

whitelist_alert_names = action_inputs.get("whitelist_alert_names", [])
whitelist_hashes = action_inputs.get("whitelist_hashes", [])
whitelist_ips = action_inputs.get("whitelist_ips", [])
whitelist_categories = action_inputs.get("whitelist_categories", [])
whitelist_udm_event_types = action_inputs.get("whitelist_udm_event_types", [])
whitelist_descriptions = action_inputs.get("whitelist_descriptions", [])

# =============================================================================
# 3. CUSTOMER-PROVIDED API KEYS (FOR EXTERNAL CHECKS)
# =============================================================================

vt_api_key = action_inputs.get("vt_api_key")
abuse_api_key = action_inputs.get("abuse_key")

# =============================================================================
# 4. CUSTOMER-PROVIDED RULES (COMPLEX CONDITIONS)
# =============================================================================

# Format: [{"type": "rule_type", "params": {...}}]
custom_rules = action_inputs.get("custom_rules", [])

# =============================================================================
# 5. GENERIC WHITELIST CHECKS (NO CUSTOMER-SPECIFIC LOGIC)
# =============================================================================

# A. ALERT NAME CHECK
if alert_name in whitelist_alert_names:
    whitelist = "YES"

# B. HASH CHECK (checks common hash locations)
try:
    # Check target.process.file.sha256
    sha256 = log_data.get("target", {}).get("process", {}).get("file", {}).get("sha256", "").lower()
    if sha256 and sha256 in [h.lower() for h in whitelist_hashes]:
        whitelist = "YES"
except:
    pass

# C. IP CHECK (checks all possible IP locations)
all_ips = set()

try:
    # principal.ip (array)
    principal_ips = log_data.get("principal", {}).get("ip", [])
    if isinstance(principal_ips, list):
        all_ips.update(principal_ips)
    elif principal_ips:  # single IP
        all_ips.add(principal_ips)
    
    # evidence.ipAddress
    evidence = log_data.get("evidence", [])
    if isinstance(evidence, list):
        for e in evidence:
            ip_value = e.get("ipAddress")
            if ip_value:
                all_ips.add(ip_value)
    
    # Check if any IP is whitelisted
    if any(ip in whitelist_ips for ip in all_ips):
        whitelist = "YES"
except:
    pass

# D. CATEGORY CHECK
try:
    category = log_data.get("category")
    if category in whitelist_categories:
        whitelist = "YES"
except:
    pass

# E. DESCRIPTION CHECK
try:
    description = log_data.get("description", "")
    if description in whitelist_descriptions:
        whitelist = "YES"
except:
    pass

# F. UDM EVENT TYPE CHECK
try:
    event_type = udmEvent.get("metadata", {}).get("productEventType")
    if event_type in whitelist_udm_event_types:
        whitelist = "YES"
except:
    pass

# =============================================================================
# 6. CUSTOM RULES (CUSTOMER-DEFINED COMPLEX LOGIC)
# =============================================================================

for rule in custom_rules:
    rule_type = rule.get("type")
    params = rule.get("params", {})
    
    try:
        # RULE: Combined Category + IP + Description
        if rule_type == "category_ip_description":
            category = log_data.get("category")
            description = log_data.get("description", "")
            evidence = log_data.get("evidence", [])
            
            ip_address = next(
                (e.get("ipAddress") for e in evidence 
                 if e.get("@odata.type") == "#microsoft.graph.security.ipEvidence"),
                None
            )
            
            required_category = params.get("category")
            required_ips = params.get("ips", [])
            description_contains = params.get("description_contains", "")
            
            if (category == required_category and 
                ip_address in required_ips and 
                description_contains in description):
                whitelist = "YES"
        
        # RULE: Alert Name + Description Match
        elif rule_type == "alert_description_match":
            required_alert = params.get("alert_name")
            required_descriptions = params.get("descriptions", [])
            description = log_data.get("description", "")
            
            if alert_name == required_alert and description in required_descriptions:
                whitelist = "YES"
        
        # RULE: VirusTotal Domain Check
        elif rule_type == "virustotal_domain":
            if not vt_api_key:
                continue
                
            required_alert = params.get("alert_name")
            if alert_name != required_alert:
                continue
                
            domain_path = params.get("domain_path", "target.administrativeDomain")
            domain_age_days = params.get("domain_age_days", 90)
            malicious_threshold = params.get("malicious_threshold", 10)
            
            # Navigate nested path
            domain = log_data
            for key in domain_path.split('.'):
                domain = domain.get(key, {})
                if not isinstance(domain, dict):
                    break
            
            if isinstance(domain, str):
                url = f"https://www.virustotal.com/api/v3/domains/{domain}"
                headers = {"x-apikey": vt_api_key}
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    malicious = data['data']['attributes']['last_analysis_stats']['malicious']
                    
                    creation_time = data['data']['attributes'].get('creation_date')
                    if creation_time:
                        creation_time = datetime.utcfromtimestamp(creation_time)
                        now_time = datetime.utcnow()
                        threshold_date = now_time - timedelta(days=domain_age_days)
                        
                        if creation_time > threshold_date or malicious > malicious_threshold:
                            whitelist = "YES"
        
        # RULE: AbuseIPDB ISP Check
        elif rule_type == "abuseipdb_isp":
            if not abuse_api_key:
                continue
                
            required_alert = params.get("alert_name")
            if alert_name != required_alert:
                continue
                
            isp_contains = params.get("isp_contains", "").lower()
            
            # Get IP from principal
            principal_ips = log_data.get("principal", {}).get("ip", [])
            principal_ip = principal_ips[0] if isinstance(principal_ips, list) and principal_ips else None
            
            if principal_ip:
                url = f'https://api.abuseipdb.com/api/v2/check?ipAddress={principal_ip}'
                headers = {
                    'Accept': 'application/json',
                    'Key': abuse_api_key
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    isp = data.get("data", {}).get("isp", "").lower()
                    
                    if isp_contains in isp:
                        whitelist = "YES"
        
        # RULE: Simple Key-Value Match
        elif rule_type == "key_value":
            field = params.get("field")
            value = params.get("value")
            
            if log_data.get(field) == value:
                whitelist = "YES"
        
        # RULE: Nested Path Match
        elif rule_type == "nested_path":
            path = params.get("path")  # e.g., "securityResult[0].ruleName"
            value = params.get("value")
            
            current = log_data
            for key in path.split('.'):
                if '[' in key:
                    # Handle array indexing
                    array_key = key.split('[')[0]
                    index = int(key.split('[')[1].split(']')[0])
                    current = current.get(array_key, [])[index]
                else:
                    current = current.get(key, {})
                
                if not current:
                    break
            
            if current == value:
                whitelist = "YES"
    
    except Exception as e:
        # Continue to next rule if this one fails
        pass

# =============================================================================
# 7. OUTPUT
# =============================================================================

# Return result (adjust based on your platform's output method)
# Option 1: If using sw_outputs
try:
    sw_outputs.append({"whitelist": whitelist})
except:
    pass

# Option 2: If returning directly
# return {"whitelist": whitelist}

# Option 3: If setting action_outputs
try:
    action_outputs = {"whitelist": whitelist}
except:
    pass
