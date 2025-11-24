# Generic Whitelist Script - Usage Guide

## Overview
**One script, all customers.** No customer-specific logic in the code. Everything is input-driven.

## How It Works

### The Script (`generic_whitelist.py`)
- Contains ZERO hardcoded customer data
- Receives all whitelist data as inputs
- Performs generic checks against provided lists
- Returns "YES" or "NO"

### Each Customer
- Provides their own whitelist data as inputs
- Data stored in customer config/database/playbook
- Same script runs for everyone

## Input Parameters

### Basic Inputs
```python
{
    "rawLog": "{}",           # JSON string of raw log
    "rawlog": "{}",           # Alternative lowercase variant
    "udmEvent": "{}",         # JSON string of UDM event
    "alertName": "alert",     # Alert name (or "name")
}
```

### Simple Whitelist Lists
```python
{
    "whitelist_alert_names": [],      # List of alert names to whitelist
    "whitelist_hashes": [],           # List of SHA256 hashes to whitelist
    "whitelist_ips": [],              # List of IP addresses to whitelist
    "whitelist_categories": [],       # List of categories to whitelist
    "whitelist_udm_event_types": [],  # List of UDM event types to whitelist
    "whitelist_descriptions": [],     # List of descriptions to whitelist
}
```

### API Keys (for external checks)
```python
{
    "vt_api_key": "key",      # VirusTotal API key
    "abuse_key": "key",       # AbuseIPDB API key
}
```

### Complex Rules
```python
{
    "custom_rules": [
        {
            "type": "rule_type",
            "params": {...}
        }
    ]
}
```

## Supported Rule Types

### 1. Simple List Checks (Automatic)
Just provide the lists - no custom rules needed:
- Alert name in list
- Hash in list
- IP in list
- Category in list
- Description in list
- UDM event type in list

### 2. `category_ip_description`
Whitelist if category + IP + description all match
```python
{
    "type": "category_ip_description",
    "params": {
        "category": "SuspiciousActivity",
        "ips": ["83.135.49.100", "5.45.7.100"],
        "description_contains": "Mass download by a single user"
    }
}
```

### 3. `alert_description_match`
Whitelist if alert name matches AND description is in list
```python
{
    "type": "alert_description_match",
    "params": {
        "alert_name": "InitialAccess",
        "descriptions": ["Email with malicious URL", "Another description"]
    }
}
```

### 4. `virustotal_domain`
Check domain age and reputation via VirusTotal
```python
{
    "type": "virustotal_domain",
    "params": {
        "alert_name": "External_user_added_to_Teams_M365",
        "domain_path": "target.administrativeDomain",
        "domain_age_days": 90,
        "malicious_threshold": 10
    }
}
```

### 5. `abuseipdb_isp`
Check if IP's ISP matches string
```python
{
    "type": "abuseipdb_isp",
    "params": {
        "alert_name": "NTT_azure_multiple_failed_logins",
        "isp_contains": "hengst"
    }
}
```

### 6. `key_value`
Simple field equals value check
```python
{
    "type": "key_value",
    "params": {
        "field": "status",
        "value": "resolved"
    }
}
```

### 7. `nested_path`
Check nested field value
```python
{
    "type": "nested_path",
    "params": {
        "path": "target.user.email",
        "value": "admin@example.com"
    }
}
```

## Complete Example: KNF Customer

```python
# In your playbook or config system, store this for KNF:

knf_config = {
    "whitelist_alert_names": [
        "Email reported by user as junk",
        "Email reported by user as not junk"
    ],
    
    "whitelist_hashes": [
        "FE7A9EA0905151A907E248E91655EC36D9481BF7DB839ADED6D0444A66D8D730"
    ],
    
    "whitelist_ips": [
        "83.135.49.100",
        "5.45.7.100"
    ],
    
    "whitelist_categories": ["SuspiciousActivity"],
    
    "whitelist_udm_event_types": [
        "MCAS_ALERT_CABINET_EVENT_MATCH_FILE"
    ],
    
    "vt_api_key": "your_vt_key",
    
    "custom_rules": [
        {
            "type": "virustotal_domain",
            "params": {
                "alert_name": "External_user_added_to_Teams_M365",
                "domain_path": "target.administrativeDomain",
                "domain_age_days": 90,
                "malicious_threshold": 10
            }
        }
    ]
}

# When running the script, merge with runtime data:
sw_context.inputs = {
    **knf_config,  # Customer config
    "rawLog": actual_log,  # Runtime data
    "udmEvent": actual_event,  # Runtime data
    "alertName": actual_alert  # Runtime data
}

# Run generic_whitelist.py
# Result: whitelist = "YES" or "NO"
```

## Adding a New Customer

1. Create their config dictionary with their whitelist data
2. Store it in your config system (database, file, etc.)
3. Pass it as inputs when running the script
4. **Done! No code changes needed.**

## Adding New Check Types

To add a new rule type, add an `elif` block in the custom rules section:

```python
elif rule_type == "my_new_check":
    field = params.get("some_param")
    # Your logic here
    if condition_met:
        whitelist = "YES"
```

## Benefits

✅ **Zero hardcoded customer data**  
✅ **Same script for all customers**  
✅ **Easy to add new customers** - just add config  
✅ **Easy to maintain** - one place to fix bugs  
✅ **Testable** - test with different inputs  
✅ **Flexible** - supports simple lists AND complex rules  

## Migration from Your Current Scripts

**Before (3 separate scripts):**
```python
# knf_script.py - 100 lines with hardcoded KNF data
# hengst_script.py - 50 lines with hardcoded HENGST data  
# xella_script.py - 20 lines with hardcoded XELLA data
```

**After (1 script + configs):**
```python
# generic_whitelist.py - 200 lines, works for ALL customers
# knf_config - just data
# hengst_config - just data
# xella_config - just data
```

Update the customer configs, not the script! 🎉
