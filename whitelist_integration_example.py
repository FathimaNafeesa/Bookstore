"""
Integration Example: How to use the generic whitelist script in your environment

Simply import and call the check_whitelist function with your client_id
"""

from generic_whitelist_script import check_whitelist

# ==================== OPTION 1: Using JSON Config File ====================
# Store client_id as environment variable or parameter

client_id = "knf"  # or "hengst", "xella", etc. - get this from env var or param

whitelist = check_whitelist(
    client_id=client_id,
    context_inputs={
        "rawLog": sw_context.inputs.get("rawLog"),
        "udmEvent": sw_context.inputs.get("udmEvent"),
        "alertName": sw_context.inputs.get("alertName"),
        "name": sw_context.inputs.get("name"),
        "rawlog": sw_context.inputs.get("rawlog"),
        "vt_api_key": sw_context.inputs.get("vt_api_key"),
        "abuse_key": sw_context.inputs.get("abuse_key"),
        "abuse_host": sw_context.inputs.get("abuse_host"),
    },
    config_path="whitelist_config.json"  # Path to your config file
)

sw_outputs.append({"whitelist": whitelist})


# ==================== OPTION 2: Using Environment Variable ====================
import os

client_id = os.getenv("CLIENT_ID", "knf")  # Default to 'knf' if not set

whitelist = check_whitelist(
    client_id=client_id,
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


# ==================== OPTION 3: Inline Configuration (No File) ====================
from generic_whitelist_script import WhitelistChecker

# Define config inline
config = {
    "rules": [
        {
            "type": "alert_name_list",
            "alert_names": ["Email reported by user as junk", "Another alert"]
        }
    ]
}

context_inputs = {
    "rawLog": sw_context.inputs.get("rawLog"),
    "alertName": sw_context.inputs.get("alertName"),
    # ... other inputs
}

checker = WhitelistChecker(config, context_inputs)
whitelist = checker.check_all_rules()

sw_outputs.append({"whitelist": whitelist})
