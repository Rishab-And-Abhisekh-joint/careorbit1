#!/usr/bin/env python3
"""
Simple debug script for CareOrbit API
"""

import requests

BASE_URL = "http://localhost:8001"

print("Testing CareOrbit API...")
print(f"URL: {BASE_URL}")
print("-" * 50)

# Test 1: Root endpoint
try:
    print("\n[1] Testing root endpoint /")
    response = requests.get(f"{BASE_URL}/", timeout=10)
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text[:200]}")
except Exception as e:
    print(f"    ERROR: {type(e).__name__}: {e}")

# Test 2: Health endpoint
try:
    print("\n[2] Testing /api/health")
    response = requests.get(f"{BASE_URL}/api/health", timeout=10)
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text[:200]}")
except Exception as e:
    print(f"    ERROR: {type(e).__name__}: {e}")

# Test 3: Patients endpoint
try:
    print("\n[3] Testing /api/patients")
    response = requests.get(f"{BASE_URL}/api/patients", timeout=10)
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text[:300]}")
except Exception as e:
    print(f"    ERROR: {type(e).__name__}: {e}")

# Test 4: Patient summary
try:
    print("\n[4] Testing /api/patients/patient-001/summary")
    response = requests.get(f"{BASE_URL}/api/patients/patient-001/summary", timeout=10)
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text[:300]}")
except Exception as e:
    print(f"    ERROR: {type(e).__name__}: {e}")

print("\n" + "-" * 50)
print("Debug test complete!")