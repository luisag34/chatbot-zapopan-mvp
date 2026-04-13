#!/usr/bin/env python3
"""
Script para ejecutar el backend del Chatbot Zapopan localmente
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys

# Configurar SECRET_KEY para desarrollo local
os.environ['SECRET_KEY'] = 'dev_secret_key_local_123'

# HTML frontend como string constante (copiado de api/index.py)
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
        .endpoints { background-color: #e3f2fd; padding: 20px; border-radius: 5px; margin: 20px 0; }
        code { background-color: #f1f1f1; padding: 2px 5px; border-radius: 3px; font-family: 'Courier New', monospace; }
        .button { background-color: #003366; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 10px 5px; text-decoration: none; display: inline-block; }
        .button:hover { background-color: #002244; }
        .login-form { max-width: 400px; margin: 30px auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; background-color: #f9f9f9; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ Chatbot Inspección y Vigilancia Zapopan</h1>
        <p>Sistema de consulta sobre facultades de la Dirección de Inspección y Vigilancia</p>
        <p><strong>Acceso restringido a personal autorizado</strong></p>
    </div>

    <div class="container">
        <div class="status">
            <h2>✅ Sistema Operativo</h2>
            <p>Backend ejecutándose localmente - Testing</p>
            <p><strong>URL:</strong> <code>http://localhost:8000</code></p>
            <p><strong>Fecha:</strong> 8 de Abril 2026</p>
            <p><strong>Estado:</strong> <span style="color: #4caf50;">●</span> En línea (Local)</p>
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

        <div class="endpoints">
            <h2>🔌 Endpoints Disponibles</h2>
            <ul>
                <li><code>GET /health</code> - Estado del sistema</li>
                <li><code>POST /api/login</code> - Autenticación</li>
                <li><code>POST /api/chat</code> - Chat con el bot</li>
                <li><code>GET /</code> - Esta interfaz</li>
            </ul>
        </div>

        <h2>📋 Testing Rápido</h2>
        <p>
            <a href="/health" class="button">Verificar Salud</a>
            <button class="button" onclick="testLogin()">Probar Login</button>
            <button class="button" onclick="testChat()">Probar Chat</button>
        </p>

        <div id="testResults" style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px; display: none;">
            <h3>Resultados de Test</h3>
            <pre id="testOutput"></pre>
        </div>
    </div>

    <script>
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
                    alert(`✅ Login exitoso\nBienvenido: ${data.user.name}\nToken: ${data.token.substring(0, 20)}...`);
                } else {
                    alert(`❌ Error: ${data.error || 'Credenciales incorrectas'}`);
                }
            } catch (error) {
                alert(`❌ Error de conexión: ${error.message}`);
            }
        });

        function testLogin() {
            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: 'administrador_supremo',
                    password: ''  // CONTRASEÑA ROTADA
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

        function testChat() {
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
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"status": "ok", "service": "Chatbot Inspección Zapopan API", "environment": "local"}
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
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data) if content_length > 0 else {}
        
        if self.path == "/api/login":
            # Simulación simple de autenticación
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
            # Respuesta simulada para testing
            user_message = data.get("message", "")
            token = data.get("token", "")
            
            response = {
                "success": True,
                "response": f"✅ Respuesta simulada del chatbot (local)\n\nPregunta: {user_message}\n\nEste es el backend local funcionando correctamente. Para respuestas reales, implementar sistema RAG.",
                "sources": ["Sistema local de testing"],
                "timestamp": "2026-04-08T11:35:00Z"
            }
            self.send_response(200)
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
    
    print(f"🚀 Iniciando backend Chatbot Zapopan en http://localhost:{port}")
    print(f"📅 Fecha: 8 de Abril 2026")
    print(f"⏰ Hora: 11:35 AM CST")
    print(f"🎯 Objetivo: MVP Deadline 16:48 CST")
    print(f"🔧 Modo: Local testing")
    print(f"📋 Endpoints:")
    print(f"   GET  /health      - Estado del sistema")
    print(f"   GET  /            - Interfaz web")
    print(f"   POST /api/login   - Autenticación")
    print(f"   POST /api/chat    - Chatbot")
    print(f"\nPresiona Ctrl+C para detener el servidor\n")
    
    httpd = HTTPServer(server_address, ChatbotHTTPRequestHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido")
        httpd.server_close()

if __name__ == "__main__":
    main()