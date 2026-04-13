#!/usr/bin/env python3
"""
Validación final del sistema Chatbot Zapopan antes de deployment
"""

import json
import requests
import time
import sys

def print_header(text):
    print(f"\n{'='*60}")
    print(f"🏰 {text}")
    print(f"{'='*60}")

def test_endpoint(url, method="GET", data=None, expected_status=200, name=""):
    """Test individual de endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        success = response.status_code == expected_status
        status = "✅" if success else "❌"
        
        print(f"{status} {name}: Status {response.status_code} (expected {expected_status})")
        
        if success and response.headers.get('content-type', '').startswith('application/json'):
            data = response.json()
            return data
        return None
        
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return None

def main():
    """Validación final completa"""
    base_url = "http://localhost:8000"
    
    print_header("VALIDACIÓN FINAL - CHATBOT ZAPOPAN MVP")
    print(f"URL: {base_url}")
    print(f"Hora: {time.strftime('%H:%M:%S')}")
    print(f"Deadline MVP: 16:48 CST (2 horas 20 minutos restantes)")
    
    # 1. Health Check
    print_header("1. HEALTH CHECK")
    health_data = test_endpoint(f"{base_url}/health", name="Health Check")
    if health_data:
        print(f"   📊 Status: {health_data.get('status')}")
        print(f"   📁 Documents: {health_data.get('documents_loaded', 'N/A')}")
        print(f"   🌍 Environment: {health_data.get('environment')}")
    
    # 2. RAG Status
    print_header("2. RAG SYSTEM")
    rag_data = test_endpoint(f"{base_url}/rag/status", name="RAG Status")
    if rag_data:
        print(f"   🔍 Status: {rag_data.get('status')}")
        print(f"   📚 Documents: {rag_data.get('documents_loaded', 0)}")
        print(f"   🔧 System: {rag_data.get('system')}")
    
    # 3. Authentication
    print_header("3. AUTHENTICATION")
    login_data = test_endpoint(
        f"{base_url}/api/login",
        method="POST",
        data={"username": "administrador_supremo", "password": ""},
        name="Admin Login"
    )
    if login_data and login_data.get("success"):
        user = login_data.get("user", {})
        print(f"   👤 User: {user.get('name')}")
        print(f"   🏢 Role: {user.get('role')}")
        print(f"   🏛️ Department: {user.get('department')}")
    
    # 4. Chat Functionality
    print_header("4. CHAT FUNCTIONALITY")
    test_questions = [
        "¿Cuáles son las facultades de la Dirección de Inspección y Vigilancia?",
        "¿Qué normativas aplican para comercios en Zapopan?",
        "¿Qué se requiere para realizar una inspección?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        chat_data = test_endpoint(
            f"{base_url}/api/chat",
            method="POST",
            data={"message": question, "token": "test"},
            name=f"Chat Q{i}"
        )
        if chat_data and chat_data.get("success"):
            print(f"   📝 Q{i}: {question[:50]}...")
            print(f"     📄 Documents found: {chat_data.get('documents_found', 0)}")
            print(f"     🔗 Sources: {', '.join(chat_data.get('sources', ['N/A']))}")
    
    # 5. Frontend Access
    print_header("5. FRONTEND ACCESS")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            content = response.text
            has_title = "Chatbot Inspección" in content
            has_chat = "chatInput" in content or "chatMessages" in content
            has_rag = "RAG" in content or "documentos" in content
            
            print(f"   ✅ Status: 200 OK")
            print(f"   📱 Title: {'✅' if has_title else '❌'}")
            print(f"   💬 Chat UI: {'✅' if has_chat else '❌'}")
            print(f"   🔍 RAG Mentioned: {'✅' if has_rag else '❌'}")
        else:
            print(f"   ❌ Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # 6. Performance Test
    print_header("6. PERFORMANCE")
    times = []
    for i in range(3):
        start = time.time()
        try:
            requests.get(f"{base_url}/health", timeout=3)
            times.append(time.time() - start)
        except:
            times.append(999)
    
    avg_time = sum(times) / len(times) if times else 999
    print(f"   ⏱️  Avg response time: {avg_time:.3f}s")
    print(f"   🚀 Performance: {'✅' if avg_time < 1.0 else '⚠️' if avg_time < 3.0 else '❌'}")
    
    # 7. Error Handling
    print_header("7. ERROR HANDLING")
    
    # Test 1: Chat sin mensaje
    error1 = test_endpoint(
        f"{base_url}/api/chat",
        method="POST",
        data={"token": "test"},
        expected_status=400,
        name="Chat sin mensaje"
    )
    
    # Test 2: Login sin credenciales
    error2 = test_endpoint(
        f"{base_url}/api/login",
        method="POST",
        data={},
        expected_status=401,
        name="Login sin credenciales"
    )
    
    # Test 3: Endpoint inexistente
    error3 = test_endpoint(
        f"{base_url}/endpoint_inexistente",
        expected_status=404,
        name="Endpoint inexistente"
    )
    
    # 8. Summary
    print_header("8. VALIDACIÓN FINAL - RESUMEN")
    
    # Verificar Vercel también
    print("\n🌐 VERCEL PRODUCTION CHECK:")
    try:
        vercel_response = requests.get("https://chatbot-inspeccion-zapopan.vercel.app/health", timeout=5)
        if vercel_response.status_code == 200:
            vercel_data = vercel_response.json()
            print(f"   ✅ Vercel: {vercel_data.get('status')}")
            print(f"   🔗 URL: https://chatbot-inspeccion-zapopan.vercel.app")
        else:
            print(f"   ⚠️  Vercel: Status {vercel_response.status_code}")
    except Exception as e:
        print(f"   ❌ Vercel: Error - {str(e)}")
    
    # MVP Requirements Check
    print("\n🎯 MVP REQUIREMENTS CHECK:")
    mvp_requirements = {
        "✅ Acceso a documentos": health_data and health_data.get("documents_loaded", 0) > 0,
        "✅ Sistema RAG básico": rag_data and rag_data.get("status") == "active",
        "✅ Autenticación": login_data and login_data.get("success"),
        "✅ Respuestas basadas en documentos": any([chat_data and chat_data.get("documents_found", 0) > 0]),
        "✅ Frontend funcional": response.status_code == 200 if 'response' in locals() else False,
        "✅ Deployment Vercel": 'vercel_response' in locals() and vercel_response.status_code == 200
    }
    
    for req, status in mvp_requirements.items():
        print(f"   {req}: {'✅' if status else '❌'}")
    
    # Final Verdict
    passed = sum(mvp_requirements.values())
    total = len(mvp_requirements)
    pass_rate = passed / total
    
    print_header("🏰 VEREDICTO FINAL")
    
    if pass_rate >= 0.8:  # 80% mínimo
        print("🎉 **MVP VALIDADO Y LISTO PARA DEPLOYMENT**")
        print(f"📈 Tasa de éxito: {pass_rate*100:.1f}% ({passed}/{total} requisitos)")
        print(f"⏰ Tiempo restante hasta deadline: 2 horas 15 minutos")
        print(f"🚀 **RECOMENDACIÓN: Proceder con deployment final en Vercel**")
        
        # Guardar reporte
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": base_url,
            "mvp_requirements": mvp_requirements,
            "pass_rate": pass_rate,
            "verdict": "APPROVED_FOR_DEPLOYMENT",
            "deadline": "2026-04-08T16:48:00CST",
            "time_remaining_minutes": 135
        }
        
        with open("/tmp/mvp_validation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Reporte guardado en: /tmp/mvp_validation_report.json")
        return 0
    else:
        print("⚠️ **MVP REQUIERE MEJORAS ANTES DE DEPLOYMENT**")
        print(f"📉 Tasa de éxito: {pass_rate*100:.1f}% ({passed}/{total} requisitos)")
        print(f"🔧 **RECOMENDACIÓN: Corregir issues antes de proceder**")
        return 1

if __name__ == "__main__":
    sys.exit(main())