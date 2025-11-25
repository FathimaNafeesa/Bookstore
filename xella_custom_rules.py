"""
XELLA Customer - Custom Rules Configuration
"""


def get_xella_custom_rules(log_data, alert_name, whitelist="NO"):
    """
    XELLA-specific custom whitelist rules
    
    Args:
        log_data: Parsed log data dictionary
        alert_name: Alert name string
        whitelist: Current whitelist status
    
    Returns:
        str: "YES" if any rule matches, otherwise returns current whitelist
    """
    
    # No custom rules defined yet for XELLA
    # Add rules here as needed
    
    return whitelist
