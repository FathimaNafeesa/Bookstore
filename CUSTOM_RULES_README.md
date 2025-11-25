# Custom Rules Processor - Documentation

## Overview

The custom rules logic has been separated into `custom_rules_processor.py` for better modularity and maintainability.

## Files

- **`generic_whitelist.py`** - Main script (handles basic checks)
- **`custom_rules_processor.py`** - Complex rules processor (handles custom rules)

## How It Works

### Main Script Flow
```python
# generic_whitelist.py does:
1. Parse inputs
2. Check simple lists (alert names, hashes, IPs, etc.)
3. Import and call custom_rules_processor
4. Return whitelist status
```

### Custom Rules Processor
```python
# custom_rules_processor.py provides:
- process_custom_rules() - Main entry point
- Individual rule handler functions
- Clean, testable code
```

## Using Custom Rules Processor

### In Main Script (Automatic)
```python
from custom_rules_processor import process_custom_rules

whitelist = process_custom_rules(
    custom_rules=custom_rules,
    log_data=log_data,
    alert_name=alert_name,
    vt_api_key=vt_api_key,
    abuse_api_key=abuse_api_key,
    current_whitelist=whitelist
)
```

### Standalone Usage
```python
from custom_rules_processor import process_custom_rules

custom_rules = [
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

result = process_custom_rules(
    custom_rules=custom_rules,
    log_data={"target": {"administrativeDomain": "example.com"}},
    alert_name="External_user_added_to_Teams_M365",
    vt_api_key="your_key"
)

print(result)  # "YES" or "NO"
```

## Supported Rule Types

### 1. category_ip_description
Check category + IP + description combination
```python
{
    "type": "category_ip_description",
    "params": {
        "category": "SuspiciousActivity",
        "ips": ["1.2.3.4", "5.6.7.8"],
        "description_contains": "Mass download by a single user"
    }
}
```

### 2. alert_description_match
Check alert name + description match
```python
{
    "type": "alert_description_match",
    "params": {
        "alert_name": "InitialAccess",
        "descriptions": ["Email with malicious URL"]
    }
}
```

### 3. virustotal_domain
Check domain reputation via VirusTotal API
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

### 4. abuseipdb_isp
Check ISP via AbuseIPDB API
```python
{
    "type": "abuseipdb_isp",
    "params": {
        "alert_name": "NTT_azure_multiple_failed_logins",
        "isp_contains": "hengst"
    }
}
```

### 5. key_value
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

### 6. nested_path
Check nested field value with array support
```python
{
    "type": "nested_path",
    "params": {
        "path": "securityResult[0].ruleName",
        "value": "Suspicious LDAP query"
    }
}
```

## Adding New Rule Types

### Method 1: Edit custom_rules_processor.py

1. Add a new handler function:
```python
def _check_my_custom_rule(log_data, params):
    """Check my custom rule"""
    field = params.get("field")
    threshold = params.get("threshold", 100)
    
    if log_data.get(field) > threshold:
        return True
    
    return False
```

2. Add to process_custom_rules():
```python
elif rule_type == "my_custom_rule":
    if _check_my_custom_rule(log_data, params):
        whitelist = "YES"
```

3. Use it:
```python
{
    "type": "my_custom_rule",
    "params": {
        "field": "risk_score",
        "threshold": 50
    }
}
```

### Method 2: External Plugin (Future Enhancement)
```python
# Could be extended to support dynamic rule registration
from custom_rules_processor import add_custom_rule_handler

def my_handler(log_data, params):
    return True  # Your logic

add_custom_rule_handler("my_rule", my_handler)
```

## Benefits of Separation

### ✅ Modularity
- Easy to test custom rules independently
- Can be imported by other scripts
- Clear separation of concerns

### ✅ Maintainability
- Custom rules logic in one place
- Easy to add new rule types
- Simpler debugging

### ✅ Reusability
- Can use custom_rules_processor in other projects
- Can test rules without running full script
- Can create rule libraries

### ✅ Performance
- Main script is smaller and faster
- Custom rules only loaded if needed
- Can cache rule results

## Testing Custom Rules

### Test Individual Rule
```python
from custom_rules_processor import _check_key_value

log_data = {"status": "active"}
params = {"field": "status", "value": "active"}

result = _check_key_value(log_data, params)
print(result)  # True
```

### Test Full Processor
```python
from custom_rules_processor import process_custom_rules

rules = [
    {"type": "key_value", "params": {"field": "status", "value": "active"}}
]

result = process_custom_rules(
    custom_rules=rules,
    log_data={"status": "active"},
    alert_name="test"
)

print(result)  # "YES"
```

## Error Handling

The processor handles errors gracefully:
- If a rule fails, continues to next rule
- If API call fails, continues processing
- If import fails, main script continues with basic checks

```python
try:
    from custom_rules_processor import process_custom_rules
    whitelist = process_custom_rules(...)
except ImportError:
    # No custom rules processor - use basic checks only
    pass
except Exception:
    # Custom rules failed - continue with current whitelist status
    pass
```

## File Structure

```
/workspace/
├── generic_whitelist.py          # Main script
├── custom_rules_processor.py     # Custom rules (THIS FILE)
├── example_action_inputs.py      # Input examples
├── customer_configs_example.py   # Customer configs
└── CUSTOM_RULES_README.md        # This documentation
```

## Migration Notes

### Before (Monolithic)
```python
# Everything in generic_whitelist.py
# ~290 lines including all custom rules logic
```

### After (Modular)
```python
# generic_whitelist.py - ~140 lines (basic checks)
# custom_rules_processor.py - ~250 lines (custom rules)
# Clear separation, easier to maintain
```

## Summary

✅ **Separated** custom rules into standalone module  
✅ **Cleaner** main script focused on basic checks  
✅ **Testable** custom rules independently  
✅ **Extensible** easy to add new rule types  
✅ **Reusable** can import in other projects  
✅ **Maintainable** changes isolated to relevant file  

Your custom rules are now in a professional, modular structure! 🎉
