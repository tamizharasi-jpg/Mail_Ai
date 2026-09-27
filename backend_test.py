#!/usr/bin/env python3
"""
Backend API Testing for MailMind AI
Tests all endpoints as specified in the review request
"""
import csv
import io
import json
import sys
import time
from typing import Any

import requests

# Backend URL - using the public endpoint
BACKEND_URL = "https://mailmind-ai-6.preview.emergentagent.com/api"
CLIENT_ID = "test-export"

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def log_test(test_name: str, status: str, message: str = "") -> None:
    """Log test results with color coding"""
    if status == "PASS":
        print(f"{GREEN}✓ {test_name}: PASS{RESET}")
        if message:
            print(f"  {message}")
    elif status == "FAIL":
        print(f"{RED}✗ {test_name}: FAIL{RESET}")
        if message:
            print(f"  {message}")
    elif status == "INFO":
        print(f"{BLUE}ℹ {test_name}{RESET}")
        if message:
            print(f"  {message}")
    else:
        print(f"{YELLOW}⚠ {test_name}: {status}{RESET}")
        if message:
            print(f"  {message}")


def test_health_endpoint() -> bool:
    """Test GET /api/health - Should return modelVersion containing 'v2.0'"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        
        if response.status_code != 200:
            log_test("Health Endpoint", "FAIL", f"Expected status 200, got {response.status_code}")
            return False
        
        data = response.json()
        
        # Check for required fields
        if "modelVersion" not in data:
            log_test("Health Endpoint", "FAIL", "Missing 'modelVersion' field in response")
            return False
        
        # Check if modelVersion contains "v2.0"
        if "v2.0" not in data["modelVersion"]:
            log_test("Health Endpoint", "FAIL", f"modelVersion should contain 'v2.0', got: {data['modelVersion']}")
            return False
        
        log_test("Health Endpoint", "PASS", f"modelVersion: {data['modelVersion']}")
        return True
        
    except Exception as e:
        log_test("Health Endpoint", "FAIL", f"Exception: {str(e)}")
        return False


def test_email_analysis_spam() -> tuple[bool, str | None]:
    """Test POST /api/email/analyze with spam email"""
    try:
        payload = {
            "sender": "spam@win.com",
            "subject": "WIN FREE MONEY",
            "body": "Click here to win $1000. Claim your prize now!!!",
            "client_id": CLIENT_ID
        }
        
        response = requests.post(f"{BACKEND_URL}/email/analyze", json=payload, timeout=10)
        
        if response.status_code != 200:
            log_test("Email Analysis (Spam)", "FAIL", f"Expected status 200, got {response.status_code}")
            return False, None
        
        data = response.json()
        
        # Check for required fields
        if "analysis" not in data:
            log_test("Email Analysis (Spam)", "FAIL", "Missing 'analysis' field in response")
            return False, None
        
        analysis = data["analysis"]
        
        # Check spam classification
        if "spam" not in analysis:
            log_test("Email Analysis (Spam)", "FAIL", "Missing 'spam' field in analysis")
            return False, None
        
        spam_label = analysis["spam"].get("label", "")
        spam_prob = analysis["spam"].get("probability", 0)
        
        # Should be classified as Spam or Suspicious with high probability
        if spam_label not in ["Spam", "Suspicious", "Phishing Risk"]:
            log_test("Email Analysis (Spam)", "FAIL", 
                    f"Expected spam/suspicious classification, got: {spam_label} (prob: {spam_prob})")
            return False, None
        
        if spam_prob < 0.5:
            log_test("Email Analysis (Spam)", "FAIL", 
                    f"Expected high spam probability, got: {spam_prob}")
            return False, None
        
        log_test("Email Analysis (Spam)", "PASS", 
                f"Classified as {spam_label} with probability {spam_prob}")
        
        return True, data.get("id")
        
    except Exception as e:
        log_test("Email Analysis (Spam)", "FAIL", f"Exception: {str(e)}")
        return False, None


def test_email_analysis_legitimate() -> tuple[bool, str | None]:
    """Test POST /api/email/analyze with legitimate email"""
    try:
        payload = {
            "sender": "alice@company.com",
            "subject": "Team Meeting",
            "body": "Hi team, our standup is at 10am tomorrow. Please be on time.",
            "client_id": CLIENT_ID
        }
        
        response = requests.post(f"{BACKEND_URL}/email/analyze", json=payload, timeout=10)
        
        if response.status_code != 200:
            log_test("Email Analysis (Legitimate)", "FAIL", f"Expected status 200, got {response.status_code}")
            return False, None
        
        data = response.json()
        
        # Check for required fields
        if "analysis" not in data:
            log_test("Email Analysis (Legitimate)", "FAIL", "Missing 'analysis' field in response")
            return False, None
        
        analysis = data["analysis"]
        
        # Check spam classification
        if "spam" not in analysis:
            log_test("Email Analysis (Legitimate)", "FAIL", "Missing 'spam' field in analysis")
            return False, None
        
        spam_label = analysis["spam"].get("label", "")
        spam_prob = analysis["spam"].get("probability", 0)
        
        # Should be classified as Legitimate with low spam probability
        if spam_label not in ["Legitimate", "Needs Review"]:
            log_test("Email Analysis (Legitimate)", "FAIL", 
                    f"Expected legitimate classification, got: {spam_label} (prob: {spam_prob})")
            return False, None
        
        if spam_prob > 0.5:
            log_test("Email Analysis (Legitimate)", "FAIL", 
                    f"Expected low spam probability, got: {spam_prob}")
            return False, None
        
        log_test("Email Analysis (Legitimate)", "PASS", 
                f"Classified as {spam_label} with probability {spam_prob}")
        
        return True, data.get("id")
        
    except Exception as e:
        log_test("Email Analysis (Legitimate)", "FAIL", f"Exception: {str(e)}")
        return False, None


def test_history_endpoint() -> bool:
    """Test GET /api/email/history?client_id=test-export"""
    try:
        response = requests.get(f"{BACKEND_URL}/email/history", 
                               params={"client_id": CLIENT_ID}, 
                               timeout=10)
        
        if response.status_code != 200:
            log_test("History Endpoint", "FAIL", f"Expected status 200, got {response.status_code}")
            return False
        
        data = response.json()
        
        # Should return a list
        if not isinstance(data, list):
            log_test("History Endpoint", "FAIL", "Expected list response")
            return False
        
        # Should have at least 2 records (from previous tests)
        if len(data) < 2:
            log_test("History Endpoint", "FAIL", 
                    f"Expected at least 2 records, got {len(data)}")
            return False
        
        # Check structure of first record
        if data:
            record = data[0]
            required_fields = ["id", "client_id", "sender", "subject", "analysis"]
            missing = [f for f in required_fields if f not in record]
            if missing:
                log_test("History Endpoint", "FAIL", 
                        f"Missing fields in record: {missing}")
                return False
        
        log_test("History Endpoint", "PASS", f"Retrieved {len(data)} records")
        return True
        
    except Exception as e:
        log_test("History Endpoint", "FAIL", f"Exception: {str(e)}")
        return False


def test_analytics_endpoint() -> bool:
    """Test GET /api/analytics/summary?client_id=test-export"""
    try:
        response = requests.get(f"{BACKEND_URL}/analytics/summary", 
                               params={"client_id": CLIENT_ID}, 
                               timeout=10)
        
        if response.status_code != 200:
            log_test("Analytics Endpoint", "FAIL", f"Expected status 200, got {response.status_code}")
            return False
        
        data = response.json()
        
        # Check for required fields
        required_fields = ["total", "spam", "suspicious", "legitimate"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            log_test("Analytics Endpoint", "FAIL", f"Missing fields: {missing}")
            return False
        
        # Should have non-zero totals (from previous tests)
        if data["total"] < 2:
            log_test("Analytics Endpoint", "FAIL", 
                    f"Expected at least 2 total records, got {data['total']}")
            return False
        
        log_test("Analytics Endpoint", "PASS", 
                f"Total: {data['total']}, Spam: {data['spam']}, Legitimate: {data['legitimate']}")
        return True
        
    except Exception as e:
        log_test("Analytics Endpoint", "FAIL", f"Exception: {str(e)}")
        return False


def test_csv_export() -> bool:
    """Test GET /api/emails/export-csv?client_id=test-export"""
    try:
        response = requests.get(f"{BACKEND_URL}/emails/export-csv", 
                               params={"client_id": CLIENT_ID}, 
                               timeout=10)
        
        if response.status_code != 200:
            log_test("CSV Export Endpoint", "FAIL", f"Expected status 200, got {response.status_code}")
            return False
        
        # Check Content-Type
        content_type = response.headers.get("Content-Type", "")
        if "text/csv" not in content_type:
            log_test("CSV Export Endpoint", "FAIL", 
                    f"Expected Content-Type 'text/csv', got '{content_type}'")
            return False
        
        # Check Content-Disposition header
        content_disposition = response.headers.get("Content-Disposition", "")
        if "attachment" not in content_disposition or "filename" not in content_disposition:
            log_test("CSV Export Endpoint", "FAIL", 
                    f"Invalid Content-Disposition header: '{content_disposition}'")
            return False
        
        # Parse CSV content
        csv_content = response.text
        csv_reader = csv.reader(io.StringIO(csv_content))
        rows = list(csv_reader)
        
        if len(rows) < 1:
            log_test("CSV Export Endpoint", "FAIL", "CSV has no rows")
            return False
        
        # Check headers
        expected_headers = [
            "Subject", "Sender", "Source", "Date", 
            "Spam Label", "Spam Confidence", 
            "Phishing Risk", "Phishing Confidence",
            "Category", "Category Confidence",
            "Priority", "Intent", "Action Required", "Summary"
        ]
        
        headers = rows[0]
        if headers != expected_headers:
            log_test("CSV Export Endpoint", "FAIL", 
                    f"Headers mismatch.\nExpected: {expected_headers}\nGot: {headers}")
            return False
        
        # Check that we have data rows (at least 2 from previous tests)
        data_rows = rows[1:]
        if len(data_rows) < 2:
            log_test("CSV Export Endpoint", "FAIL", 
                    f"Expected at least 2 data rows, got {len(data_rows)}")
            return False
        
        # Verify data row structure (should have 14 columns)
        for i, row in enumerate(data_rows[:3], 1):  # Check first 3 rows
            if len(row) != 14:
                log_test("CSV Export Endpoint", "FAIL", 
                        f"Row {i} has {len(row)} columns, expected 14")
                return False
            
            # Check that key fields are populated
            if not row[0]:  # Subject
                log_test("CSV Export Endpoint", "FAIL", f"Row {i} has empty Subject")
                return False
            if not row[4]:  # Spam Label
                log_test("CSV Export Endpoint", "FAIL", f"Row {i} has empty Spam Label")
                return False
        
        log_test("CSV Export Endpoint", "PASS", 
                f"CSV with {len(data_rows)} rows, correct headers and structure")
        
        # Log sample data for verification
        log_test("CSV Sample Data", "INFO", 
                f"First row: Subject='{data_rows[0][0]}', Spam Label='{data_rows[0][4]}'")
        
        return True
        
    except Exception as e:
        log_test("CSV Export Endpoint", "FAIL", f"Exception: {str(e)}")
        return False


def main():
    """Run all backend tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}MailMind AI Backend Testing{RESET}")
    print(f"{BLUE}Backend URL: {BACKEND_URL}{RESET}")
    print(f"{BLUE}Client ID: {CLIENT_ID}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    results = {}
    
    # Test 1: Health Check
    print(f"\n{YELLOW}[1/6] Testing Health Endpoint...{RESET}")
    results["health"] = test_health_endpoint()
    time.sleep(0.5)
    
    # Test 2: Email Analysis - Spam
    print(f"\n{YELLOW}[2/6] Testing Email Analysis (Spam)...{RESET}")
    spam_result, spam_id = test_email_analysis_spam()
    results["analysis_spam"] = spam_result
    time.sleep(0.5)
    
    # Test 3: Email Analysis - Legitimate
    print(f"\n{YELLOW}[3/6] Testing Email Analysis (Legitimate)...{RESET}")
    legit_result, legit_id = test_email_analysis_legitimate()
    results["analysis_legitimate"] = legit_result
    time.sleep(0.5)
    
    # Test 4: History
    print(f"\n{YELLOW}[4/6] Testing History Endpoint...{RESET}")
    results["history"] = test_history_endpoint()
    time.sleep(0.5)
    
    # Test 5: Analytics
    print(f"\n{YELLOW}[5/6] Testing Analytics Endpoint...{RESET}")
    results["analytics"] = test_analytics_endpoint()
    time.sleep(0.5)
    
    # Test 6: CSV Export
    print(f"\n{YELLOW}[6/6] Testing CSV Export Endpoint...{RESET}")
    results["csv_export"] = test_csv_export()
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"{GREEN}✓ All tests passed!{RESET}\n")
        return 0
    else:
        print(f"{RED}✗ Some tests failed{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
