# Generic Whitelist Script - Configuration-Driven Solution

## Overview
This is a **single, reusable script** that replaces your three client-specific scripts (KNF, HENGST, XELLA) without using if/else conditions based on client names.

## How It Works

### 1. **Configuration-Driven Approach**
- All client-specific logic is stored in `whitelist_config.json`
- Each client has a set of "rules" that define whitelist conditions
- The script dynamically applies rules based on configuration

### 2. **No Client-Specific Conditionals**
- No `if client == "KNF"` or similar statements
- Client identifier is passed as a parameter
- Same code works for all clients

## Files

```
whitelist_config.json              # Configuration for all clients
generic_whitelist_script.py        # Main reusable script
whitelist_integration_example.py   # Examples of how to integrate
```

## Supported Rule Types

### 1. `alert_name_list`
Whitelist if alert name is in a predefined list
```json
{
  "type": "alert_name_list",
  "alert_names": ["Email reported by user as junk", "Another alert"]
}
```

### 2. `hash_match`
Whitelist if file hash matches for specific alert
```json
{
  "type": "hash_match",
  "alert_name": "wannacry_ransomware_via_sysmon",
  "hash_path": "target.process.file.sha256",
  "hash_list": ["FE7A9EA0905151A907E248E91655EC36D9481BF7DB839ADED6D0444A66D8D730"]
}
```

### 3. `category_ip_description`
Whitelist based on category + IP + description combination
```json
{
  "type": "category_ip_description",
  "whitelisted_categories": ["SuspiciousActivity"],
  "whitelisted_ips": ["83.135.49.100", "5.45.7.100"],
  "description_contains": "Mass download by a single user"
}
```

### 4. `alert_description_match`
Whitelist if alert name matches and description is in list
```json
{
  "type": "alert_description_match",
  "alert_name": "InitialAccess",
  "description_list": ["Emails with malicious URL..."]
}
```

### 5. `product_event_type`
Whitelist based on product event type in UDM event
```json
{
  "type": "product_event_type",
  "event_types": ["MCAS_ALERT_CABINET_EVENT_MATCH_FILE"],
  "path": "metadata.productEventType"
}
```

### 6. `virustotal_domain_check`
Check domain age and reputation via VirusTotal API
```json
{
  "type": "virustotal_domain_check",
  "alert_name": "External_user_added_to_Teams_M365",
  "domain_path": "target.administrativeDomain",
  "criteria": {
    "domain_age_days": 90,
    "malicious_threshold": 10
  }
}
```

### 7. `abuseipdb_isp_check`
Check ISP via AbuseIPDB API
```json
{
  "type": "abuseipdb_isp_check",
  "alert_name": "NTT_azure_multiple_failed_logins",
  "ip_path": "principal.ip[0]",
  "isp_contains": "hengst"
}
```

## Usage

### Simple Integration
```python
from generic_whitelist_script import check_whitelist

# Pass client_id as parameter (from env var, input, etc.)
whitelist = check_whitelist(
    client_id="knf",  # or "hengst", "xella"
    context_inputs={
        "rawLog": sw_context.inputs.get("rawLog"),
        "udmEvent": sw_context.inputs.get("udmEvent"),
        "alertName": sw_context.inputs.get("alertName"),
        "vt_api_key": sw_context.inputs.get("vt_api_key"),
        "abuse_key": sw_context.inputs.get("abuse_key"),
    }
)

sw_outputs.append({"whitelist": whitelist})
```

## Adding a New Client

To add a new client, simply add their configuration to `whitelist_config.json`:

```json
{
  "new_client": {
    "rules": [
      {
        "type": "alert_name_list",
        "alert_names": ["Some alert"]
      }
    ]
  }
}
```

**No code changes needed!** Just configuration.

## Adding a New Rule Type

If you need a new rule type:

1. Add the rule to config:
```json
{
  "type": "my_custom_rule",
  "param1": "value1"
}
```

2. Add handler method to `WhitelistChecker` class:
```python
def _check_my_custom_rule(self, rule: Dict) -> bool:
    # Your logic here
    return True  # if whitelisted
```

The naming convention is: `_check_{rule_type}`

## Benefits

✅ **No client-specific if/else statements**  
✅ **Easy to add new clients** - just add config  
✅ **Easy to maintain** - logic separated from config  
✅ **Testable** - can unit test each rule type  
✅ **Extensible** - add new rule types easily  
✅ **Type-safe** - uses type hints  
✅ **Error handling** - continues even if one rule fails  

## Migration Path

Replace your existing scripts with:

```python
# OLD:
# if client == "KNF":
#     # KNF specific logic
# elif client == "HENGST":
#     # HENGST specific logic

# NEW:
whitelist = check_whitelist(client_id=client_id, context_inputs=inputs)
```

That's it! 🚀
