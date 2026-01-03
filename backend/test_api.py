#!/usr/bin/env python3
"""
CareOrbit API Test Script
Run this to validate your backend deployment
"""

import httpx
import asyncio
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"  # Change for production

async def test_api():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=" * 60)
        print("CareOrbit API Test Suite")
        print("=" * 60)
        print(f"Testing: {BASE_URL}")
        print(f"Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        tests_passed = 0
        tests_failed = 0
        
        # Test 1: Health Check
        print("\n[TEST 1] Health Check")
        try:
            response = await client.get(f"{BASE_URL}/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            print(f"  ✅ PASSED - Status: {data['status']}")
            print(f"     Agents: {list(data.get('agents', {}).keys())}")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ FAILED - {e}")
            tests_failed += 1
        
        # Test 2: Get Patients
        print("\n[TEST 2] Get Patients")
        try:
            response = await client.get(f"{BASE_URL}/api/patients")
            assert response.status_code == 200
            patients = response.json()
            assert len(patients) > 0
            print(f"  ✅ PASSED - Found {len(patients)} patient(s)")
            patient_id = patients[0]["id"]
            print(f"     Demo Patient: {patients[0]['first_name']} {patients[0]['last_name']}")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ FAILED - {e}")
            tests_failed += 1
            patient_id = "patient-001"  # Fallback
        
        # Test 3: Get Patient Summary
        print("\n[TEST 3] Get Patient Summary")
        try:
            response = await client.get(f"{BASE_URL}/api/patients/{patient_id}/summary")
            assert response.status_code == 200
            summary = response.json()
            print(f"  ✅ PASSED - Status: {summary['overall_status']}")
            print(f"     Conditions: {len(summary['active_conditions'])}")
            print(f"     Medications: {summary['active_medications']}")
            print(f"     Appointments: {summary['upcoming_appointments']}")
            print(f"     Care Gaps: {summary['open_care_gaps']}")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ FAILED - {e}")
            tests_failed += 1
        
        # Test 4: Get Medications
        print("\n[TEST 4] Get Medications")
        try:
            response = await client.get(f"{BASE_URL}/api/patients/{patient_id}/medications?active_only=true")
            assert response.status_code == 200
            medications = response.json()
            print(f"  ✅ PASSED - Found {len(medications)} active medication(s)")
            for med in medications[:3]:
                print(f"     - {med['name']} ({med['dosage']}) by {med['prescriber']}")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ FAILED - {e}")
            tests_failed += 1
        
        # Test 5: Get Appointments
        print("\n[TEST 5] Get Appointments")
        try:
            response = await client.get(f"{BASE_URL}/api/patients/{patient_id}/appointments?upcoming_only=true")
            assert response.status_code == 200
            appointments = response.json()
            print(f"  ✅ PASSED - Found {len(appointments)} upcoming appointment(s)")
            for apt in appointments[:3]:
                print(f"     - {apt['provider_name']} ({apt['specialty']})")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ FAILED - {e}")
            tests_failed += 1
        
        # Test 6: Get Care Gaps
        print("\n[TEST 6] Get Care Gaps")
        try:
            response = await client.get(f"{BASE_URL}/api/patients/{patient_id}/care-gaps")
            assert response.status_code == 200
            gaps = response.json()
            print(f"  ✅ PASSED - Found {len(gaps)} care gap(s)")
            for gap in gaps[:3]:
                print(f"     - [{gap['severity'].upper()}] {gap['title']}")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ FAILED - {e}")
            tests_failed += 1
        
        # Test 7: Chat with AI Agents
        print("\n[TEST 7] Chat with AI Agents")
        try:
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json={
                    "patient_id": patient_id,
                    "message": "What medications am I taking?"
                }
            )
            assert response.status_code == 200
            result = response.json()
            print(f"  ✅ PASSED - Received response from agents")
            print(f"     Agents involved: {[a['agent_name'] for a in result['agent_contributions']]}")
            print(f"     Response preview: {result['primary_response'][:100]}...")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ FAILED - {e}")
            tests_failed += 1
        
        # Test 8: Chat about Care Gaps
        print("\n[TEST 8] Chat about Care Gaps")
        try:
            response = await client.post(
                f"{BASE_URL}/api/chat",
                json={
                    "patient_id": patient_id,
                    "message": "What care gaps need attention?"
                }
            )
            assert response.status_code == 200
            result = response.json()
            print(f"  ✅ PASSED - Care gap query successful")
            print(f"     Care gaps mentioned: {len(result.get('care_gaps_detected', []))}")
            tests_passed += 1
        except Exception as e:
            print(f"  ❌ FAILED - {e}")
            tests_failed += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"  Passed: {tests_passed}")
        print(f"  Failed: {tests_failed}")
        print(f"  Total:  {tests_passed + tests_failed}")
        print("=" * 60)
        
        if tests_failed == 0:
            print("\n🎉 All tests passed! Your CareOrbit API is working correctly.")
        else:
            print(f"\n⚠️  {tests_failed} test(s) failed. Please check your configuration.")
        
        return tests_failed == 0

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
    
    success = asyncio.run(test_api())
    sys.exit(0 if success else 1)
