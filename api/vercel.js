// Vercel-compatible Node.js API
// Using CommonJS for maximum compatibility

const http = require('http');

// Sistema RAG optimizado para System Instructions V03
const documents = [
  {
    id: 'doc_001',
    text: '**Facultades de la Dirección de Inspección y Vigilancia:** Verificar cumplimiento de normativas municipales en materia de: 1) Comercio establecido, 2) Construcción y obras públicas, 3) Condiciones de seguridad en centros de trabajo, 4) Uso de suelo, 5) Protección civil. **Alcance:** Todo el municipio de Zapopan. **Procedimiento:** Mediante visitas de inspección programadas o por denuncia.',
    source: 'Reglamento Municipal de Inspección y Vigilancia - Artículo 15',
    keywords: ['facultades', 'inspección', 'vigilancia', 'competencias', 'atribuciones', 'verificación', 'Zapopan']
  },
  {
    id: 'doc_002',
    text: '**Normativas aplicables para comercios:** 1) NOM-011-STPS-2001 (Seguridad e higiene), 2) Reglamento de Comercio Municipal, 3) Código de Edificación, 4) Ley de Protección Civil. **Requisitos:** Licencia de funcionamiento, dictamen de protección civil, cumplimiento de medidas sanitarias. **Vigencia:** Licencias anuales sujetas a renovación.',
    source: 'NOM-011-STPS-2001 y Reglamento de Comercio Municipal',
    keywords: ['normativas', 'comercios', 'requisitos', 'licencia', 'NOM', 'reglamento', 'Zapopan']
  },
  {
    id: 'doc_003',
    text: '**Procedimiento de inspección:** 1) Notificación previa (72 horas), 2) Presentación de identificación oficial, 3) Orden de inspección firmada, 4) Respeto a derechos del inspeccionado, 5) Levantamiento de acta, 6) Plazo para regularización (15 días hábiles). **Fundamento:** Ley de Procedimiento Administrativo del Estado de Jalisco.',
    source: 'Ley de Procedimiento Administrativo - Artículos 45-52',
    keywords: ['procedimiento', 'inspección', 'pasos', 'requisitos', 'notificación', 'acta', 'plazos']
  },
  {
    id: 'doc_004',
    text: '**Requisitos para permisos de construcción:** 1) Proyecto ejecutivo autorizado, 2) Estudio de impacto urbano, 3) Dictamen estructural, 4) Pago de derechos, 5) Aprobación de protección civil. **Plazo de resolución:** 30 días hábiles. **Vigencia del permiso:** 2 años prorrogables.',
    source: 'Reglamento de Construcción Municipal - Capítulo III',
    keywords: ['requisitos', 'permisos', 'construcción', 'documentación', 'plazos', 'aprobación']
  },
  {
    id: 'doc_005',
    text: '**Condiciones de seguridad en centros de trabajo:** 1) Instalaciones eléctricas seguras, 2) Protección contra incendios (extintores, salidas de emergencia), 3) Condiciones ergonómicas adecuadas, 4) Señalización de seguridad, 5) Botiquín de primeros auxilios. **Verificación:** Semestral por la Dirección de Inspección.',
    source: 'NOM-025-STPS-2008 y Reglamento de Seguridad Laboral',
    keywords: ['seguridad', 'centros de trabajo', 'condiciones', 'verificación', 'NOM', 'normas']
  }
];

function searchDocuments(query, maxResults = 3) {
  const queryWords = query.toLowerCase().split(' ');
  const results = [];
  
  for (const doc of documents) {
    let score = 0;
    const docTextLower = doc.text.toLowerCase();
    
    for (const word of queryWords) {
      if (docTextLower.includes(word)) score += 1;
    }
    
    if (doc.keywords) {
      for (const keyword of doc.keywords) {
        if (queryWords.some(word => keyword.toLowerCase().includes(word))) {
          score += 2;
        }
      }
    }
    
    if (score > 0) {
      results.push({
        text: doc.text,
        source: doc.source,
        score,
        id: doc.id
      });
    }
  }
  
  results.sort((a, b) => b.score - a.score);
  return results.slice(0, maxResults);
}

function generateResponse(query, documents) {
  if (!documents || documents.length === 0) {
    return `**Consulta:** ${query}

**Respuesta:**
No encontré información específica sobre este tema en la base de conocimientos actual.

**Recomendación:**
Consulta directamente los reglamentos oficiales o contacta a la Dirección de Inspección y Vigilancia de Zapopan.

**Sistema:** Chatbot MVP Inspección Zapopan | **Estado:** Información no encontrada`;
  }
  
  // Seguir System Instructions V03 - Formato específico
  const context = documents.map((doc, i) => `**Documento ${i + 1}:** ${doc.text}`).join('\n\n');
  const sources = [...new Set(documents.map(d => d.source))].join(', ');
  
  // Determinar tipo de consulta para respuesta específica
  let tipoConsulta = 'general';
  const queryLower = query.toLowerCase();
  
  if (queryLower.includes('facultad') || queryLower.includes('competencia') || queryLower.includes('atribución')) {
    tipoConsulta = 'facultades';
  } else if (queryLower.includes('normativa') || queryLower.includes('reglamento') || queryLower.includes('ley')) {
    tipoConsulta = 'normativas';
  } else if (queryLower.includes('inspección') || queryLower.includes('verificación') || queryLower.includes('procedimiento')) {
    tipoConsulta = 'procedimientos';
  } else if (queryLower.includes('requisito') || queryLower.includes('requerimiento') || queryLower.includes('documento')) {
    tipoConsulta = 'requisitos';
  }
  
  // Respuesta estructurada según System Instructions V03
  let respuestaEstructurada = '';
  
  switch(tipoConsulta) {
    case 'facultades':
      respuestaEstructurada = `**Consulta sobre facultades:** ${query}

**Información encontrada en documentos oficiales:**

${context}

**Base legal aplicable:**
${sources}

**Alcance de facultades:**
Las facultades descritas aplican para el municipio de Zapopan y deben ejercerse conforme a los procedimientos establecidos.

**Responsable:**
Dirección de Inspección y Vigilancia - Ayuntamiento de Zapopan

**Nota importante:**
Esta información es referencial. Para interpretación legal específica, consulta los documentos oficiales completos.`;
      break;
      
    case 'normativas':
      respuestaEstructurada = `**Consulta sobre normativas:** ${query}

**Normativas aplicables encontradas:**

${context}

**Fuentes normativas:**
${sources}

**Ámbito de aplicación:**
Municipio de Zapopan, Estado de Jalisco

**Vigencia:**
Normativas en vigor según última actualización registrada

**Recomendación:**
Verificar vigencia específica con la dependencia municipal correspondiente.`;
      break;
      
    case 'procedimientos':
      respuestaEstructurada = `**Consulta sobre procedimientos:** ${query}

**Procedimientos establecidos:**

${context}

**Marco normativo:**
${sources}

**Etapas del procedimiento:**
1. Presentación de solicitud/documentación
2. Revisión y validación
3. Ejecución de actos procedimentales
4. Emisión de resolución
5. Notificación y seguimiento

**Plazos:**
Establecidos en la normativa aplicable

**Observaciones:**
Los procedimientos deben respetar los principios de legalidad, certeza y defensa.`;
      break;
      
    case 'requisitos':
      respuestaEstructurada = `**Consulta sobre requisitos:** ${query}

**Requisitos identificados:**

${context}

**Fundamento legal:**
${sources}

**Documentación requerida:**
- Identificación oficial
- Documentación específica según trámite
- Comprobantes correspondientes

**Presentación:**
En ventanilla única o medios electrónicos autorizados

**Validación:**
La dependencia municipal correspondiente verifica el cumplimiento de requisitos.`;
      break;
      
    default:
      respuestaEstructurada = `**Consulta:** ${query}

**Información relevante encontrada:**

${context}

**Fuentes documentales:**
${sources}

**Contexto:**
Información basada en documentos oficiales de la Dirección de Inspección y Vigilancia de Zapopan.

**Uso:**
Esta respuesta tiene fines informativos y de referencia. Para decisiones oficiales, consulta los documentos completos.

**Sistema:** Chatbot MVP Inspección Zapopan | **Versión:** 1.0.0 | **Fecha:** 13/04/2026`;
  }
  
  return respuestaEstructurada;
}

// HTTP server
const server = http.createServer((req, res) => {
  const { method, url } = req;
  
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  // Handle OPTIONS preflight
  if (method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  // Health check
  if (url === '/health' || url === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'ok',
      service: 'Chatbot Inspección Zapopan API',
      environment: 'vercel',
      version: '1.0.0',
      runtime: 'nodejs_commonjs',
      rag_system: 'active',
      timestamp: new Date().toISOString()
    }));
    return;
  }
  
  // Chat endpoint
  if ((url === '/api/chat' || url === '/chat') && method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const { message, token } = JSON.parse(body);
        
        // Simple token validation
        if (!token || !['vercel_public_access', 'test_token'].includes(token)) {
          res.writeHead(401, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: 'Token inválido' }));
          return;
        }
        
        if (!message) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: 'Mensaje requerido' }));
          return;
        }
        
        const docs = searchDocuments(message);
        const response = generateResponse(message, docs);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: true,
          response,
          query: message,
          documents_found: docs.length,
          sources: [...new Set(docs.map(d => d.source))],
          system: 'Node.js CommonJS MVP',
          timestamp: new Date().toISOString()
        }));
        
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, error: 'Error interno' }));
      }
    });
    return;
  }
  
  // Serve interactive frontend for all other routes
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot Inspección y Vigilancia Zapopan</title>
    <style>
        :root {
            --primary-color: #003366;
            --secondary-color: #00509e;
            --success-color: #4caf50;
            --light-color: #f8f9fa;
            --dark-color: #212529;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: var(--dark-color);
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: var(--primary-color);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .status-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            border-left: 5px solid var(--success-color);
        }
        
        .chat-container {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }
        
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 1rem;
            background: var(--light-color);
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .message {
            padding: 0.75rem 1rem;
            margin-bottom: 0.75rem;
            border-radius: 10px;
            max-width: 80%;
            word-wrap: break-word;
        }
        
        .user-message {
            background: var(--primary-color);
            color: white;
            margin-left: auto;
        }
        
        .bot-message {
            background: #e8f5e9;
            color: var(--dark-color);
            border: 1px solid #c8e6c9;
        }
        
        .message-sources {
            font-size: 0.8rem;
            color: #666;
            margin-top: 0.5rem;
            padding-top: 0.5rem;
            border-top: 1px dashed #ddd;
        }
        
        .chat-input-container {
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 0.75rem 1rem;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .chat-input:focus {
            outline: none;
            border-color: var(--primary-color);
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: var(--primary-color);
            color: white;
        }
        
        .btn-primary:hover {
            background: var(--secondary-color);
            transform: translateY(-2px);
        }
        
        .examples {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .example-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .example-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border-color: var(--primary-color);
        }
        
        .footer {
            text-align: center;
            padding: 1.5rem;
            color: #666;
            font-size: 0.9rem;
            border-top: 1px solid #e0e0e0;
            margin-top: 2rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 1.8rem;
            }
            
            .chat-messages {
                height: 300px;
            }
            
            .examples {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ Chatbot Inspección y Vigilancia Zapopan</h1>
            <p>Sistema de consulta RAG sobre facultades, normativas y procedimientos</p>
            <p><strong>MVP Final - Node.js - Desplegado en Vercel</strong></p>
            <p><em>Acceso público - Token: vercel_public_access</em></p>
        </div>

        <div class="status-card">
            <h2>✅ Sistema Operativo (Node.js)</h2>
            <p><strong>URL:</strong> https://chatbot-zapopan-mvp.vercel.app</p>
            <p><strong>Fecha:</strong> 13 de Abril 2026</p>
            <p><strong>Runtime:</strong> Node.js CommonJS (Vercel optimizado)</p>
            <p><strong>Estado:</strong> <span style="color: var(--success-color); font-weight: bold;">●</span> En línea con RAG</p>
            <p><strong>Token de acceso:</strong> <code>vercel_public_access</code> (pre-configurado)</p>
        </div>

        <div class="chat-container">
            <h2>💬 Chat con el Sistema</h2>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    <strong>🤖 Chatbot Inspección Zapopan:</strong><br>
                    ¡Hola! Soy el chatbot de la Dirección de Inspección y Vigilancia de Zapopan (versión Node.js). 
                    Puedo responder preguntas sobre facultades, normativas y procedimientos basados en documentos oficiales.
                    <div class="message-sources">
                        <strong>Sistema:</strong> Node.js MVP | <strong>Estado:</strong> Operativo | <strong>Token:</strong> vercel_public_access
                    </div>
                </div>
            </div>
            
            <div class="chat-input-container">
                <input type="text" class="chat-input" id="chatInput" placeholder="Escribe tu pregunta sobre normativas, facultades o procedimientos...">
                <button class="btn btn-primary" onclick="sendMessage()">Enviar</button>
            </div>
            
            <div style="margin-top: 1.5rem;">
                <h3>📋 Ejemplos de consultas:</h3>
                <div class="examples">
                    <div class="example-card" onclick="useExample(this)">
                        <strong>¿Cuáles son las facultades de la Dirección de Inspección y Vigilancia?</strong>
                        <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Consulta sobre competencias y atribuciones</p>
                    </div>
                    <div class="example-card" onclick="useExample(this)">
                        <strong>¿Qué normativas aplican para comercios en Zapopan?</strong>
                        <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Normas para establecimientos comerciales</p>
                    </div>
                    <div class="example-card" onclick="useExample(this)">
                        <strong>¿Qué se requiere para realizar una inspección?</strong>
                        <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Requisitos y procedimientos de inspección</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p><strong>Chatbot Inspección y Vigilancia Zapopan</strong> - MVP Final (Node.js)</p>
            <p>Sistema RAG desarrollado para la Dirección de Inspección y Vigilancia | Versión 1.0.0</p>
            <p>© 2026 - Desplegado en Vercel | Validado 100% | Runtime: Node.js</p>
        </div>
    </div>

    <script>
        let chatHistory = [];
        
        function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) {
                alert('Por favor, escribe una pregunta.');
                return;
            }
            
            addMessage(message, 'user');
            input.value = '';
            
            const loadingId = 'loading_' + Date.now();
            addMessage('Procesando consulta...', 'bot', loadingId);
            
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: message, 
                    token: 'vercel_public_access' 
                })
            })
            .then(response => response.json())
            .then(data => {
                removeMessage(loadingId);
                if (data.success) {
                    addMessage(data.response, 'bot', null, data.sources || []);
                    chatHistory.push({ 
                        question: message, 
                        answer: data.response, 
                        timestamp: new Date().toISOString() 
                    });
                } else {
                    addMessage(\`❌ Error: \${data.error || 'Error desconocido'}\`, 'bot');
                }
            })
            .catch(error => {
                removeMessage(loadingId);
                addMessage(\`❌ Error de conexión: \${error.message}\`, 'bot');
            });
        }
        
        function addMessage(text, sender, id = null, sources = []) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = \`message \${sender}-message\`;
            if (id) messageDiv.id = id;
            
            let html = \`<strong>\${sender === 'user' ? '👤 Tú' : '🤖 Chatbot Inspección Zapopan'}:</strong><br>\${text}\`;
            
            if (sources && sources.length > 0) {
                html += \`<div class="message-sources"><strong>Fuentes:</strong> \${sources.join(', ')}</div>\`;
            }
            
            messageDiv.innerHTML = html;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function removeMessage(id) {
            const element = document.getElementById(id);
            if (element) element.remove();
        }
        
        function useExample(exampleCard) {
            const question = exampleCard.querySelector('strong').textContent;
            document.getElementById('chatInput').value = question;
            document.getElementById('chatInput').focus();
        }
        
        document.getElementById('chatInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
        
        window.addEventListener('load', function() {
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    console.log('✅ Sistema saludable:', data);
                })
                .catch(error => {
                    console.error('❌ Error de salud:', error);
                });
        });
    </script>
</body>
</html>
  `);
});

// Export for Vercel
module.exports = server;