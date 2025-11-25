"""
Generic Whitelist Script - Input-Driven Approach
All customer-specific data comes from inputs - NO hardcoded logic
"""

import json

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

# Import custom rules processor
try:
    from custom_rules_processor import process_custom_rules
    
    whitelist = process_custom_rules(
        custom_rules=custom_rules,
        log_data=log_data,
        alert_name=alert_name,
        vt_api_key=vt_api_key,
        abuse_api_key=abuse_api_key,
        current_whitelist=whitelist
    )
except ImportError:
    # Fallback: If custom_rules_processor not available, skip custom rules
    pass
except Exception as e:
    # If custom rules processing fails, continue with current whitelist status
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
