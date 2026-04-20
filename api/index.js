// API SIMPLE PARA PRUEBA DE DEPLOYMENT
const http = require('http');

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json');
  
  if (req.url === '/health' || req.url === '/api/health') {
    res.end(JSON.stringify({ 
      status: 'ok', 
      service: 'Chatbot Zapopan - Deployment Test',
      version: '3.2-deployment-test',
      timestamp: new Date().toISOString()
    }));
    return;
  }
  
  if (req.url === '/api/login') {
    res.end(JSON.stringify({ 
      token: 'vercel_public_access', 
      expiresIn: 3600,
      success: true 
    }));
    return;
  }
  
  // Ruta por defecto
  res.end(JSON.stringify({ 
    message: 'API Chatbot Inspección Zapopan - Deployment Test',
    version: '3.2-deployment-test',
    endpoints: ['/health', '/api/login'],
    status: 'deployment_test',
    success: true
  }));
});

server.listen(PORT, () => {
  console.log(`🚀 Servidor deployment test en puerto ${PORT}`);
});

module.exports = server;
