"""
Example of how action_inputs is structured for the generic whitelist script
"""

# Example from Brusa customer
action_inputs = {
    "alert": {
        "cfs.customer_id": "Brusa",
        "cfs.alertsourceapi": "Detection Engine: ListDetections",
        "cfs.name": "NTT_m365_graph_api_v2_alert",
        "cfs.severity": "Medium",
        "cfs.timestamp": "2025-11-25T08:40:50.103137Z",
        "cfs.udmevent": "{}",
        "cfs.rawlog": """{
            "metadata": {
                "productLogId": "daca5e886d-1f4b-4ed1-a9ba-0b842bf6e3c4_1",
                "eventTimestamp": "2025-11-25T08:28:41.123333300Z",
                "eventType": "STATUS_UPDATE",
                "vendorName": "Microsoft",
                "productName": "Microsoft Defender for Endpoint",
                "productEventType": "Discovery",
                "description": "A suspect LDAP query..."
            },
            "principal": {
                "hostname": "33-eag-nb007.brusa.biz",
                "user": {
                    "userid": "Bo.Wang",
                    "emailAddresses": ["Bo.Wang@brusahypower.com"]
                },
                "administrativeDomain": "BRUSA"
            },
            "target": {
                "process": {
                    "file": {
                        "sha256": "00961e84a82ea30e7439ec3635d1c621925aeb47632108afe6d1013cfd46949a"
                    }
                }
            }
        }""",
        "cfs.alerthash": "de_ff303f25-d49b-f16d-9de5-3edd9b2d114e"
    },
    
    # Customer-specific whitelist data
    "whitelist_alert_names": [
        "Email reported by user as junk",
        "Email reported by user as not junk"
    ],
    
    "whitelist_hashes": [
        "FE7A9EA0905151A907E248E91655EC36D9481BF7DB839ADED6D0444A66D8D730"
    ],
    
    "whitelist_ips": [
        "83.135.49.100",
        "5.45.7.100",
        "178.174.74.158"
    ],
    
    "whitelist_categories": [
        "SuspiciousActivity"
    ],
    
    # Optional: API keys for external checks
    "vt_api_key": "your_virustotal_api_key",
    "abuse_key": "your_abuseipdb_api_key",
    
    # Optional: Complex custom rules
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


# =============================================================================
# HOW THE SCRIPT READS THIS
# =============================================================================

"""
1. Alert data from nested "alert" dict:
   - alert_name = action_inputs["alert"]["cfs.name"]
   - rawlog = JSON.parse(action_inputs["alert"]["cfs.rawlog"])
   - udmevent = JSON.parse(action_inputs["alert"]["cfs.udmevent"])
   - customer_id = action_inputs["alert"]["cfs.customer_id"]

2. Whitelist data from root level:
   - whitelist_alert_names = action_inputs["whitelist_alert_names"]
   - whitelist_hashes = action_inputs["whitelist_hashes"]
   - whitelist_ips = action_inputs["whitelist_ips"]
   - etc.

3. Then the script performs generic checks against the provided lists
"""


# =============================================================================
# EXAMPLE FOR DIFFERENT CUSTOMERS
# =============================================================================

# KNF Customer
knf_action_inputs = {
    "alert": {
        "cfs.customer_id": "KNF",
        "cfs.name": "wannacry_ransomware_via_sysmon",
        "cfs.rawlog": "{...}",
        "cfs.udmevent": "{...}"
    },
    "whitelist_alert_names": [
        "Email reported by user as junk",
        "Malicious emails were delivered and later removed -V1.0.0.2"
    ],
    "whitelist_hashes": [
        "FE7A9EA0905151A907E248E91655EC36D9481BF7DB839ADED6D0444A66D8D730"
    ],
    "whitelist_ips": [
        "83.135.49.100", "5.45.7.100"
    ],
    "vt_api_key": "knf_vt_key",
    "custom_rules": [...]
}

# HENGST Customer
hengst_action_inputs = {
    "alert": {
        "cfs.customer_id": "HENGST",
        "cfs.name": "NTT_azure_multiple_failed_logins",
        "cfs.rawlog": "{...}",
        "cfs.udmevent": "{}"
    },
    "whitelist_alert_names": [],
    "whitelist_hashes": [],
    "whitelist_ips": [],
    "abuse_key": "hengst_abuse_key",
    "custom_rules": [
        {
            "type": "abuseipdb_isp",
            "params": {
                "alert_name": "NTT_azure_multiple_failed_logins",
                "isp_contains": "hengst"
            }
        }
    ]
}

# XELLA Customer (no rules yet)
xella_action_inputs = {
    "alert": {
        "cfs.customer_id": "XELLA",
        "cfs.name": "some_alert",
        "cfs.rawlog": "{...}",
        "cfs.udmevent": "{}"
    },
    "whitelist_alert_names": [],
    "whitelist_hashes": [],
    "whitelist_ips": []
}
