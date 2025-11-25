# Migration Notes: From sw_context to action_inputs

## What Changed

The script now reads from `action_inputs` instead of `sw_context.inputs`.

## Input Structure Changes

### ❌ Old (sw_context.inputs)
```python
sw_context.inputs = {
    "rawLog": "{...}",
    "udmEvent": "{...}",
    "alertName": "some_alert",
    "whitelist_alert_names": [...],
    "whitelist_hashes": [...],
}
```

### ✅ New (action_inputs)
```python
action_inputs = {
    "alert": {
        "cfs.customer_id": "CustomerName",
        "cfs.name": "some_alert",
        "cfs.rawlog": "{...}",
        "cfs.udmevent": "{...}",
    },
    "whitelist_alert_names": [...],
    "whitelist_hashes": [...],
}
```

## Key Differences

### 1. Alert Data is Nested
- Old: `sw_context.inputs.get("rawLog")`
- New: `action_inputs["alert"]["cfs.rawlog"]`

### 2. Field Names Use "cfs." Prefix
- Old: `"alertName"`
- New: `"cfs.name"`
- Old: `"rawLog"`
- New: `"cfs.rawlog"`
- Old: `"udmEvent"`
- New: `"cfs.udmevent"`

### 3. Whitelist Data Stays at Root Level
- Still: `action_inputs["whitelist_alert_names"]`
- No change in structure for whitelist lists

### 4. Customer ID is Now Available
- New field: `action_inputs["alert"]["cfs.customer_id"]`
- Useful for logging/debugging

## Code Changes in generic_whitelist.py

```python
# OLD
rawLog = safe_json_parse(sw_context.inputs.get("rawLog"))
alertName = sw_context.inputs.get("alertName")
whitelist_ips = sw_context.inputs.get("whitelist_ips", [])

# NEW
alert_data = action_inputs.get("alert", {})
rawLog = safe_json_parse(alert_data.get("cfs.rawlog"))
alert_name = alert_data.get("cfs.name")
whitelist_ips = action_inputs.get("whitelist_ips", [])
```

## Output Changes

The script now tries multiple output methods for compatibility:

```python
# Option 1: sw_outputs (for backward compatibility)
try:
    sw_outputs.append({"whitelist": whitelist})
except:
    pass

# Option 2: action_outputs (for new platform)
try:
    action_outputs = {"whitelist": whitelist}
except:
    pass
```

## Testing Your Migration

1. **Verify input structure** matches new format
2. **Check field names** use "cfs." prefix for alert data
3. **Confirm nesting** of alert data under "alert" key
4. **Test output method** works with your platform

## Example Real Data

From your actual system (Brusa customer):

```python
action_inputs = {
    "alert": {
        "cfs.customer_id": "Brusa",
        "cfs.alertsourceapi": "Detection Engine: ListDetections",
        "cfs.name": "NTT_m365_graph_api_v2_alert",
        "cfs.severity": "Medium",
        "cfs.timestamp": "2025-11-25T08:40:50.103137Z",
        "cfs.uri": ["https://..."],
        "cfs.udmevent": "{}",
        "cfs.rawlog": "{...very long JSON...}",
        "cfs.alerthash": "de_ff303f25-d49b-f16d-9de5-3edd9b2d114e",
        "tracking-id": "BRAA-24",
        "first-created": "2025-11-25T11:47:31.3759139Z"
    },
    "whitelist_alert_names": [...],
    "whitelist_hashes": [...],
    "whitelist_ips": [...],
    "whitelist_categories": [...]
}
```

## No Changes Needed For

✅ Whitelist lists structure (same)  
✅ Custom rules format (same)  
✅ API keys location (same)  
✅ Script logic (same)  

## Breaking Changes

⚠️ Cannot use old `sw_context.inputs` format  
⚠️ Must restructure to nest alert data  
⚠️ Must add "cfs." prefix to alert fields  
