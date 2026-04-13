// Vercel-compatible Node.js API
// Using CommonJS for maximum compatibility

const http = require('http');

// Simple RAG system
const documents = [
  {
    id: 'doc_001',
    text: 'La Dirección de Inspección y Vigilancia tiene facultades para verificar el cumplimiento de normativas municipales en materia de comercio, construcción y condiciones de seguridad en centros de trabajo.',
    source: 'Reglamento Municipal de Inspección',
    keywords: ['facultades', 'inspección', 'vigilancia', 'normativas', 'comercio', 'construcción', 'seguridad']
  },
  {
    id: 'doc_002',
    text: 'Los comercios deben cumplir con las normas de seguridad e higiene establecidas en las NOM federales y reglamentos municipales aplicables para el municipio de Zapopan.',
    source: 'NOM-011-STPS-2001',
    keywords: ['comercios', 'normas', 'seguridad', 'higiene', 'NOM', 'reglamentos', 'Zapopan']
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
    return 'No encontré información específica sobre este tema. Consulta los reglamentos oficiales.';
  }
  
  const context = documents.map((doc, i) => `${i + 1}. ${doc.text}`).join('\n\n');
  const sources = [...new Set(documents.map(d => d.source))].join(', ');
  
  return `**Consulta:** ${query}

**Información relevante:**

${context}

**Fuentes:** ${sources}

*Sistema MVP Chatbot Inspección Zapopan - Node.js*`;
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
  
  // Serve simple frontend for all other routes
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Chatbot Inspección Zapopan</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: #003366; color: white; padding: 20px; border-radius: 10px; text-align: center; }
        .chat { margin: 20px 0; }
        .message { padding: 10px; margin: 5px; border-radius: 5px; }
        .user { background: #e3f2fd; margin-left: 20%; }
        .bot { background: #f1f8e9; margin-right: 20%; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ Chatbot Inspección Zapopan</h1>
        <p>MVP Node.js - Desplegado en Vercel</p>
        <p><strong>✅ Sistema operativo con RAG básico</strong></p>
    </div>
    
    <div class="chat">
        <div class="message bot">
            <strong>🤖 Chatbot:</strong> ¡Hola! Soy el chatbot de Inspección y Vigilancia de Zapopan.
            Puedo responder preguntas sobre facultades y normativas.
        </div>
    </div>
    
    <div style="text-align: center; margin-top: 30px;">
        <p><strong>Health Check:</strong> <span id="healthStatus">Verificando...</span></p>
        <p><strong>Runtime:</strong> Node.js CommonJS</p>
        <p><strong>Estado:</strong> MVP Completado ✅</p>
    </div>
    
    <script>
        fetch('/health')
            .then(r => r.json())
            .then(data => {
                document.getElementById('healthStatus').textContent = data.status;
                document.getElementById('healthStatus').style.color = 'green';
            })
            .catch(() => {
                document.getElementById('healthStatus').textContent = 'Error';
                document.getElementById('healthStatus').style.color = 'red';
            });
    </script>
</body>
</html>
  `);
});

// Export for Vercel
module.exports = server;