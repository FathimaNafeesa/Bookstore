"""
KNF Customer - Custom Rules Configuration
"""

import requests
from datetime import datetime, timedelta


def get_knf_custom_rules(log_data, alert_name, vt_api_key=None, whitelist="NO"):
    """
    KNF-specific custom whitelist rules
    
    Args:
        log_data: Parsed log data dictionary
        alert_name: Alert name string
        vt_api_key: VirusTotal API key (optional)
        whitelist: Current whitelist status
    
    Returns:
        str: "YES" if any rule matches, otherwise returns current whitelist
    """
    
    # RULE 1: Category + IP + Description Check
    try:
        category = log_data.get("category")
        description = log_data.get("description", "")
        evidence = log_data.get("evidence", [])
        
        ip_address = next(
            (e.get("ipAddress") for e in evidence 
             if e.get("@odata.type") == "#microsoft.graph.security.ipEvidence"),
            None
        )
        
        whitelisted_categories = ["SuspiciousActivity"]
        whitelisted_ips = [
            "83.135.49.100", "5.45.7.100", "178.174.74.158", "93.64.21.162",
            "109.164.253.18", "62.84.220.189", "182.74.194.122", "81.62.137.122",
            "112.217.96.26", "195.67.15.34", "83.144.238.14", "81.62.221.10",
            "118.238.219.96", "124.110.102.16", "12.26.44.228", "108.58.132.154",
            "77.159.255.36", "90.80.222.57", "193.117.132.34", "1.119.186.210",
            "101.204.45.250", "210.13.71.132", "116.227.23.83", "219.134.241.42"
        ]
        
        if (category in whitelisted_categories and 
            ip_address in whitelisted_ips and 
            "Mass download by a single user" in description):
            whitelist = "YES"
    except:
        pass
    
    # RULE 2: InitialAccess Alert with Description Match
    try:
        if alert_name == "InitialAccess":
            description = log_data.get("description", "")
            alert_descriptions = [
                "This alert is triggered when any email message is reported as junk by users -V1.0.0.0",
                "Malicious emails were delivered and later removed -V1.0.0.2",
                "Emails with malicious URL that were delivered and later removed -V1.0.0.3",
                "Email messages containing malicious URL removed after delivery",
                "Email messages containing malicious file removed after delivery",
                "Email reported by user as junk",
                "Email reported by user as not junk",
                "Email messages from a campaign removed after delivery",
                "Email messages from a campaign were delivered and later removed -V1.0.0.2"
            ]
            
            if description in alert_descriptions:
                whitelist = "YES"
    except:
        pass
    
    # RULE 3: VirusTotal Domain Check for External Teams User
    try:
        if alert_name == "External_user_added_to_Teams_M365" and vt_api_key:
            admin_domain = log_data.get("target", {}).get("administrativeDomain")
            
            if admin_domain:
                url = f"https://www.virustotal.com/api/v3/domains/{admin_domain}"
                headers = {"x-apikey": vt_api_key}
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    malicious = data['data']['attributes']['last_analysis_stats']['malicious']
                    
                    creation_time = data['data']['attributes'].get('creation_date')
                    if creation_time:
                        creation_time = datetime.utcfromtimestamp(creation_time)
                        now_time = datetime.utcnow()
                        three_months_ago = now_time - timedelta(days=90)
                        
                        if creation_time > three_months_ago or malicious > 10:
                            whitelist = "YES"
    except:
        pass
    
    return whitelist
