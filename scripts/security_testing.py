#!/usr/bin/env python3
"""
Testing de seguridad básico para Chatbot Zapopan
"""

import requests
import json
import time

def test_sql_injection(base_url: str):
    """Test básico de inyección SQL"""
    print(f"\n🔒 SQL INJECTION TEST")
    
    injection_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT username, password FROM users --",
        "admin' --",
        "1' OR '1'='1' --"
    ]
    
    vulnerable = False
    test_results = []
    
    for payload in injection_payloads:
        try:
            # Test en endpoint de login
            response = requests.post(
                f"{base_url}/api/login",
                json={"username": payload, "password": payload},
                timeout=3
            )
            
            # Si acepta el payload sin error 400/500, podría ser vulnerable
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"   ❌ POTENTIAL VULNERABILITY: Payload '{payload[:20]}...' accepted")
                    vulnerable = True
                else:
                    print(f"   ✅ Payload '{payload[:20]}...' rejected (expected)")
            else:
                print(f"   ✅ Payload '{payload[:20]}...' rejected (status {response.status_code})")
            
            test_results.append({
                "payload": payload,
                "status_code": response.status_code,
                "accepted": response.status_code == 200 and data.get("success", False) if response.status_code == 200 else False
            })
            
        except Exception as e:
            print(f"   ⚠️  Payload '{payload[:20]}...' error: {str(e)[:50]}")
            test_results.append({
                "payload": payload,
                "error": str(e),
                "accepted": False
            })
    
    if not vulnerable:
        print("   🎉 No SQL injection vulnerabilities detected")
    
    return {
        "test": "sql_injection",
        "vulnerable": vulnerable,
        "payloads_tested": len(injection_payloads),
        "details": test_results
    }

def test_xss_injection(base_url: str):
    """Test básico de XSS"""
    print(f"\n🛡️ XSS INJECTION TEST")
    
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg/onload=alert('XSS')>",
        "'\"><script>alert('XSS')</script>"
    ]
    
    vulnerable = False
    test_results = []
    
    for payload in xss_payloads:
        try:
            # Test en endpoint de chat
            response = requests.post(
                f"{base_url}/api/chat",
                json={"message": payload, "token": "test"},
                timeout=3
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                
                # Buscar si el payload aparece en la respuesta (sin sanitizar)
                if payload in response_text:
                    print(f"   ❌ POTENTIAL XSS: Payload reflected in response")
                    vulnerable = True
                else:
                    print(f"   ✅ Payload '{payload[:20]}...' sanitized")
            else:
                print(f"   ✅ Payload '{payload[:20]}...' rejected (status {response.status_code})")
            
            test_results.append({
                "payload": payload,
                "status_code": response.status_code,
                "reflected": payload in response_text if response.status_code == 200 else False
            })
            
        except Exception as e:
            print(f"   ⚠️  Payload '{payload[:20]}...' error: {str(e)[:50]}")
            test_results.append({
                "payload": payload,
                "error": str(e),
                "reflected": False
            })
    
    if not vulnerable:
        print("   🎉 No XSS vulnerabilities detected")
    
    return {
        "test": "xss_injection",
        "vulnerable": vulnerable,
        "payloads_tested": len(xss_payloads),
        "details": test_results
    }

def test_authentication_bypass(base_url: str):
    """Test de bypass de autenticación"""
    print(f"\n🔐 AUTHENTICATION BYPASS TEST")
    
    bypass_attempts = [
        # Token manipulation
        {"token": "admin_token_123", "message": "test"},
        {"token": "../../../etc/passwd", "message": "test"},
        {"token": "<script>", "message": "test"},
        {"token": "' OR '1'='1", "message": "test"},
        
        # Headers manipulation
        {"X-Forwarded-For": "127.0.0.1", "message": "test"},
        {"Authorization": "Bearer fake_token", "message": "test"},
        
        # Parameter pollution
        {"token": ["valid", "invalid"], "message": "test"},
        {"token": "", "message": "test", "admin": "true"}
    ]
    
    bypassed = False
    test_results = []
    
    for i, attempt in enumerate(bypass_attempts):
        try:
            # Extraer token y headers
            token = attempt.get("token", "test") if isinstance(attempt, dict) else attempt
            headers = {"Content-Type": "application/json"}
            
            # Agregar headers especiales si existen
            for key, value in attempt.items():
                if key.startswith("X-") or key.lower() == "authorization":
                    headers[key] = value
            
            # Preparar payload
            payload = {"message": "test message", "token": token}
            
            response = requests.post(
                f"{base_url}/api/chat",
                json=payload,
                headers=headers,
                timeout=3
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"   ❌ POTENTIAL BYPASS: Attempt {i+1} succeeded")
                    bypassed = True
                else:
                    print(f"   ✅ Attempt {i+1} rejected (no success)")
            else:
                print(f"   ✅ Attempt {i+1} rejected (status {response.status_code})")
            
            test_results.append({
                "attempt": i+1,
                "type": "token_manipulation" if "token" in str(attempt) else "header_manipulation",
                "status_code": response.status_code,
                "success": response.status_code == 200 and data.get("success", False) if response.status_code == 200 else False
            })
            
        except Exception as e:
            print(f"   ⚠️  Attempt {i+1} error: {str(e)[:50]}")
            test_results.append({
                "attempt": i+1,
                "error": str(e),
                "success": False
            })
    
    if not bypassed:
        print("   🎉 No authentication bypass vulnerabilities detected")
    
    return {
        "test": "authentication_bypass",
        "bypassed": bypassed,
        "attempts": len(bypass_attempts),
        "details": test_results
    }

def test_rate_limiting(base_url: str):
    """Test de rate limiting básico"""
    print(f"\n⏱️ RATE LIMITING TEST")
    
    # Realizar 20 requests rápidas
    rapid_requests = 20
    success_count = 0
    response_times = []
    
    print(f"   Sending {rapid_requests} rapid requests...")
    
    for i in range(rapid_requests):
        start = time.time()
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            elapsed = time.time() - start
            response_times.append(elapsed)
            
            if response.status_code == 200:
                success_count += 1
            
            # Pequeña pausa pero muy corta para simular ataque
            time.sleep(0.05)
            
        except Exception as e:
            print(f"   ⚠️  Request {i+1} failed: {str(e)[:30]}")
    
    success_rate = success_count / rapid_requests
    
    if success_rate >= 0.9:
        print(f"   ⚠️  NO RATE LIMITING: {success_count}/{rapid_requests} succeeded ({success_rate*100:.0f}%)")
        print("   RECOMMENDATION: Implement rate limiting for production")
        has_limiting = False
    elif success_rate >= 0.5:
        print(f"   ⚠️  WEAK RATE LIMITING: {success_count}/{rapid_requests} succeeded ({success_rate*100:.0f}%)")
        has_limiting = True
    else:
        print(f"   ✅ STRONG RATE LIMITING: {success_count}/{rapid_requests} succeeded ({success_rate*100:.0f}%)")
        has_limiting = True
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print(f"   ⏱️  Average response time: {avg_time:.3f}s")
    
    return {
        "test": "rate_limiting",
        "rapid_requests": rapid_requests,
        "successful_requests": success_count,
        "success_rate": success_rate,
        "has_rate_limiting": has_limiting,
        "recommendation": "Implement rate limiting" if not has_limiting else "Rate limiting adequate"
    }

def test_sensitive_data_exposure(base_url: str):
    """Test de exposición de datos sensibles"""
    print(f"\n📄 SENSITIVE DATA EXPOSURE TEST")
    
    sensitive_endpoints = [
        "/config/users.json",
        "/.env",
        "/.git/config",
        "/api/secret",
        "/admin",
        "/backup"
    ]
    
    exposed = False
    test_results = []
    
    for endpoint in sensitive_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=3)
            
            if response.status_code == 200:
                content = response.text[:100]
                
                # Verificar si parece contener datos sensibles
                sensitive_keywords = ["password", "secret", "key", "token", "admin", "database"]
                has_sensitive = any(keyword in content.lower() for keyword in sensitive_keywords)
                
                if has_sensitive:
                    print(f"   ❌ SENSITIVE DATA: {endpoint} returns data (status 200)")
                    exposed = True
                else:
                    print(f"   ⚠️  {endpoint} accessible (status 200) but no obvious sensitive data")
            elif response.status_code == 404:
                print(f"   ✅ {endpoint} not found (status 404)")
            else:
                print(f"   ✅ {endpoint} protected (status {response.status_code})")
            
            test_results.append({
                "endpoint": endpoint,
                "status_code": response.status_code,
                "exposed": response.status_code == 200 and has_sensitive if response.status_code == 200 else False
            })
            
        except Exception as e:
            print(f"   ⚠️  {endpoint} error: {str(e)[:50]}")
            test_results.append({
                "endpoint": endpoint,
                "error": str(e),
                "exposed": False
            })
    
    if not exposed:
        print("   🎉 No sensitive data exposure detected")
    
    return {
        "test": "sensitive_data_exposure",
        "exposed": exposed,
        "endpoints_tested": len(sensitive_endpoints),
        "details": test_results
    }

def main():
    """Función principal de testing de seguridad"""
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("🔒 SECURITY TESTING - CHATBOT ZAPOPAN")
    print("="*60)
    print(f"Base URL: {base_url}")
    print(f"Start time: {time.strftime('%H:%M:%S')}")
    print("="*60)
    
    all_results = []
    
    try:
        # Ejecutar todos los tests de seguridad
        sql_result = test_sql_injection(base_url)
        all_results.append(sql_result)
        
        xss_result = test_xss_injection(base_url)
        all_results.append(xss_result)
        
        auth_result = test_authentication_bypass(base_url)
        all_results.append(auth_result)
        
        rate_result = test_rate_limiting(base_url)
        all_results.append(rate_result)
        
        data_result = test_sensitive_data_exposure(base_url)
        all_results.append(data_result)
        
        # Resumen de seguridad
        print("\n" + "="*60)
        print("📊 SECURITY TESTING SUMMARY")
        print("="*60)
        
        vulnerabilities = [
            sql_result.get("vulnerable", False),
            xss_result.get("vulnerable", False),
            auth_result.get("bypassed", False),
            data_result.get("exposed", False)
        ]
        
        critical_vulns = sum(vulnerabilities)
        
        if critical_vulns == 0:
            print("🎉 SECURITY: ✅ EXCELLENT")
            print("   No critical vulnerabilities detected")
            security_rating = "EXCELLENT"
        elif critical_vulns == 1:
            print("⚠️ SECURITY: ✅ GOOD")
            print(f"   {critical_vulns} potential vulnerability detected")
            security_rating = "GOOD"
        elif critical_vulns <= 2:
            print("⚠️ SECURITY: ⚠️ FAIR")
            print(f"   {critical_vulns} potential vulnerabilities detected")
            security_rating = "FAIR"
        else:
            print("❌ SECURITY: ❌ POOR")
            print(f"   {critical_vulns} potential vulnerabilities detected")
            security_rating = "POOR"
        
        # Rate limiting check
        if not rate_result.get("has_rate_limiting", True):
            print("   ⚠️  WARNING: No rate limiting detected")
        
        # Guardar reporte
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": base_url,
            "tests": all_results,
            "critical_vulnerabilities": critical_vulns,
            "security_rating": security_rating,
            "recommendations": []
        }
        
        # Recomendaciones basadas en resultados
        if critical_vulns > 0:
            report["recommendations"].append("Address detected security vulnerabilities before production")
        
        if not rate_result.get("has_rate_limiting", True):
            report["recommendations"].append("Implement rate limiting to prevent DoS attacks")
        
        if auth_result.get("bypassed", False):
            report["recommendations"].append("Strengthen authentication and authorization mechanisms")
        
        with open("/tmp/security_testing_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Security report saved to: /tmp/security_testing_report.json")
        
        # Mostrar recomendaciones
        if report["recommendations"]:
            print("\n🔧 SECURITY RECOMMENDATIONS:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")
        
        return 0 if security_rating in ["EXCELLENT", "GOOD"] else 1
        
    except KeyboardInterrupt:
        print("\n\n🛑 Security testing interrupted")
        return 2
    except Exception as e:
        print(f"\n❌ Error in security testing: {e}")
        return 3

if __name__ == "__main__":
    import sys
    sys.exit(main())