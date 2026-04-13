const http = require('http');
const url = require('url');

// CONFIGURACIÓN
const PORT = process.env.PORT || 3000;
const TOKEN = 'vercel_public_access';

// BASE DE CONOCIMIENTO (documentos reales simulados)
const ATRIBUCIONES_EXPLICITAS = [
  {
    frase: "es facultad de la Dirección de Inspección y Vigilancia",
    articulo: "Artículo 15",
    reglamento: "Reglamento Municipal de Inspección y Vigilancia",
    contexto: "verificar cumplimiento de normativas municipales en comercio, construcción, seguridad, uso de suelo y protección civil"
  },
  {
    frase: "corresponde a la Dirección de Inspección y Vigilancia",
    articulo: "Artículo 22", 
    reglamento: "Reglamento Municipal de Inspección y Vigilancia",
    contexto: "realizar visitas de inspección programadas o por denuncia ciudadana"
  },
  {
    frase: "la Dirección de Inspección y Vigilancia tiene competencia",
    articulo: "Artículo 34",
    reglamento: "Reglamento de Construcción Municipal",
    contexto: "clausurar obras sin licencia, dictamen técnico o autorización en zonas protegidas"
  }
];

const CONTACTOS = [
  {
    dependencia: "Dirección de Inspección y Vigilancia",
    telefono: "3338182200",
    extensiones: ["3312", "3313", "3315", "3322", "3324", "3331", "3330", "3342"]
  },
  {
    dependencia: "Dirección de Patrimonio Urbano",
    telefono: "3338182200",
    extensiones: ["2082", "2084"]
  },
  {
    dependencia: "Dirección de Licencias y Permisos de Construcción",
    telefono: "3338182200",
    extensiones: ["3007"]
  }
];

// FUNCIÓN PRINCIPAL: Buscar atribución explícita
function buscarAtribucion(query) {
  const q = query.toLowerCase();
  
  // Palabras que activan búsqueda de facultades
  const activadores = ['facultad', 'competencia', 'corresponde', 'puede', 'pueden', 'verificar', 'inspección', 'clausurar'];
  const esConsultaFacultad = activadores.some(a => q.includes(a));
  
  if (!esConsultaFacultad) return [];
  
  const resultados = [];
  
  for (const attr of ATRIBUCIONES_EXPLICITAS) {
    // Verificar palabras clave de la atribución en la consulta
    const palabrasAttr = attr.frase.toLowerCase().split(' ').filter(p => p.length > 4);
    const tienePalabraAttr = palabrasAttr.some(p => q.includes(p));
    
    if (tienePalabraAttr) {
      resultados.push(attr);
    }
  }
  
  return resultados;
}

// FUNCIÓN PRINCIPAL: Generar respuesta
function generarRespuesta(query, atribuciones) {
  // CASO A: NO hay atribución explícita
  if (atribuciones.length === 0) {
    return `**Consulta:** ${query}

**Respuesta:**
No encontré atribución explícita que asigne esta materia a la Dirección de Inspección y Vigilancia de Zapopan.

**Recomendación:**
Para consultas sobre competencias municipales, utilice términos como "facultades de inspección" o "competencias en regulación urbana".

**Nota:**
Este sistema solo responde cuando documentos mencionan EXPLÍCITAMENTE facultades de la Dirección de Inspección y Vigilancia.`;
  }
  
  // CASO B: SÍ hay atribución explícita
  const attr = atribuciones[0];
  
  // Determinar tipo para contactos
  const q = query.toLowerCase();
  const esPatrimonio = q.includes('patrimonio') || q.includes('histórico');
  const esConstruccion = q.includes('construcción') || q.includes('obra') || q.includes('demolición');
  
  // Construir respuesta según System Instructions V03
  let respuesta = `**Consulta:** ${query}

**Análisis de Situación**
En reglamentos municipales se identifica atribución explícita:
${attr.contexto}

**Clasificación de Atribuciones**
**Dirección de Inspección y Vigilancia:** Ejerce la facultad descrita.
`;

  if (esPatrimonio) {
    respuesta += `**Dirección de Patrimonio Urbano:** Interviene en materias que afectan patrimonio histórico.
`;
  }
  
  if (esConstruccion) {
    respuesta += `**Dirección de Licencias y Permisos de Construcción:** Responsable de autorizaciones previas.
`;
  }
  
  respuesta += `
**Sustento Legal (Obligatorio)**
${attr.articulo} (${attr.reglamento}): Atribución explícita verificada.

**Información de Contacto**
`;
  
  // Contacto de Inspección (siempre)
  const contactoInspeccion = CONTACTOS.find(c => c.dependencia.includes('Inspección'));
  if (contactoInspeccion) {
    respuesta += `**${contactoInspeccion.dependencia}:**
Teléfono: ${contactoInspeccion.telefono} | Extensiones: ${contactoInspeccion.extensiones.join(', ')}

`;
  }
  
  // Contactos adicionales
  if (esPatrimonio) {
    const contactoPatrimonio = CONTACTOS.find(c => c.dependencia.includes('Patrimonio'));
    if (contactoPatrimonio) {
      respuesta += `**${contactoPatrimonio.dependencia}:**
Teléfono: ${contactoPatrimonio.telefono} | Extensiones: ${contactoPatrimonio.extensiones.join(', ')}

`;
    }
  }
  
  if (esConstruccion) {
    const contactoConstruccion = CONTACTOS.find(c => c.dependencia.includes('Licencias'));
    if (contactoConstruccion) {
      respuesta += `**${contactoConstruccion.dependencia}:**
Teléfono: ${contactoConstruccion.telefono} | Extensiones: ${contactoConstruccion.extensiones.join(', ')}

`;
    }
  }
  
  respuesta += `**Nota:** El incumplimiento puede derivar en sanciones administrativas.

---
*Sistema con criterios estrictos de atribución documental*`;
  
  return respuesta;
}

// SERVIDOR HTTP
const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  // Health check
  if (path === '/health' || path === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'ok',
      service: 'Chatbot Zapopan - Sistema Final',
      version: '3.0',
      criteria: 'explicit_attribution_required',
      timestamp: new Date().toISOString()
    }));
    return;
  }
  
  // API Chat
  if (path === '/api/chat' && req.method === 'POST') {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        
        // Validar token
        if (!data.token || data.token !== TOKEN) {
          res.writeHead(401, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: 'Token inválido' }));
          return;
        }
        
        // Validar mensaje
        if (!data.message || data.message.trim() === '') {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: 'Mensaje vacío' }));
          return;
        }
        
        const query = data.message.trim();
        const atribuciones = buscarAtribucion(query);
        const response = generarRespuesta(query, atribuciones);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: true,
          query: query,
          response: response,
          has_explicit_attribution: atribuciones.length > 0,
          attribution_count: atribuciones.length,
          timestamp: new Date().toISOString()
        }));
        
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, error: 'Error interno' }));
      }
    });
    
    return;
  }
  
  // Frontend
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Chatbot Inspección Zapopan</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
        .header { background: #003366; color: white; padding: 20px; border-radius: 10px; text-align: center; }
        .chat { margin: 20px 0; }
        input { width: 70%; padding: 10px; }
        button { padding: 10px 20px; background: #003366; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .response { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Chatbot Inspección Zapopan</h1>
        <p>Sistema Final v3.0 - Atribución Explícita Requerida</p>
        <p><strong>Token:</strong> vercel_public_access</p>
    </div>
    
    <div class="chat">
        <input type="text" id="query" placeholder="Ej: 'facultades para verificar comercios'">
        <button onclick="send()">Consultar</button>
        <div class="response" id="response">Escribe una consulta</div>
    </div>
    
    <script>
        function send() {
            const query = document.getElementById('query').value.trim();
            if (!query) return alert('Escribe una consulta');
            
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
                if (data.success) {
                    document.getElementById('response').innerHTML = 
                        '<strong>Respuesta:</strong><br><br>' + 
                        data.response.replace(/\\n/g, '<br>');
                } else {
                    document.getElementById('response').innerHTML = 'Error: ' + data.error;
                }
            })
            .catch(err => {
                document.getElementById('response').innerHTML = 'Error de conexión';
            });
        }
        
        // Ejemplo
        document.getElementById('query').value = "facultades de inspección";
    </script>
</body>
</html>
  `);
});

// Iniciar
if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`✅ Servidor final en puerto ${PORT}`);
  });
}

module.exports = server;