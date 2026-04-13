#!/usr/bin/env python3
"""
Testing de carga y estrés básico para Chatbot Zapopan
"""

import requests
import time
import concurrent.futures
import json
from typing import List, Dict

def stress_test_health(endpoint: str, num_requests: int = 20, max_workers: int = 5):
    """Test de carga en endpoint /health"""
    print(f"\n🔧 STRESS TEST: {endpoint}")
    print(f"   Requests: {num_requests}, Workers: {max_workers}")
    
    def make_request(i):
        start = time.time()
        try:
            response = requests.get(endpoint, timeout=3)
            elapsed = time.time() - start
            return {
                "success": response.status_code == 200,
                "time": elapsed,
                "status": response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "time": time.time() - start,
                "error": str(e)
            }
    
    start_total = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    total_time = time.time() - start_total
    
    # Análisis de resultados
    successful = sum(1 for r in results if r["success"])
    failed = num_requests - successful
    
    times = [r["time"] for r in results if "time" in r]
    avg_time = sum(times) / len(times) if times else 0
    max_time = max(times) if times else 0
    min_time = min(times) if times else 0
    
    print(f"   ✅ Successful: {successful}/{num_requests}")
    print(f"   ❌ Failed: {failed}/{num_requests}")
    print(f"   ⏱️  Avg time: {avg_time:.3f}s")
    print(f"   ⏱️  Min time: {min_time:.3f}s")
    print(f"   ⏱️  Max time: {max_time:.3f}s")
    print(f"   ⏱️  Total time: {total_time:.3f}s")
    print(f"   📈 Requests/sec: {num_requests/total_time:.1f}")
    
    return {
        "endpoint": endpoint,
        "total_requests": num_requests,
        "successful": successful,
        "failed": failed,
        "success_rate": successful/num_requests,
        "avg_response_time": avg_time,
        "requests_per_second": num_requests/total_time
    }

def test_concurrent_chats(base_url: str, num_chats: int = 10):
    """Test de chats concurrentes"""
    print(f"\n💬 CONCURRENT CHAT TEST: {num_chats} chats simultáneos")
    
    questions = [
        "¿Qué normativas aplican?",
        "¿Cuáles son las facultades?",
        "¿Qué se requiere para inspección?",
        "¿Documentos necesarios?",
        "¿Permisos de construcción?"
    ]
    
    def chat_request(i):
        question = questions[i % len(questions)]
        start = time.time()
        try:
            response = requests.post(
                f"{base_url}/api/chat",
                json={"message": question, "token": f"test_{i}"},
                timeout=10
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": data.get("success", False),
                    "time": elapsed,
                    "documents": data.get("documents_found", 0),
                    "question": question
                }
            else:
                return {
                    "success": False,
                    "time": elapsed,
                    "error": f"Status {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "time": time.time() - start,
                "error": str(e)
            }
    
    start_total = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(chat_request, i) for i in range(num_chats)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    total_time = time.time() - start_total
    
    # Análisis
    successful = sum(1 for r in results if r["success"])
    avg_docs = sum(r.get("documents", 0) for r in results if r["success"]) / max(successful, 1)
    times = [r["time"] for r in results if "time" in r]
    avg_time = sum(times) / len(times) if times else 0
    
    print(f"   ✅ Successful chats: {successful}/{num_chats}")
    print(f"   📄 Avg documents per chat: {avg_docs:.1f}")
    print(f"   ⏱️  Avg response time: {avg_time:.3f}s")
    print(f"   ⏱️  Total test time: {total_time:.3f}s")
    
    # Mostrar algunos resultados
    print(f"\n   📋 SAMPLE RESULTS:")
    for i, result in enumerate(results[:3]):
        if result["success"]:
            print(f"     {i+1}. '{result['question'][:30]}...' → {result['documents']} docs, {result['time']:.2f}s")
    
    return {
        "test": "concurrent_chats",
        "total_chats": num_chats,
        "successful": successful,
        "success_rate": successful/num_chats,
        "avg_documents": avg_docs,
        "avg_response_time": avg_time
    }

def test_memory_usage(base_url: str):
    """Test de uso de memoria (aproximado)"""
    print(f"\n🧠 MEMORY USAGE TEST")
    
    # Realizar múltiples requests y medir tiempos
    start_mem_test = time.time()
    response_times = []
    
    for i in range(30):
        start = time.time()
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                response_times.append(time.time() - start)
        except:
            pass
        
        # Pequeña pausa para simular uso sostenido
        time.sleep(0.1)
    
    total_mem_test_time = time.time() - start_mem_test
    
    if response_times:
        initial_avg = sum(response_times[:5]) / 5
        final_avg = sum(response_times[-5:]) / 5
        memory_leak_indicator = final_avg / initial_avg if initial_avg > 0 else 1
        
        print(f"   ⏱️  Test duration: {total_mem_test_time:.1f}s")
        print(f"   📊 Initial avg response: {initial_avg:.3f}s")
        print(f"   📊 Final avg response: {final_avg:.3f}s")
        print(f"   📈 Memory leak indicator: {memory_leak_indicator:.2f}x")
        print(f"   🚨 Leak warning: {'⚠️' if memory_leak_indicator > 1.5 else '✅'}")
        
        return {
            "test": "memory_usage",
            "duration": total_mem_test_time,
            "initial_avg_response": initial_avg,
            "final_avg_response": final_avg,
            "leak_indicator": memory_leak_indicator,
            "has_potential_leak": memory_leak_indicator > 1.5
        }
    else:
        print("   ❌ No valid responses for memory test")
        return None

def test_error_recovery(base_url: str):
    """Test de recuperación de errores"""
    print(f"\n🔄 ERROR RECOVERY TEST")
    
    # 1. Hacer request válido
    print("   1. Valid request...")
    valid_start = time.time()
    try:
        valid_response = requests.get(f"{base_url}/health", timeout=2)
        valid_time = time.time() - valid_start
        print(f"      ✅ Status: {valid_response.status_code}, Time: {valid_time:.3f}s")
    except Exception as e:
        print(f"      ❌ Error: {e}")
        valid_time = 999
    
    # 2. Hacer request inválido (forzar error)
    print("   2. Invalid request (force error)...")
    error_start = time.time()
    try:
        error_response = requests.get(f"{base_url}/invalid_endpoint_123", timeout=2)
        error_time = time.time() - error_start
        print(f"      ⚠️  Status: {error_response.status_code} (expected 404)")
    except Exception as e:
        error_time = time.time() - error_start
        print(f"      ❌ Connection error: {e}")
    
    # 3. Hacer request válido nuevamente (recuperación)
    print("   3. Valid request again (recovery)...")
    recovery_start = time.time()
    try:
        recovery_response = requests.get(f"{base_url}/health", timeout=2)
        recovery_time = time.time() - recovery_start
        
        if recovery_response.status_code == 200:
            print(f"      ✅ Recovery successful: {recovery_time:.3f}s")
            recovery_success = True
        else:
            print(f"      ❌ Recovery failed: Status {recovery_response.status_code}")
            recovery_success = False
    except Exception as e:
        print(f"      ❌ Recovery error: {e}")
        recovery_success = False
        recovery_time = 999
    
    # Evaluar recuperación
    if recovery_success and recovery_time < valid_time * 2:  # No más del doble del tiempo
        print("   🎉 Error recovery: ✅ EXCELLENT")
        recovery_rating = "excellent"
    elif recovery_success:
        print("   ⚠️ Error recovery: ✅ ACCEPTABLE (slower)")
        recovery_rating = "acceptable"
    else:
        print("   ❌ Error recovery: ❌ FAILED")
        recovery_rating = "failed"
    
    return {
        "test": "error_recovery",
        "valid_response_time": valid_time,
        "recovery_response_time": recovery_time,
        "recovery_successful": recovery_success,
        "recovery_rating": recovery_rating
    }

def main():
    """Función principal de testing de estrés"""
    base_url = "http://localhost:8000"
    
    print("="*60)
    print("🏰 STRESS TESTING - CHATBOT ZAPOPAN")
    print("="*60)
    print(f"Base URL: {base_url}")
    print(f"Start time: {time.strftime('%H:%M:%S')}")
    print("="*60)
    
    all_results = []
    
    try:
        # 1. Stress test health endpoint
        health_result = stress_test_health(f"{base_url}/health", num_requests=30, max_workers=10)
        all_results.append(health_result)
        
        # 2. Concurrent chat testing
        chat_result = test_concurrent_chats(base_url, num_chats=15)
        all_results.append(chat_result)
        
        # 3. Memory usage test
        mem_result = test_memory_usage(base_url)
        if mem_result:
            all_results.append(mem_result)
        
        # 4. Error recovery test
        recovery_result = test_error_recovery(base_url)
        all_results.append(recovery_result)
        
        # Resumen final
        print("\n" + "="*60)
        print("📊 STRESS TESTING SUMMARY")
        print("="*60)
        
        success_rates = [r.get("success_rate", 0) for r in all_results if "success_rate" in r]
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
        
        print(f"📈 Average success rate: {avg_success_rate*100:.1f}%")
        
        # Evaluación general
        if avg_success_rate >= 0.9:
            print("🎉 STRESS TESTING: ✅ EXCELLENT")
            print("   Sistema maneja carga alta con excelente performance")
            verdict = "EXCELLENT"
        elif avg_success_rate >= 0.7:
            print("⚠️ STRESS TESTING: ✅ ACCEPTABLE")
            print("   Sistema maneja carga moderada, puede requerir optimización")
            verdict = "ACCEPTABLE"
        else:
            print("❌ STRESS TESTING: ❌ NEEDS IMPROVEMENT")
            print("   Sistema tiene problemas con carga, requiere optimización")
            verdict = "NEEDS_IMPROVEMENT"
        
        # Guardar resultados
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": base_url,
            "tests": all_results,
            "avg_success_rate": avg_success_rate,
            "verdict": verdict,
            "recommendations": []
        }
        
        # Recomendaciones basadas en resultados
        if avg_success_rate < 0.9:
            report["recommendations"].append("Considerar optimización de performance para carga alta")
        if mem_result and mem_result.get("has_potential_leak", False):
            report["recommendations"].append("Investigar posible memory leak en uso sostenido")
        if recovery_result and recovery_result.get("recovery_rating") == "failed":
            report["recommendations"].append("Mejorar manejo y recuperación de errores")
        
        with open("/tmp/stress_testing_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Reporte completo guardado en: /tmp/stress_testing_report.json")
        
        # Mostrar recomendaciones
        if report["recommendations"]:
            print("\n🔧 RECOMENDACIONES:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")
        
        return 0 if verdict in ["EXCELLENT", "ACCEPTABLE"] else 1
        
    except KeyboardInterrupt:
        print("\n\n🛑 Stress testing interrumpido")
        return 2
    except Exception as e:
        print(f"\n❌ Error en stress testing: {e}")
        return 3

if __name__ == "__main__":
    import sys
    sys.exit(main())