// API SUPER SIMPLE - SOLO PARA DIAGNÓSTICO
const http = require('http');

const server = http.createServer((req, res) => {
  console.log(`Request: ${req.url}`);
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Hello from Vercel - Diagnostic Test\n');
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Diagnostic server running on port ${PORT}`);
});

module.exports = server;
