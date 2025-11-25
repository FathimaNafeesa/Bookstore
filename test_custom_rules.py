"""
Test suite for custom_rules_processor.py
Shows how to test individual rules and the full processor

NOTE: Requires 'requests' module to run
Install with: pip install requests

This file serves as both a test suite and documentation
"""

# Uncomment when requests is installed:
# from custom_rules_processor import (
#     process_custom_rules,
#     _check_key_value,
#     _check_nested_path,
#     _check_alert_description_match,
#     _check_category_ip_description
# )

# Mock imports for documentation purposes
def process_custom_rules(*args, **kwargs): pass
def _check_key_value(*args, **kwargs): pass
def _check_nested_path(*args, **kwargs): pass
def _check_alert_description_match(*args, **kwargs): pass
def _check_category_ip_description(*args, **kwargs): pass


# =============================================================================
# TEST INDIVIDUAL RULE HANDLERS
# =============================================================================

def test_key_value_match():
    """Test simple key-value matching"""
    log_data = {"status": "active", "severity": "high"}
    
    # Should match
    params = {"field": "status", "value": "active"}
    assert _check_key_value(log_data, params) == True
    
    # Should not match
    params = {"field": "status", "value": "inactive"}
    assert _check_key_value(log_data, params) == False
    
    print("✅ test_key_value_match passed")


def test_nested_path():
    """Test nested path matching"""
    log_data = {
        "securityResult": [
            {"ruleName": "Suspicious LDAP query"},
            {"ruleName": "Another rule"}
        ],
        "target": {
            "user": {
                "email": "test@example.com"
            }
        }
    }
    
    # Should match array access
    params = {"path": "securityResult[0].ruleName", "value": "Suspicious LDAP query"}
    assert _check_nested_path(log_data, params) == True
    
    # Should match nested dict
    params = {"path": "target.user.email", "value": "test@example.com"}
    assert _check_nested_path(log_data, params) == True
    
    # Should not match
    params = {"path": "securityResult[0].ruleName", "value": "Wrong value"}
    assert _check_nested_path(log_data, params) == False
    
    print("✅ test_nested_path passed")


def test_alert_description_match():
    """Test alert name + description matching"""
    log_data = {"description": "Email with malicious URL"}
    alert_name = "InitialAccess"
    
    # Should match
    params = {
        "alert_name": "InitialAccess",
        "descriptions": ["Email with malicious URL", "Another description"]
    }
    assert _check_alert_description_match(log_data, alert_name, params) == True
    
    # Should not match - wrong alert
    alert_name = "DifferentAlert"
    assert _check_alert_description_match(log_data, alert_name, params) == False
    
    # Should not match - description not in list
    alert_name = "InitialAccess"
    log_data = {"description": "Some other description"}
    assert _check_alert_description_match(log_data, alert_name, params) == False
    
    print("✅ test_alert_description_match passed")


def test_category_ip_description():
    """Test combined category + IP + description"""
    log_data = {
        "category": "SuspiciousActivity",
        "description": "Mass download by a single user detected",
        "evidence": [
            {"@odata.type": "#microsoft.graph.security.ipEvidence", "ipAddress": "83.135.49.100"},
            {"@odata.type": "#other.type", "value": "something"}
        ]
    }
    
    # Should match
    params = {
        "category": "SuspiciousActivity",
        "ips": ["83.135.49.100", "5.45.7.100"],
        "description_contains": "Mass download by a single user"
    }
    assert _check_category_ip_description(log_data, params) == True
    
    # Should not match - wrong IP
    params["ips"] = ["1.2.3.4"]
    assert _check_category_ip_description(log_data, params) == False
    
    print("✅ test_category_ip_description passed")


# =============================================================================
# TEST FULL PROCESSOR
# =============================================================================

def test_process_custom_rules_single_match():
    """Test processor with single matching rule"""
    custom_rules = [
        {
            "type": "key_value",
            "params": {"field": "status", "value": "active"}
        }
    ]
    
    log_data = {"status": "active"}
    
    result = process_custom_rules(
        custom_rules=custom_rules,
        log_data=log_data,
        alert_name="test_alert"
    )
    
    assert result == "YES"
    print("✅ test_process_custom_rules_single_match passed")


def test_process_custom_rules_no_match():
    """Test processor with no matching rules"""
    custom_rules = [
        {
            "type": "key_value",
            "params": {"field": "status", "value": "inactive"}
        }
    ]
    
    log_data = {"status": "active"}
    
    result = process_custom_rules(
        custom_rules=custom_rules,
        log_data=log_data,
        alert_name="test_alert"
    )
    
    assert result == "NO"
    print("✅ test_process_custom_rules_no_match passed")


def test_process_custom_rules_multiple_rules():
    """Test processor with multiple rules"""
    custom_rules = [
        {
            "type": "key_value",
            "params": {"field": "status", "value": "inactive"}  # Won't match
        },
        {
            "type": "nested_path",
            "params": {"path": "target.user.email", "value": "test@example.com"}  # Will match
        }
    ]
    
    log_data = {
        "status": "active",
        "target": {"user": {"email": "test@example.com"}}
    }
    
    result = process_custom_rules(
        custom_rules=custom_rules,
        log_data=log_data,
        alert_name="test_alert"
    )
    
    assert result == "YES"
    print("✅ test_process_custom_rules_multiple_rules passed")


def test_process_custom_rules_preserves_current_status():
    """Test that processor preserves existing whitelist status"""
    custom_rules = [
        {
            "type": "key_value",
            "params": {"field": "status", "value": "inactive"}  # Won't match
        }
    ]
    
    log_data = {"status": "active"}
    
    # If already whitelisted, should stay whitelisted
    result = process_custom_rules(
        custom_rules=custom_rules,
        log_data=log_data,
        alert_name="test_alert",
        current_whitelist="YES"
    )
    
    assert result == "YES"
    print("✅ test_process_custom_rules_preserves_current_status passed")


# =============================================================================
# RUN ALL TESTS
# =============================================================================

if __name__ == "__main__":
    print("Running custom_rules_processor tests...\n")
    
    # Test individual handlers
    test_key_value_match()
    test_nested_path()
    test_alert_description_match()
    test_category_ip_description()
    
    print()
    
    # Test full processor
    test_process_custom_rules_single_match()
    test_process_custom_rules_no_match()
    test_process_custom_rules_multiple_rules()
    test_process_custom_rules_preserves_current_status()
    
    print("\n✅ All tests passed!")
