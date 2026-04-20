// ARCHIVO DIAGNÓSTICO - DEBE RESPONDER SI SE EJECUTA
const http = require('http');

const server = http.createServer((req, res) => {
  res.writeHead(200, { 
    'Content-Type': 'application/json',
    'X-Diagnostic': 'true',
    'X-File': 'DIAGNOSTIC.js'
  });
  res.end(JSON.stringify({
    diagnostic: true,
    file: 'DIAGNOSTIC.js',
    timestamp: new Date().toISOString(),
    message: 'If you see this, DIAGNOSTIC.js is running'
  }));
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`DIAGNOSTIC.js running on port ${PORT}`);
  console.log(`This should be the file Vercel executes`);
});

module.exports = server;
