#!/usr/bin/env python3
"""
Testing exhaustivo del Chatbot Inspección Zapopan
"""

import json
import requests
import time
import sys
from typing import Dict, List, Any

class ChatbotTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Registrar resultado de test"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            status = "✅"
        else:
            self.results["failed"] += 1
            status = "❌"
        
        self.results["details"].append({
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%H:%M:%S")
        })
        
        print(f"{status} {test_name}: {details}")
        return success
    
    def test_health_endpoint(self):
        """Test endpoint /health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    return self.log_test(
                        "Health Check", 
                        True, 
                        f"Status: {data.get('status')}, Documents: {data.get('documents_loaded', 'N/A')}"
                    )
            return self.log_test("Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            return self.log_test("Health Check", False, f"Error: {str(e)}")
    
    def test_rag_status(self):
        """Test endpoint /rag/status"""
        try:
            response = requests.get(f"{self.base_url}/rag/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "active":
                    return self.log_test(
                        "RAG Status", 
                        True, 
                        f"Active with {data.get('documents_loaded', 0)} documents"
                    )
            return self.log_test("RAG Status", False, f"Status code: {response.status_code}")
        except Exception as e:
            return self.log_test("RAG Status", False, f"Error: {str(e)}")
    
    def test_login_endpoint(self):
        """Test endpoint /api/login"""
        test_users = [
            {"username": "administrador_supremo", "password": "", "expected_role": "admin"},
            {"username": "inspector_01", "password": "", "expected_role": "inspector"},
            {"username": "consultor_01", "password": "", "expected_role": "consultant"}
        ]
        
        passed = 0
        for user in test_users:
            try:
                response = requests.post(
                    f"{self.base_url}/api/login",
                    json={"username": user["username"], "password": user["password"]},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("user", {}).get("role") == user["expected_role"]:
                        passed += 1
            except:
                pass
        
        success = passed >= 2  # Al menos 2 de 3 usuarios funcionan
        return self.log_test(
            "Login Authentication", 
            success, 
            f"{passed}/3 usuarios autenticados correctamente"
        )
    
    def test_chat_endpoint(self):
        """Test endpoint /api/chat con preguntas reales"""
        test_questions = [
            "¿Cuáles son las facultades de la Dirección de Inspección y Vigilancia?",
            "¿Qué normativas aplican para comercios?",
            "¿Qué se requiere para realizar una inspección?",
            "¿Cuáles son los requisitos para permisos de construcción?",
            "¿Qué documentos se necesitan para una verificación?"
        ]
        
        passed = 0
        responses = []
        
        for question in test_questions:
            try:
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json={"message": question, "token": "test_token"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("documents_found", 0) > 0:
                        passed += 1
                        responses.append({
                            "question": question,
                            "documents_found": data.get("documents_found"),
                            "response_preview": data.get("response", "")[:100] + "..."
                        })
            except Exception as e:
                print(f"  ⚠️  Error en pregunta '{question}': {e}")
        
        success = passed >= 3  # Al menos 3 de 5 preguntas funcionan
        details = f"{passed}/5 preguntas respondidas con documentos"
        
        if responses:
            details += f"\n  Ejemplo: '{responses[0]['question']}' → {responses[0]['documents_found']} documentos"
        
        return self.log_test("Chat with RAG", success, details)
    
    def test_frontend_access(self):
        """Test acceso a frontend HTML"""
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                content = response.text
                if "<title>Chatbot Inspección" in content and "Dirección de Inspección" in content:
                    return self.log_test("Frontend HTML", True, "Interfaz web cargada correctamente")
            return self.log_test("Frontend HTML", False, f"Status code: {response.status_code}")
        except Exception as e:
            return self.log_test("Frontend HTML", False, f"Error: {str(e)}")
    
    def test_performance(self):
        """Test de performance básico"""
        start_time = time.time()
        successful_requests = 0
        
        # 5 requests rápidas
        for i in range(5):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=2)
                if response.status_code == 200:
                    successful_requests += 1
            except:
                pass
        
        elapsed_time = time.time() - start_time
        avg_time = elapsed_time / 5 if successful_requests > 0 else 999
        
        success = avg_time < 1.0  # Menos de 1 segundo promedio
        return self.log_test(
            "Performance", 
            success, 
            f"Avg response: {avg_time:.2f}s, Success: {successful_requests}/5"
        )
    
    def test_error_handling(self):
        """Test manejo de errores"""
        tests = [
            ("POST /api/chat sin mensaje", {"token": "test"}, 400),
            ("POST /api/login sin credenciales", {}, 401),
            ("GET endpoint inexistente", None, 404)
        ]
        
        passed = 0
        for test_name, data, expected_code in tests:
            try:
                if test_name.startswith("GET"):
                    response = requests.get(f"{self.base_url}/endpoint_inexistente", timeout=3)
                else:
                    endpoint = "/api/chat" if "chat" in test_name else "/api/login"
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data if data else {},
                        timeout=3
                    )
                
                if response.status_code == expected_code:
                    passed += 1
            except:
                pass
        
        success = passed >= 2  # Al menos 2 de 3 tests de error
        return self.log_test("Error Handling", success, f"{passed}/3 errores manejados correctamente")
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        print("\n" + "="*60)
        print("🏰 TESTING EXHAUSTIVO - CHATBOT ZAPOPAN")
        print("="*60)
        print(f"Base URL: {self.base_url}")
        print(f"Hora inicio: {time.strftime('%H:%M:%S')}")
        print("="*60 + "\n")
        
        # Ejecutar tests
        tests = [
            self.test_health_endpoint,
            self.test_rag_status,
            self.test_login_endpoint,
            self.test_chat_endpoint,
            self.test_frontend_access,
            self.test_performance,
            self.test_error_handling
        ]
        
        for test_func in tests:
            test_func()
            time.sleep(0.5)  # Pequeña pausa entre tests
        
        # Mostrar resumen
        print("\n" + "="*60)
        print("📊 RESUMEN DE TESTING")
        print("="*60)
        print(f"Total tests: {self.results['total_tests']}")
        print(f"✅ Aprobados: {self.results['passed']}")
        print(f"❌ Fallados: {self.results['failed']}")
        print(f"📈 Tasa éxito: {(self.results['passed']/self.results['total_tests']*100):.1f}%")
        print("="*60)
        
        # Mostrar detalles
        print("\n📋 DETALLES POR TEST:")
        for detail in self.results["details"]:
            print(f"  {detail['status']} {detail['test']}: {detail['details']}")
        
        # Determinar si pasa testing
        pass_rate = self.results['passed'] / self.results['total_tests']
        if pass_rate >= 0.8:  # 80% mínimo para pasar
            print("\n" + "="*60)
            print("🎉 TESTING EXHAUSTIVO: ✅ APROBADO")
            print("="*60)
            return True
        else:
            print("\n" + "="*60)
            print("⚠️ TESTING EXHAUSTIVO: ❌ REPROBADO")
            print("="*60)
            return False

def main():
    """Función principal"""
    tester = ChatbotTester()
    
    try:
        success = tester.run_all_tests()
        
        # Guardar resultados
        with open("/tmp/chatbot_testing_results.json", "w") as f:
            json.dump(tester.results, f, indent=2)
        
        print(f"\n📄 Resultados guardados en: /tmp/chatbot_testing_results.json")
        
        # Recomendaciones basadas en resultados
        print("\n🔧 RECOMENDACIONES:")
        if success:
            print("  1. ✅ Sistema listo para deployment en Vercel")
            print("  2. ✅ Proceder con actualización de producción")
            print("  3. ✅ Realizar testing de integración final")
        else:
            print("  1. ⚠️  Corregir tests fallidos antes de deployment")
            print("  2. ⚠️  Revisar logs en /tmp/chatbot_log_2.txt")
            print("  3. ⚠️  Validar conexión y configuración")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n🛑 Testing interrumpido por usuario")
        return 2
    except Exception as e:
        print(f"\n❌ Error en testing: {e}")
        return 3

if __name__ == "__main__":
    sys.exit(main())