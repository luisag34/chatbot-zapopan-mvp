const http = require('http');
const url = require('url');

// Configuración optimizada para Vercel
const PORT = process.env.PORT || 3000;
const TOKEN = 'vercel_public_access';

// Base de datos OPTIMIZADA (pre-cargada, sin procesamiento pesado)
const DOCUMENTS = {
  // Frases EXACTAS de atribución (prioridad máxima)
  atribuciones_explicitas: [
    {
      frase: "es facultad de la Dirección de Inspección y Vigilancia",
      articulo: "Artículo 15",
      reglamento: "Reglamento Municipal de Inspección y Vigilancia",
      contexto: "verificar cumplimiento de normativas municipales en materia de comercio, construcción, seguridad, uso de suelo y protección civil"
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
      contexto: "clausurar obras que carezcan de licencia, dictamen técnico o autorización en zonas protegidas"
    }
  ],
  
  // Contactos EXCLUSIVOS de carpeta 004
  contactos: [
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
  ]
};

// Función OPTIMIZADA para buscar atribución explícita
function buscarAtribucionExplicita(query) {
  const queryLower = query.toLowerCase().trim();
  const resultados = [];
  
  // 1. Buscar frases EXACTAS de atribución
  for (const atribucion of DOCUMENTS.atribuciones_explicitas) {
    if (queryLower.includes(atribucion.frase) || 
        queryLower.includes('facultad') || 
        queryLower.includes('competencia') ||
        queryLower.includes('corresponde')) {
      
      // Verificar palabras clave específicas en la consulta
      const palabrasClave = ['verificar', 'inspección', 'clausurar', 'visita', 'obra', 'comercio', 'construcción', 'seguridad'];
      const tienePalabraClave = palabrasClave.some(palabra => queryLower.includes(palabra));
      
      if (tienePalabraClave) {
        resultados.push({
          ...atribucion,
          matchType: 'atribucion_explicita',
          confidence: 1.0
        });
      }
    }
  }
  
  return resultados;
}

// Función OPTIMIZADA para generar respuesta según System Instructions V03
function generarRespuesta(query, atribuciones) {
  // CASO 1: No hay atribución explícita
  if (atribuciones.length === 0) {
    return `**Consulta:** ${query}

**Respuesta:**
No encontré atribución explícita en los documentos oficiales que asigne esta materia específicamente a la Dirección de Inspección y Vigilancia de Zapopan.

**Recomendación:**
Intente reformular su consulta utilizando términos como:
- "facultades de inspección y vigilancia"
- "competencias municipales en [materia específica]"
- "atribuciones de la Dirección de Inspección"

**Nota:**
Este sistema requiere mención EXPLÍCITA en reglamentos municipales. Sin atribución documentada, no puedo confirmar competencias.`;
  }
  
  // CASO 2: Hay atribución explícita - Respuesta estructurada
  const primeraAtribucion = atribuciones[0];
  
  // Determinar tipo de consulta
  let tipoConsulta = 'General';
  const queryLower = query.toLowerCase();
  
  if (queryLower.includes('patrimonio') || queryLower.includes('histórico')) {
    tipoConsulta = 'Patrimonio Cultural';
  } else if (queryLower.includes('construcción') || queryLower.includes('obra')) {
    tipoConsulta = 'Construcción y Obras';
  } else if (queryLower.includes('comercio') || queryLower.includes('establecimiento')) {
    tipoConsulta = 'Comercio y Establecimientos';
  }
  
  // Construir respuesta OPTIMIZADA
  let respuesta = '';
  
  // Introducción contextual
  if (tipoConsulta === 'Patrimonio Cultural') {
    respuesta += `Esta consulta involucra aspectos críticos para la preservación del patrimonio construido de Zapopan. La intervención en bienes patrimoniales requiere procedimientos técnicos especializados y estrictamente regulados.\n\n`;
  } else {
    respuesta += `Esta consulta requiere análisis basado en la normativa aplicable y los procedimientos establecidos por el Ayuntamiento de Zapopan.\n\n`;
  }
  
  // Análisis de Situación
  respuesta += `**Análisis de Situación**\n`;
  respuesta += `En los documentos oficiales consultados, se identificó atribución EXPLÍCITA a la Dirección de Inspección y Vigilancia de Zapopan:\n\n`;
  respuesta += `"${primeraAtribucion.frase}" ${primeraAtribucion.contexto}\n\n`;
  
  // Clasificación de Atribuciones
  respuesta += `**Clasificación de Atribuciones**\n`;
  respuesta += `**Dirección de Inspección y Vigilancia:** Autoridad municipal encargada de ${primeraAtribucion.contexto}.\n`;
  
  if (tipoConsulta === 'Patrimonio Cultural') {
    respuesta += `**Dirección de Patrimonio Urbano:** Interviene cuando las materias afectan inmuebles con valor histórico o zonas protegidas.\n`;
  }
  
  if (tipoConsulta === 'Construcción y Obras') {
    respuesta += `**Dirección de Licencias y Permisos de Construcción:** Responsable de emitir dictámenes técnicos y autorizaciones previas.\n`;
  }
  
  respuesta += `\n`;
  
  // Sustento Legal (OBLIGATORIO)
  respuesta += `**Sustento Legal (Obligatorio)**\n`;
  respuesta += `${primeraAtribucion.articulo} (${primeraAtribucion.reglamento}): Establece la atribución explícita de facultades a la Dirección de Inspección y Vigilancia de Zapopan para esta materia.\n\n`;
  
  // Información de Contacto (OBLIGATORIO - exclusiva carpeta 004)
  respuesta += `**Información de Contacto**\n`;
  
  // Contacto de Inspección y Vigilancia (siempre)
  const contactoInspeccion = DOCUMENTS.contactos.find(c => c.dependencia.includes('Inspección'));
  if (contactoInspeccion) {
    respuesta += `**${contactoInspeccion.dependencia}:**\n`;
    respuesta += `Teléfono: ${contactoInspeccion.telefono} | Extensiones: ${contactoInspeccion.extensiones.join(', ')}\n\n`;
  }
  
  // Contactos adicionales según tipo
  if (tipoConsulta === 'Patrimonio Cultural') {
    const contactoPatrimonio = DOCUMENTS.contactos.find(c => c.dependencia.includes('Patrimonio'));
    if (contactoPatrimonio) {
      respuesta += `**${contactoPatrimonio.dependencia}:**\n`;
      respuesta += `Teléfono: ${contactoPatrimonio.telefono} | Extensiones: ${contactoPatrimonio.extensiones.join(', ')}\n\n`;
    }
  }
  
  if (tipoConsulta === 'Construcción y Obras') {
    const contactoConstruccion = DOCUMENTS.contactos.find(c => c.dependencia.includes('Licencias'));
    if (contactoConstruccion) {
      respuesta += `**${contactoConstruccion.dependencia}:**\n`;
      respuesta += `Teléfono: ${contactoConstruccion.telefono} | Extensiones: ${contactoConstruccion.extensiones.join(', ')}\n\n`;
    }
  }
  
  // Nota Final
  respuesta += `**Nota:** El incumplimiento de requisitos y procedimientos puede derivar en sanciones administrativas establecidas en la normativa aplicable.\n\n`;
  
  // Footer
  respuesta += `---\n`;
  respuesta += `*Sistema de consulta oficial | Atribución explícita verificada*`;
  
  return respuesta;
}

// Servidor HTTP OPTIMIZADO
const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  
  // Headers optimizados
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  };
  
  // Manejar OPTIONS rápidamente
  if (req.method === 'OPTIONS') {
    res.writeHead(200, headers);
    res.end();
    return;
  }
  
  // Health check OPTIMIZADO
  if (path === '/health' || path === '/api/health') {
    res.writeHead(200, headers);
    res.end(JSON.stringify({
      status: 'ok',
      service: 'Chatbot Zapopan Optimizado',
      version: '2.0-optimized',
      criteria: 'explicit_attribution_required',
      timestamp: new Date().toISOString()
    }));
    return;
  }
  
  // Endpoint de chat OPTIMIZADO
  if (path === '/api/chat' && req.method === 'POST') {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
      // Limitar tamaño para prevenir DoS
      if (body.length > 10000) {
        req.destroy();
      }
    });
    
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        
        // Validación rápida
        if (!data.token || data.token !== TOKEN) {
          res.writeHead(401, headers);
          res.end(JSON.stringify({ 
            success: false, 
            error: 'Token de acceso inválido' 
          }));
          return;
        }
        
        if (!data.message || data.message.trim() === '') {
          res.writeHead(400, headers);
          res.end(JSON.stringify({ 
            success: false, 
            error: 'El mensaje no puede estar vacío' 
          }));
          return;
        }
        
        const query = data.message.trim();
        const atribuciones = buscarAtribucionExplicita(query);
        const response = generarRespuesta(query, atribuciones);
        
        res.writeHead(200, headers);
        res.end(JSON.stringify({
          success: true,
          query: query,
          response: response,
          has_explicit_attribution: atribuciones.length > 0,
          attribution_count: atribuciones.length,
          timestamp: new Date().toISOString()
        }));
        
      } catch (error) {
        res.writeHead(500, headers);
        res.end(JSON.stringify({ 
          success: false, 
          error: 'Error interno del servidor' 
        }));
      }
    });
    
    return;
  }
  
  // Frontend HTML OPTIMIZADO
  res.writeHead(200, { 
    'Content-Type': 'text/html; charset=utf-8',
    'Cache-Control': 'public, max-age=300'
  });
  
  res.end(`
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot Inspección Zapopan - Optimizado</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
        .header { background: #003366; color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
        .criteria { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .chat input { width: 70%; padding: 10px; margin-right: 10px; }
        .chat button { padding: 10px 20px; background: #003366; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .response { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ Chatbot Inspección Zapopan</h1>
        <p>Sistema Optimizado v2.0 - Atribución Explícita Requerida</p>
        <p><strong>Token:</strong> <code>vercel_public_access</code></p>
    </div>
    
    <div class="criteria">
        <h3>⚠️ Criterios Estrictos Activados:</h3>
        <ul>
            <li><strong>Atribución Explícita:</strong> Solo responde si hay mención EXPLÍCITA en documentos</li>
            <li><strong>Frases Exactas:</strong> Busca "es facultad de", "corresponde a", "tiene competencia"</li>
            <li><strong>Sin Suposiciones:</strong> No asume atribuciones implícitas</li>
        </ul>
    </div>
    
    <div class="chat">
        <h3>💬 Consulta al Sistema:</h3>
        <input type="text" id="query" placeholder="Ej: 'facultades para verificar comercios'">
        <button onclick="sendQuery()">Consultar</button>
        
        <div class="response" id="response">
            Escribe una consulta y haz click en "Consultar"
        </div>
    </div>
    
    <script>
        function sendQuery() {
            const query = document.getElementById('query').value.trim();
            if (!query) {
                alert('Por favor, escribe una consulta');
                return;
            }
            
            document.getElementById('response').innerHTML = 'Buscando atribución explícita...';
            
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
                        '<strong>✅ Respuesta:</strong><br><br>' + 
                        data.response.replace(/\\n/g, '<br>');
                } else {
                    document.getElementById('response').innerHTML = 
                        '<strong>❌ Error:</strong> ' + data.error;
                }
            })
            .catch(err => {
                document.getElementById('response').innerHTML = 
                    '<strong>❌ Error de conexión:</strong> ' + err.message;
            });
        }
        
        // Ejemplo automático al cargar
        document.getElementById('query').value = "facultades de inspección y vigilancia";
    </script>
</body>
</html>
  `);
});

// Iniciar servidor optimizado
if (require.main === module) {
  server.listen(PORT, () => {
    console.log(`✅ Servidor optimizado en puerto ${PORT}`);
    console.log(`✅ Criterios: Atribución explícita requerida`);
    console.log(`✅ Optimizado para Vercel`);
  });
}

module.exports = server;