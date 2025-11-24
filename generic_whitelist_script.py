"""
Generic Whitelist Script - Configuration-Driven Approach
Supports multiple clients without hardcoded if/else conditions
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class WhitelistChecker:
    """Generic whitelist checker that uses configuration-driven rules"""
    
    def __init__(self, config: Dict[str, Any], context_inputs: Dict[str, Any]):
        """
        Initialize the whitelist checker
        
        Args:
            config: Client-specific configuration with rules
            context_inputs: Runtime inputs (rawLog, udmEvent, alertName, etc.)
        """
        self.config = config
        self.context_inputs = context_inputs
        self.whitelist = "NO"
        
        # Parse JSON inputs
        self.rawLog = self._parse_json_input("rawLog")
        self.udmEvent = self._parse_json_input("udmEvent")
        self.rawlog = self._parse_json_input("rawlog")  # Some use lowercase
        self.alertName = context_inputs.get("alertName") or context_inputs.get("name")
        
    def _parse_json_input(self, key: str) -> Optional[Dict]:
        """Safely parse JSON input"""
        try:
            value = self.context_inputs.get(key)
            if value:
                return json.loads(value) if isinstance(value, str) else value
        except:
            pass
        return None
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """
        Get value from nested dictionary using dot notation
        Example: 'target.process.file.sha256' -> data['target']['process']['file']['sha256']
        """
        if not data:
            return None
            
        keys = path.split('.')
        value = data
        
        for key in keys:
            # Handle array indexing like 'principal.ip[0]'
            if '[' in key and ']' in key:
                array_key = key.split('[')[0]
                index = int(key.split('[')[1].split(']')[0])
                value = value.get(array_key, [])
                if isinstance(value, list) and len(value) > index:
                    value = value[index]
                else:
                    return None
            else:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return None
                    
            if value is None:
                return None
                
        return value
    
    def check_all_rules(self) -> str:
        """Execute all rules defined in config and return whitelist status"""
        rules = self.config.get("rules", [])
        
        for rule in rules:
            rule_type = rule.get("type")
            
            # Dynamically call the appropriate rule handler
            handler_method = f"_check_{rule_type}"
            if hasattr(self, handler_method):
                try:
                    if getattr(self, handler_method)(rule):
                        self.whitelist = "YES"
                        # Could add 'break' here if you want first match to win
                except Exception as e:
                    # Log error but continue with other rules
                    print(f"Error in rule {rule_type}: {str(e)}")
                    continue
        
        return self.whitelist
    
    # ==================== RULE HANDLERS ====================
    
    def _check_alert_name_list(self, rule: Dict) -> bool:
        """Check if alert name is in the configured list"""
        alert_names = rule.get("alert_names", [])
        return self.alertName in alert_names
    
    def _check_hash_match(self, rule: Dict) -> bool:
        """Check if file hash matches whitelisted hashes"""
        if self.alertName != rule.get("alert_name"):
            return False
            
        if not self.rawLog:
            return False
            
        hash_path = rule.get("hash_path")
        hash_list = [h.lower() for h in rule.get("hash_list", [])]
        
        actual_hash = self._get_nested_value(self.rawLog, hash_path)
        
        if actual_hash and actual_hash.lower() in hash_list:
            return True
            
        return False
    
    def _check_category_ip_description(self, rule: Dict) -> bool:
        """Check category + IP + description combination"""
        if not self.rawLog:
            return False
            
        category = self.rawLog.get("category")
        description = self.rawLog.get("description", "")
        evidence = self.rawLog.get("evidence", [])
        
        # Extract IP address from evidence
        ip_address = next(
            (evidence_item.get("ipAddress") 
             for evidence_item in evidence 
             if evidence_item.get("@odata.type") == "#microsoft.graph.security.ipEvidence"),
            None
        )
        
        whitelisted_categories = rule.get("whitelisted_categories", [])
        whitelisted_ips = rule.get("whitelisted_ips", [])
        description_contains = rule.get("description_contains", "")
        
        if (category in whitelisted_categories and 
            ip_address in whitelisted_ips and 
            description_contains in description):
            return True
            
        return False
    
    def _check_alert_description_match(self, rule: Dict) -> bool:
        """Check if alert name matches and description is in list"""
        if self.alertName != rule.get("alert_name"):
            return False
            
        if not self.rawLog:
            return False
            
        description = self.rawLog.get("description", "")
        description_list = rule.get("description_list", [])
        
        return description in description_list
    
    def _check_product_event_type(self, rule: Dict) -> bool:
        """Check if product event type matches"""
        if not self.udmEvent:
            return False
            
        path = rule.get("path")
        event_types = rule.get("event_types", [])
        
        actual_type = self._get_nested_value(self.udmEvent, path)
        
        return actual_type in event_types
    
    def _check_virustotal_domain_check(self, rule: Dict) -> bool:
        """Check domain reputation via VirusTotal API"""
        if self.alertName != rule.get("alert_name"):
            return False
            
        if not self.rawLog:
            return False
            
        vt_api_key = self.context_inputs.get("vt_api_key")
        if not vt_api_key:
            return False
            
        domain_path = rule.get("domain_path")
        domain = self._get_nested_value(self.rawLog, domain_path)
        
        if not domain:
            return False
            
        criteria = rule.get("criteria", {})
        domain_age_days = criteria.get("domain_age_days", 90)
        malicious_threshold = criteria.get("malicious_threshold", 10)
        
        url = f"https://www.virustotal.com/api/v3/domains/{domain}"
        headers = {"x-apikey": vt_api_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                malicious = data['data']['attributes']['last_analysis_stats']['malicious']
                
                # Check domain age
                creation_time = data['data']['attributes'].get('creation_date')
                if creation_time:
                    creation_time = datetime.utcfromtimestamp(creation_time)
                    now_time = datetime.utcnow()
                    threshold_date = now_time - timedelta(days=domain_age_days)
                    
                    if creation_time > threshold_date or malicious > malicious_threshold:
                        return True
        except Exception as e:
            print(f"VirusTotal API error: {str(e)}")
            
        return False
    
    def _check_abuseipdb_isp_check(self, rule: Dict) -> bool:
        """Check ISP via AbuseIPDB API"""
        if self.alertName != rule.get("alert_name"):
            return False
            
        # Try both rawLog and rawlog (lowercase)
        log_data = self.rawLog or self.rawlog
        if not log_data:
            return False
            
        ip_path = rule.get("ip_path")
        principal_ip = self._get_nested_value(log_data, ip_path)
        
        if not principal_ip:
            return False
            
        abuse_key = self.context_inputs.get("abuse_key")
        if not abuse_key:
            return False
            
        url = f'https://api.abuseipdb.com/api/v2/check?ipAddress={principal_ip}'
        headers = {
            'Accept': 'application/json',
            'Key': abuse_key
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                isp = data.get("data", {}).get("isp", "").lower()
                isp_contains = rule.get("isp_contains", "").lower()
                
                if isp_contains in isp:
                    return True
        except Exception as e:
            print(f"AbuseIPDB API error: {str(e)}")
            
        return False


# ==================== MAIN EXECUTION ====================

def load_config(config_path: str = None, client_id: str = None) -> Dict:
    """
    Load configuration from file or use provided config
    
    Args:
        config_path: Path to JSON config file
        client_id: Client identifier to load specific config
    """
    if config_path:
        with open(config_path, 'r') as f:
            all_configs = json.load(f)
            return all_configs.get(client_id, {"rules": []})
    return {"rules": []}


def check_whitelist(client_id: str, context_inputs: Dict[str, Any], 
                    config_path: str = "whitelist_config.json") -> str:
    """
    Main function to check whitelist status
    
    Args:
        client_id: Client identifier (e.g., 'knf', 'hengst', 'xella')
        context_inputs: Dictionary with inputs (rawLog, alertName, etc.)
        config_path: Path to configuration file
        
    Returns:
        "YES" or "NO"
    """
    config = load_config(config_path, client_id)
    checker = WhitelistChecker(config, context_inputs)
    return checker.check_all_rules()


# ==================== USAGE IN YOUR SCRIPT ====================
# Replace 'CLIENT_ID_HERE' with your client identifier

# Example usage (uncomment and modify):
"""
whitelist = check_whitelist(
    client_id="CLIENT_ID_HERE",  # 'knf', 'hengst', or 'xella'
    context_inputs={
        "rawLog": sw_context.inputs.get("rawLog"),
        "udmEvent": sw_context.inputs.get("udmEvent"),
        "alertName": sw_context.inputs.get("alertName"),
        "name": sw_context.inputs.get("name"),
        "rawlog": sw_context.inputs.get("rawlog"),
        "vt_api_key": sw_context.inputs.get("vt_api_key"),
        "abuse_key": sw_context.inputs.get("abuse_key"),
        "abuse_host": sw_context.inputs.get("abuse_host"),
    }
)

sw_outputs.append({"whitelist": whitelist})
"""
