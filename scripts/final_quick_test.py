#!/usr/bin/env python3
"""
Testing rápido final para validación MVP
"""

import requests
import json
import time

def quick_test():
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("🏰 FINAL QUICK TEST - CHATBOT ZAPOPAN MVP")
    print("="*60)
    print(f"Time: {time.strftime('%H:%M:%S CST')}")
    print(f"Deadline: 16:48:00 CST")
    print("="*60)
    
    tests = []
    
    # Test 1: Health
    try:
        start = time.time()
        resp = requests.get(f"{base_url}/health", timeout=3)
        elapsed = (time.time() - start) * 1000
        success = resp.status_code == 200
        tests.append(("Health Check", success, f"{elapsed:.0f}ms"))
    except Exception as e:
        tests.append(("Health Check", False, str(e)))
    
    # Test 2: RAG Status
    try:
        resp = requests.get(f"{base_url}/rag/status", timeout=3)
        data = resp.json() if resp.status_code == 200 else {}
        success = data.get("status") == "active"
        tests.append(("RAG System", success, f"{data.get('documents_loaded', 0)} docs"))
    except Exception as e:
        tests.append(("RAG System", False, str(e)))
    
    # Test 3: Authentication
    try:
        resp = requests.post(
            f"{base_url}/api/login",
            json={"username": "administrador_supremo", "password": ""},
            timeout=3
        )
        data = resp.json() if resp.status_code == 200 else {}
        success = data.get("success", False)
        tests.append(("Authentication", success, data.get("user", {}).get("name", "N/A")))
    except Exception as e:
        tests.append(("Authentication", False, str(e)))
    
    # Test 4: Chat Functionality
    try:
        resp = requests.post(
            f"{base_url}/api/chat",
            json={"message": "¿Cuáles son las facultades de inspección?", "token": "test_token"},
            timeout=5
        )
        data = resp.json() if resp.status_code == 200 else {}
        success = data.get("success", False) and data.get("documents_found", 0) > 0
        tests.append(("Chat with RAG", success, f"{data.get('documents_found', 0)} docs found"))
    except Exception as e:
        tests.append(("Chat with RAG", False, str(e)))
    
    # Test 5: Frontend
    try:
        resp = requests.get(base_url, timeout=3)
        success = resp.status_code == 200 and "Chatbot Inspección" in resp.text
        tests.append(("Frontend UI", success, "HTML loaded"))
    except Exception as e:
        tests.append(("Frontend UI", False, str(e)))
    
    # Test 6: Security - Invalid token
    try:
        resp = requests.post(
            f"{base_url}/api/chat",
            json={"message": "test", "token": "invalid_token_xyz"},
            timeout=3
        )
        success = resp.status_code == 401  # Should reject invalid token
        tests.append(("Security - Token Validation", success, f"Status {resp.status_code}"))
    except Exception as e:
        tests.append(("Security - Token Validation", False, str(e)))
    
    # Test 7: Error handling
    try:
        resp = requests.post(
            f"{base_url}/api/chat",
            json={"token": "test_token"},  # Missing message
            timeout=3
        )
        success = resp.status_code == 400  # Bad request
        tests.append(("Error Handling", success, f"Status {resp.status_code}"))
    except Exception as e:
        tests.append(("Error Handling", False, str(e)))
    
    # Display results
    print("\n📋 TEST RESULTS:")
    passed = 0
    for name, success, details in tests:
        status = "✅" if success else "❌"
        print(f"{status} {name}: {details}")
        if success:
            passed += 1
    
    total = len(tests)
    success_rate = (passed / total) * 100
    
    print(f"\n📊 SUMMARY: {passed}/{total} passed ({success_rate:.1f}%)")
    
    # MVP Requirements check
    print("\n🎯 MVP REQUIREMENTS CHECK:")
    mvp_reqs = [
        ("✅" if any("Health" in t[0] and t[1] for t in tests) else "❌", "System operational"),
        ("✅" if any("RAG" in t[0] and t[1] for t in tests) else "❌", "RAG system active"),
        ("✅" if any("Authentication" in t[0] and t[1] for t in tests) else "❌", "Authentication working"),
        ("✅" if any("Chat" in t[0] and t[1] for t in tests) else "❌", "Chat functionality"),
        ("✅" if any("Frontend" in t[0] and t[1] for t in tests) else "❌", "Frontend UI"),
        ("✅" if success_rate >= 80 else "❌", "Overall reliability")
    ]
    
    for status, req in mvp_reqs:
        print(f"{status} {req}")
    
    mvp_passed = sum(1 for status, _ in mvp_reqs if status == "✅")
    
    # Final verdict
    print("\n" + "="*60)
    if success_rate >= 90 and mvp_passed == len(mvp_reqs):
        print("🏆 FINAL VERDICT: ✅ EXCELLENT - READY FOR DEPLOYMENT")
        verdict = "EXCELLENT"
    elif success_rate >= 80 and mvp_passed >= len(mvp_reqs) - 1:
        print("🏆 FINAL VERDICT: ✅ GOOD - READY FOR DEPLOYMENT")
        verdict = "GOOD"
    elif success_rate >= 70:
        print("🏆 FINAL VERDICT: ⚠️ FAIR - MINOR ISSUES")
        verdict = "FAIR"
    else:
        print("🏆 FINAL VERDICT: ❌ POOR - NEEDS WORK")
        verdict = "POOR"
    
    # Time remaining
    deadline_hour = 16
    deadline_minute = 48
    current_hour = int(time.strftime("%H"))
    current_minute = int(time.strftime("%M"))
    
    hours_left = deadline_hour - current_hour
    minutes_left = deadline_minute - current_minute
    if minutes_left < 0:
        hours_left -= 1
        minutes_left += 60
    
    print(f"\n⏰ TIME REMAINING: {hours_left}h {minutes_left}m until 16:48 deadline")
    
    # Save report
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "base_url": base_url,
        "tests": [{"name": n, "success": s, "details": d} for n, s, d in tests],
        "summary": {
            "passed": passed,
            "total": total,
            "success_rate": success_rate,
            "mvp_requirements_passed": mvp_passed,
            "mvp_requirements_total": len(mvp_reqs),
            "verdict": verdict,
            "time_remaining_minutes": hours_left * 60 + minutes_left
        },
        "recommendations": []
    }
    
    if verdict in ["EXCELLENT", "GOOD"]:
        report["recommendations"].append("Proceed with deployment to Vercel")
    else:
        report["recommendations"].append("Address issues before deployment")
    
    with open("/tmp/final_quick_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to: /tmp/final_quick_test_report.json")
    
    return verdict in ["EXCELLENT", "GOOD"]

if __name__ == "__main__":
    import sys
    success = quick_test()
    sys.exit(0 if success else 1)