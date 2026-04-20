const http = require('http');
const url = require('url');

// Configuración mínima para Vercel
const PORT = process.env.PORT || 3000;
const TOKEN = 'vercel_public_access';

// Base de datos simplificada (solo para prueba)
const documents = [
  {
    id: 'test_001',
    text: 'Es facultad de la Dirección de Inspección y Vigilancia verificar cumplimiento de normativas municipales.',
    source: 'Reglamento Municipal - Artículo 15',
    atribucion_explicita: true
  }
];

// Health check simple
function handleHealth(req, res) {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    status: 'ok',
    service: 'Chatbot Zapopan MVP',
    version: '2.0-simple',
    timestamp: new Date().toISOString()
  }));
}

// Chat endpoint simple
function handleChat(req, res, data) {
  if (!data.token || data.token !== TOKEN) {
    res.writeHead(401, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: false, error: 'Token inválido' }));
    return;
  }

  const query = data.message || '';
  const hasAttribution = query.toLowerCase().includes('facultad');
  
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    success: true,
    query: query,
    response: hasAttribution 
      ? `**Consulta:** ${query}\n\n**Respuesta:** Se encontró atribución explícita en documentos.\n\n**Sistema:** MVP Simple funcionando.`
      : `**Consulta:** ${query}\n\n**Respuesta:** No se encontró atribución explícita.\n\n**Sistema:** MVP Simple funcionando.`,
    has_explicit_attribution: hasAttribution
  }));
}

// Frontend HTML mínimo
function handleFrontend(req, res) {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Chatbot Zapopan - MVP Simple</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
        .header { background: #003366; color: white; padding: 20px; border-radius: 10px; text-align: center; }
        .chat { margin: 20px 0; }
        input, button { padding: 10px; margin: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Chatbot Zapopan - MVP Simple</h1>
        <p>Versión simplificada para diagnóstico Vercel</p>
        <p><strong>Token:</strong> vercel_public_access</p>
    </div>
    
    <div class="chat">
        <input type="text" id="query" placeholder="Escribe 'facultad' para prueba..." style="width: 70%;">
        <button onclick="sendQuery()">Enviar</button>
        <div id="response" style="margin-top: 20px; padding: 10px; background: #f0f0f0; border-radius: 5px;"></div>
    </div>
    
    <script>
        function sendQuery() {
            const query = document.getElementById('query').value;
            document.getElementById('response').innerHTML = 'Procesando...';
            
            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: query, 
                    token: 'vercel_public_access' 
                })
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('response').innerHTML = 
                    '<strong>Respuesta:</strong><br>' + data.response.replace(/\\n/g, '<br>');
            })
            .catch(err => {
                document.getElementById('response').innerHTML = 'Error: ' + err.message;
            });
        }
    </script>
</body>
</html>
  `);
}

// Servidor principal
const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  // Routing simple
  if (path === '/health' || path === '/api/health') {
    handleHealth(req, res);
    return;
  }
  
  if (path === '/api/chat' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk.toString());
    req.on('end', () => {
      try {
        handleChat(req, res, JSON.parse(body));
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, error: 'JSON inválido' }));
      }
    });
    return;
  }
  
  // Todo lo demás va al frontend
  handleFrontend(req, res);
});

// Iniciar servidor
if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`✅ Servidor simple en puerto ${PORT}`);
  });
}

module.exports = server;