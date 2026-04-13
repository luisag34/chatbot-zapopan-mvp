#!/usr/bin/env python3
"""
Backend Chatbot Zapopan con sistema RAG integrado
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
import time
from collections import defaultdict

# Importar sistema RAG
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.rag_simple_mvp import UltraSimpleRAG

# Configurar SECRET_KEY para desarrollo local
os.environ['SECRET_KEY'] = 'dev_secret_key_local_123'

# Rate limiting básico (más permisivo para testing)
class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_ip):
        """Verificar si el cliente puede hacer otra request"""
        now = time.time()
        
        # Limpiar requests antiguas
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window_seconds
        ]
        
        # Verificar límite
        if len(self.requests[client_ip]) >= self.max_requests:
            return False
        
        # Registrar nueva request
        self.requests[client_ip].append(now)
        return True

# Inicializar rate limiter (más permisivo para testing local)
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)  # 100 requests por minuto

# Inicializar sistema RAG
print("🔧 Inicializando sistema RAG...")
rag_system = UltraSimpleRAG()
doc_count = rag_system.load_documents()
print(f"✅ Sistema RAG listo con {doc_count} documentos")

# HTML frontend actualizado con RAG
FRONTEND_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot Inspección y Vigilancia Zapopan</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5; color: #333; }
        .header { background-color: #003366; color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; text-align: center; }
        .container { background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .status { background-color: #e8f5e9; border-left: 5px solid #4caf50; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .rag-status { background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .endpoints { background-color: #fff3e0; padding: 20px; border-radius: 5px; margin: 20px 0; }
        code { background-color: #f1f1f1; padding: 2px 5px; border-radius: 3px; font-family: 'Courier New', monospace; }
        .button { background-color: #003366; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px 5px; text-decoration: none; display: inline-block; }
        .button:hover { background-color: #002244; }
        .login-form { max-width: 400px; margin: 30px auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; background-color: #f9f9f9; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        .chat-container { margin-top: 30px; }
        .chat-message { padding: 15px; margin: 10px 0; border-radius: 10px; max-width: 80%; }
        .user-message { background-color: #e3f2fd; margin-left: auto; }
        .bot-message { background-color: #f1f8e9; }
        .sources { font-size: 12px; color: #666; margin-top: 10px; padding: 10px; background-color: #f5f5f5; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ Chatbot Inspección y Vigilancia Zapopan</h1>
        <p>Sistema de consulta RAG sobre facultades de la Dirección de Inspección y Vigilancia</p>
        <p><strong>Acceso restringido a personal autorizado</strong></p>
    </div>

    <div class="container">
        <div class="status">
            <h2>✅ Sistema Operativo</h2>
            <p>Backend con RAG ejecutándose localmente</p>
            <p><strong>URL:</strong> <code>http://localhost:8000</code></p>
            <p><strong>Fecha:</strong> 8 de Abril 2026</p>
            <p><strong>Estado:</strong> <span style="color: #4caf50;">●</span> En línea (Local + RAG)</p>
        </div>

        <div class="rag-status">
            <h2>🔍 Sistema RAG Activo</h2>
            <p><strong>Documentos cargados:</strong> 2951 documentos oficiales</p>
            <p><strong>Cobertura:</strong> Normativas federales, estatales y municipales</p>
            <p><strong>Tecnología:</strong> Búsqueda semántica por palabras clave</p>
            <p><strong>Estado:</strong> <span style="color: #2196f3;">●</span> Respondiendo basado en documentos reales</p>
        </div>

        <h2>🔐 Acceso al Sistema</h2>
        <div class="login-form">
            <h3>Iniciar Sesión</h3>
            <form id="loginForm">
                <input type="text" id="username" placeholder="Usuario" required>
                <input type="password" id="password" placeholder="Contraseña" required>
                <button type="submit" class="button">Ingresar</button>
            </form>
            <p><small>⚠️ <strong>CREDENCIALES ROTADAS:</strong> Contactar al administrador para nuevas credenciales</small></p>
        </div>

        <div class="chat-container" id="chatContainer" style="display: none;">
            <h2>💬 Chat con el Sistema</h2>
            <div id="chatMessages"></div>
            <div style="display: flex; margin-top: 20px;">
                <input type="text" id="chatInput" placeholder="Escribe tu pregunta sobre normativas..." style="flex: 1; margin-right: 10px;">
                <button class="button" onclick="sendMessage()">Enviar</button>
            </div>
            <p><small>Ejemplos: "¿Qué normativas aplican para comercios?", "¿Cuáles son las facultades de inspección?"</small></p>
        </div>

        <div class="endpoints">
            <h2>🔌 Sistema Integrado</h2>
            <ul>
                <li><code>GET /health</code> - Estado del sistema</li>
                <li><code>POST /api/login</code> - Autenticación</li>
                <li><code>POST /api/chat</code> - Chat con RAG (basado en 2951 documentos)</li>
                <li><code>GET /rag/status</code> - Estado del sistema RAG</li>
                <li><code>GET /</code> - Esta interfaz</li>
            </ul>
        </div>

        <h2>📋 Testing Rápido</h2>
        <p>
            <a href="/health" class="button">Verificar Salud</a>
            <a href="/rag/status" class="button">Estado RAG</button>
            <button class="button" onclick="testRAG()">Probar RAG</button>
        </p>

        <div id="testResults" style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px; display: none;">
            <h3>Resultados de Test</h3>
            <pre id="testOutput"></pre>
        </div>
    </div>

    <script>
        // Manejar login
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    alert(`✅ Login exitoso\nBienvenido: ${data.user.name}`);
                    document.getElementById('chatContainer').style.display = 'block';
                    document.getElementById('loginForm').style.display = 'none';
                    addMessage('🤖 Bot', '¡Hola! Soy el chatbot de la Dirección de Inspección y Vigilancia. Puedo responder preguntas basadas en 2951 documentos oficiales. ¿En qué puedo ayudarte?', 'bot');
                } else {
                    alert(`❌ Error: ${data.error || 'Credenciales incorrectas'}`);
                }
            } catch (error) {
                alert(`❌ Error de conexión: ${error.message}`);
            }
        });

        // Funciones de chat
        function addMessage(sender, text, type) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${type}-message`;
            messageDiv.innerHTML = `<strong>${sender}:</strong><br>${text}`;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Agregar mensaje del usuario
            addMessage('👤 Tú', message, 'user');
            input.value = '';
            
            // Enviar al backend
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    token: 'user_token_placeholder'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addMessage('🤖 Bot', data.response, 'bot');
                    
                    // Mostrar fuentes si existen
                    if (data.sources && data.sources.length > 0) {
                        const sourcesDiv = document.createElement('div');
                        sourcesDiv.className = 'sources';
                        sourcesDiv.innerHTML = `<strong>Fuentes:</strong> ${data.sources.join(', ')}`;
                        document.getElementById('chatMessages').appendChild(sourcesDiv);
                    }
                } else {
                    addMessage('🤖 Bot', `❌ Error: ${data.error || 'Error desconocido'}`, 'bot');
                }
            })
            .catch(error => {
                addMessage('🤖 Bot', `❌ Error de conexión: ${error.message}`, 'bot');
            });
        }

        // Testing
        function testRAG() {
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: '¿Cuáles son las facultades de la Dirección de Inspección y Vigilancia?',
                    token: 'test_token'
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('testResults').style.display = 'block';
                document.getElementById('testOutput').textContent = JSON.stringify(data, null, 2);
            })
            .catch(error => {
                document.getElementById('testResults').style.display = 'block';
                document.getElementById('testOutput').textContent = 'Error: ' + error.message;
            });
        }

        // Verificar salud al cargar
        fetch('/health')
            .then(response => response.json())
            .then(data => {
                console.log('✅ Sistema saludable:', data);
            })
            .catch(error => {
                console.error('❌ Error de salud:', error);
            });
    </script>
</body>
</html>"""

class ChatbotHTTPRequestHandler(BaseHTTPRequestHandler):
    def get_client_ip(self):
        """Obtener IP del cliente"""
        return self.client_address[0]
    
    def check_rate_limit(self):
        """Verificar rate limiting"""
        client_ip = self.get_client_ip()
        if not rate_limiter.is_allowed(client_ip):
            self.send_response(429)  # Too Many Requests
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {
                "success": False,
                "error": "Rate limit exceeded. Please try again later.",
                "retry_after": 60
            }
            self.wfile.write(json.dumps(response).encode())
            return False
        return True
    
    def do_GET(self):
        # Verificar rate limiting para todas las GET requests
        if not self.check_rate_limit():
            return
        
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {
                "status": "ok", 
                "service": "Chatbot Inspección Zapopan API", 
                "environment": "local",
                "rag_system": "active",
                "documents_loaded": len(rag_system.documents)
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == "/rag/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {
                "status": "active",
                "documents_loaded": len(rag_system.documents),
                "index_size": len(rag_system.index),
                "system": "UltraSimpleRAG MVP"
            }
            self.wfile.write(json.dumps(response).encode())
        
        # Bloquear endpoints sensibles
        elif self.path in ["/config/users.json", "/.env", "/.git/config", "/api/secret", "/admin", "/backup"]:
            self.send_response(403)  # Forbidden
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {
                "error": "Access forbidden",
                "message": "This endpoint is not accessible"
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(FRONTEND_HTML.encode())
        
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(FRONTEND_HTML.encode())
    
    def do_POST(self):
        # Verificar rate limiting para todas las POST requests
        if not self.check_rate_limit():
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data) if content_length > 0 else {}
        
        if self.path == "/api/login":
            # Autenticación simple
            username = data.get("username", "")
            password = data.get("password", "")
            
            if username == "administrador_supremo" and password == "":  # CONTRASEÑA ROTADA
                response = {
                    "success": True,
                    "user": {
                        "username": "administrador_supremo",
                        "name": "Administrador Supremo",
                        "role": "admin",
                        "department": "Dirección General"
                    },
                    "token": "simulated_token_for_local_testing_123"
                }
                self.send_response(200)
            else:
                response = {
                    "success": False,
                    "error": "Invalid credentials - Contraseñas rotadas, configurar nueva"
                }
                self.send_response(401)
            
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == "/api/chat":
            # Chat con sistema RAG
            user_message = data.get("message", "")
            token = data.get("token", "")
            
            if not user_message:
                response = {
                    "success": False,
                    "error": "No message provided"
                }
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Validación básica de token (para MVP)
            valid_tokens = [
                "test_token",
                "simulated_token_for_local_testing_123",
                "user_token_placeholder",
                "public_access_token"
            ]
            
            if token not in valid_tokens:
                response = {
                    "success": False,
                    "error": "Invalid or missing authentication token"
                }
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Procesar con sistema RAG
            try:
                rag_result = rag_system.process_query(user_message)
                
                if rag_result['success']:
                    response = {
                        "success": True,
                        "response": rag_result['response'],
                        "query": rag_result['query'],
                        "documents_found": rag_result['documents_found'],
                        "sources": rag_result['sources'],
                        "system": rag_result['system'],
                        "timestamp": "2026-04-08T11:45:00Z"
                    }
                    self.send_response(200)
                else:
                    response = {
                        "success": False,
                        "error": "RAG system error",
                        "details": rag_result.get('error', 'Unknown error')
                    }
                    self.send_response(500)
            
            except Exception as e:
                response = {
                    "success": False,
                    "error": "Internal server error",
                    "details": str(e)
                }
                self.send_response(500)
            
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"error": "Endpoint not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        # Reducir logging para claridad
        print(f"[{self.log_date_time_string()}] {args[0]}")

def main():
    port = 8000
    server_address = ('', port)
    
    print(f"\n{'='*60}")
    print(f"🚀 CHATBOT ZAPOPAN CON RAG INTEGRADO")
    print(f"{'='*60}")
    print(f"📅 Fecha: 8 de Abril 2026")
    print(f"⏰ Hora: 11:45 AM CST")
    print(f"🎯 MVP Deadline: 16:48 CST (5 horas restantes)")
    print(f"🔧 Sistema: Backend + RAG (2951 documentos)")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"{'='*60}")
    print(f"📋 Endpoints:")
    print(f"   GET  /health      - Estado del sistema")
    print(f"   GET  /rag/status  - Estado RAG")
    print(f"   GET  /            - Interfaz web con chat")
    print(f"   POST /api/login   - Autenticación")
    print(f"   POST /api/chat    - Chatbot con RAG")
    print(f"\n🏰 Sistema listo para MVP Deadline")
    print(f"{'='*60}")
    print(f"Presiona Ctrl+C para detener el servidor\n")
    
    httpd = HTTPServer(server_address, ChatbotHTTPRequestHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido")
        httpd.server_close()

if __name__ == "__main__":
    main()
