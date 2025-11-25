"""
Custom Rules Processor - Separate Module for Complex Whitelist Logic
Handles customer-defined complex rules for whitelist checking
"""

import requests
from datetime import datetime, timedelta


def process_custom_rules(custom_rules, log_data, alert_name, vt_api_key=None, abuse_api_key=None, current_whitelist="NO"):
    """
    Process custom rules and return whitelist status
    
    Args:
        custom_rules: List of rule dictionaries with 'type' and 'params'
        log_data: Parsed log data dictionary
        alert_name: Alert name string
        vt_api_key: VirusTotal API key (optional)
        abuse_api_key: AbuseIPDB API key (optional)
        current_whitelist: Current whitelist status (default "NO")
    
    Returns:
        str: "YES" if any rule matches, otherwise returns current_whitelist
    """
    whitelist = current_whitelist
    
    for rule in custom_rules:
        rule_type = rule.get("type")
        params = rule.get("params", {})
        
        try:
            # RULE: Combined Category + IP + Description
            if rule_type == "category_ip_description":
                if _check_category_ip_description(log_data, params):
                    whitelist = "YES"
            
            # RULE: Alert Name + Description Match
            elif rule_type == "alert_description_match":
                if _check_alert_description_match(log_data, alert_name, params):
                    whitelist = "YES"
            
            # RULE: VirusTotal Domain Check
            elif rule_type == "virustotal_domain":
                if vt_api_key and _check_virustotal_domain(log_data, alert_name, vt_api_key, params):
                    whitelist = "YES"
            
            # RULE: AbuseIPDB ISP Check
            elif rule_type == "abuseipdb_isp":
                if abuse_api_key and _check_abuseipdb_isp(log_data, alert_name, abuse_api_key, params):
                    whitelist = "YES"
            
            # RULE: Simple Key-Value Match
            elif rule_type == "key_value":
                if _check_key_value(log_data, params):
                    whitelist = "YES"
            
            # RULE: Nested Path Match
            elif rule_type == "nested_path":
                if _check_nested_path(log_data, params):
                    whitelist = "YES"
        
        except Exception as e:
            # Continue to next rule if this one fails
            pass
    
    return whitelist


# =============================================================================
# RULE HANDLER FUNCTIONS
# =============================================================================

def _check_category_ip_description(log_data, params):
    """Check combined Category + IP + Description rule"""
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
        return True
    
    return False


def _check_alert_description_match(log_data, alert_name, params):
    """Check Alert Name + Description Match rule"""
    required_alert = params.get("alert_name")
    required_descriptions = params.get("descriptions", [])
    description = log_data.get("description", "")
    
    if alert_name == required_alert and description in required_descriptions:
        return True
    
    return False


def _check_virustotal_domain(log_data, alert_name, vt_api_key, params):
    """Check VirusTotal Domain reputation rule"""
    required_alert = params.get("alert_name")
    if alert_name != required_alert:
        return False
    
    domain_path = params.get("domain_path", "target.administrativeDomain")
    domain_age_days = params.get("domain_age_days", 90)
    malicious_threshold = params.get("malicious_threshold", 10)
    
    # Navigate nested path
    domain = log_data
    for key in domain_path.split('.'):
        domain = domain.get(key, {})
        if not isinstance(domain, dict):
            break
    
    if not isinstance(domain, str):
        return False
    
    try:
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
                    return True
    except Exception as e:
        pass
    
    return False


def _check_abuseipdb_isp(log_data, alert_name, abuse_api_key, params):
    """Check AbuseIPDB ISP rule"""
    required_alert = params.get("alert_name")
    if alert_name != required_alert:
        return False
    
    isp_contains = params.get("isp_contains", "").lower()
    
    # Get IP from principal
    principal_ips = log_data.get("principal", {}).get("ip", [])
    principal_ip = principal_ips[0] if isinstance(principal_ips, list) and principal_ips else None
    
    if not principal_ip:
        return False
    
    try:
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
                return True
    except Exception as e:
        pass
    
    return False


def _check_key_value(log_data, params):
    """Check simple Key-Value Match rule"""
    field = params.get("field")
    value = params.get("value")
    
    if log_data.get(field) == value:
        return True
    
    return False


def _check_nested_path(log_data, params):
    """Check Nested Path Match rule"""
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
        return True
    
    return False


# =============================================================================
# HELPER FUNCTION TO ADD NEW RULE TYPES
# =============================================================================

def add_custom_rule_handler(rule_type, handler_function):
    """
    Add a new custom rule handler dynamically
    
    Args:
        rule_type: String identifier for the rule type
        handler_function: Function that takes (log_data, params) and returns bool
    
    Example:
        def my_custom_check(log_data, params):
            return log_data.get("field") == params.get("value")
        
        add_custom_rule_handler("my_custom_rule", my_custom_check)
    """
    # This would require refactoring process_custom_rules to use a registry pattern
    # Left as a placeholder for future enhancement
    pass
