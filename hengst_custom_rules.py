"""
HENGST Customer - Custom Rules Configuration
"""

import requests


def get_hengst_custom_rules(log_data, alert_name, abuse_api_key=None, whitelist="NO"):
    """
    HENGST-specific custom whitelist rules
    
    Args:
        log_data: Parsed log data dictionary
        alert_name: Alert name string
        abuse_api_key: AbuseIPDB API key (optional)
        whitelist: Current whitelist status
    
    Returns:
        str: "YES" if any rule matches, otherwise returns current whitelist
    """
    
    # RULE: AbuseIPDB ISP Check for Azure Failed Logins
    try:
        if alert_name == "NTT_azure_multiple_failed_logins" and abuse_api_key:
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
                    
                    if "hengst" in isp:
                        whitelist = "YES"
    except:
        pass
    
    return whitelist
