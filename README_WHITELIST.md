# Generic Whitelist Solution

## Files

### Main Script
- **`generic_whitelist.py`** (5.8KB) - Generic whitelist checker for all clients

### Client-Specific Custom Rules
- **`knf_custom_rules.py`** (4KB) - KNF custom rules
- **`hengst_custom_rules.py`** (1.5KB) - HENGST custom rules  
- **`xella_custom_rules.py`** (520 bytes) - XELLA custom rules

## How It Works

### 1. Generic Script
The main script (`generic_whitelist.py`) handles common checks for all clients:
- Alert name whitelist
- Hash whitelist (SHA256)
- IP address whitelist
- Category whitelist
- Description whitelist
- UDM event type whitelist

### 2. Client-Specific Custom Rules
Based on `cfs.customer_id` in the alert data, the script automatically imports and calls the appropriate custom rules:

```python
if customer_id == "KNF":
    from knf_custom_rules import get_knf_custom_rules
    whitelist = get_knf_custom_rules(...)

elif customer_id == "HENGST":
    from hengst_custom_rules import get_hengst_custom_rules
    whitelist = get_hengst_custom_rules(...)

elif customer_id == "XELLA":
    from xella_custom_rules import get_xella_custom_rules
    whitelist = get_xella_custom_rules(...)
```

## Input Structure

```python
action_inputs = {
    "alert": {
        "cfs.customer_id": "KNF",           # Customer identifier
        "cfs.name": "alert_name",            # Alert name
        "cfs.rawlog": "{...JSON...}",        # Raw log data
        "cfs.udmevent": "{...JSON...}"       # UDM event data
    },
    
    # Generic whitelists (optional)
    "whitelist_alert_names": [...],
    "whitelist_hashes": [...],
    "whitelist_ips": [...],
    "whitelist_categories": [...],
    
    # API keys (optional)
    "vt_api_key": "...",
    "abuse_key": "..."
}
```

## Client Custom Rules

### KNF (`knf_custom_rules.py`)
- Category + IP + Description check (SuspiciousActivity + specific IPs)
- InitialAccess alert with description matching
- VirusTotal domain age/reputation check for Teams external users

### HENGST (`hengst_custom_rules.py`)
- AbuseIPDB ISP check for Azure failed logins
- Whitelists if ISP contains "hengst"

### XELLA (`xella_custom_rules.py`)
- No custom rules yet (ready for future rules)

## Adding New Client

1. Create new file: `{client}_custom_rules.py`
2. Define function: `get_{client}_custom_rules(log_data, alert_name, ...)`
3. Add elif block to `generic_whitelist.py`:

```python
elif customer_id == "NEWCLIENT":
    from newclient_custom_rules import get_newclient_custom_rules
    whitelist = get_newclient_custom_rules(...)
```

## Output

The script returns: `whitelist = "YES"` or `"NO"`
