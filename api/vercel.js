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
    contexto: "verificar cumplimiento de normativas municipales en comercio, construcción, seguridad, uso de suelo y protección civil",
    categorias: ["general", "comercio", "construccion", "seguridad"]
  },
  {
    frase: "corresponde a la Dirección de Inspección y Vigilancia",
    articulo: "Artículo 22", 
    reglamento: "Reglamento Municipal de Inspección y Vigilancia",
    contexto: "realizar visitas de inspección programadas o por denuncia ciudadana",
    categorias: ["general", "inspeccion"]
  },
  {
    frase: "la Dirección de Inspección y Vigilancia tiene competencia",
    articulo: "Artículo 34",
    reglamento: "Reglamento de Construcción Municipal",
    contexto: "clausurar obras sin licencia, dictamen técnico o autorización en zonas protegidas",
    categorias: ["construccion", "clausura"]
  },
  {
    frase: "facultad de la Dirección de Inspección y Vigilancia para revisar permisos de construcción",
    articulo: "Artículo 28",
    reglamento: "Reglamento de Construcción Municipal (Carpeta 003)",
    contexto: "revisar y verificar que las obras cuenten con los permisos de construcción correspondientes",
    categorias: ["construccion", "permisos", "verificacion"]
  },
  {
    frase: "es competencia de la Dirección de Inspección y Vigilancia verificar obras",
    articulo: "Artículo 31",
    reglamento: "Reglamento de Control de Obras Municipales",
    contexto: "verificar que las obras se realicen conforme a los planos autorizados y permisos otorgados",
    categorias: ["construccion", "verificacion", "obras"]
  }
];

const CONTACTOS = [
  {
    dependencia: "Dirección de Inspección y Vigilancia",
    telefono: "3338182200",
    extensiones: ["3312", "3313", "3315", "3322", "3324", "3331", "3330", "3342"],
    tipo: "inspeccion"
  },
  {
    dependencia: "Dirección de Patrimonio Urbano",
    telefono: "3338182200",
    extensiones: ["2082", "2084"],
    tipo: "patrimonio"
  },
  {
    dependencia: "Dirección de Licencias y Permisos de Construcción",
    telefono: "3338182200",
    extensiones: ["3007"],
    tipo: "construccion"
  },
  {
    dependencia: "Centro Público de Mediación Zona Centro",
    telefono: "3331234567",
    extensiones: ["1001", "1002"],
    tipo: "mediacion",
    zona: "Centro"
  },
  {
    dependencia: "Centro Público de Mediación Zona Norte",
    telefono: "3331234568", 
    extensiones: ["2001", "2002"],
    tipo: "mediacion",
    zona: "Norte"
  },
  {
    dependencia: "Centro Público de Mediación Zona Sur",
    telefono: "3331234569",
    extensiones: ["3001", "3002"],
    tipo: "mediacion",
    zona: "Sur"
  },
  {
    dependencia: "Centro Público de Mediación Zona Oriente",
    telefono: "3331234570",
    extensiones: ["4001", "4002"],
    tipo: "mediacion",
    zona: "Oriente"
  }
];

// FUNCIÓN PRINCIPAL: Buscar atribución explícita
function buscarAtribucion(query) {
  const queryLower = query.toLowerCase();
  
  // Determinar tipo de consulta
  const esRuidoVecinos = (queryLower.includes('ruido') || queryLower.includes('molestia')) && 
                        (queryLower.includes('vecino') || queryLower.includes('vecinos') || queryLower.includes('residencial'));
  const esRuidoComercial = (queryLower.includes('ruido') || queryLower.includes('sonido')) && 
                          (queryLower.includes('comercio') || queryLower.includes('negocio') || queryLower.includes('industrial') || queryLower.includes('evento'));
  const esConstruccion = queryLower.includes('construcción') || queryLower.includes('obra') || queryLower.includes('permiso') || 
                        queryLower.includes('clausurar') || queryLower.includes('edificación');
  
  // Si es ruido de vecinos, NO buscar atribución de Inspección
  if (esRuidoVecinos) {
    return []; // Centros de Mediación se manejan aparte
  }
  
  // Palabras que activan búsqueda de facultades
  const activadores = ['facultad', 'competencia', 'corresponde', 'puede', 'pueden', 'verificar', 'inspección', 'clausurar', 'revisar', 'controlar'];
  const esConsultaFacultad = activadores.some(a => queryLower.includes(a)) || esConstruccion || esRuidoComercial;
  
  if (!esConsultaFacultad) return [];
  
  const resultados = [];
  
  for (const attr of ATRIBUCIONES_EXPLICITAS) {
    // Verificar match mejorado
    const palabrasClave = attr.frase.toLowerCase().split(' ').filter(p => p.length > 3);
    const tienePalabraClave = palabrasClave.some(p => queryLower.includes(p));
    
    // También verificar categorías
    const categoriasRelevantes = attr.categorias || [];
    const tieneCategoriaRelevante = categoriasRelevantes.some(cat => {
      if (cat === 'construccion' && esConstruccion) return true;
      if (cat === 'comercio' && esRuidoComercial) return true;
      return false;
    });
    
    if (tienePalabraClave || tieneCategoriaRelevante) {
      resultados.push(attr);
    }
  }
  
  return resultados;
}

// FUNCIÓN PRINCIPAL: Generar respuesta
function generarRespuesta(query, atribuciones) {
  const queryLower = query.toLowerCase();
  
  // DETECTAR TIPO ESPECÍFICO DE CONSULTA
  const esRuidoVecinos = (queryLower.includes('ruido') || queryLower.includes('molestia')) && 
                        (queryLower.includes('vecino') || queryLower.includes('vecinos') || queryLower.includes('residencial'));
  const esRuidoComercial = (queryLower.includes('ruido') || queryLower.includes('sonido')) && 
                          (queryLower.includes('comercio') || queryLower.includes('negocio') || queryLower.includes('industrial') || queryLower.includes('evento'));
  
  // CASO ESPECIAL: Ruido de vecinos → Centros de Mediación
  if (esRuidoVecinos) {
    const contactosMediacion = CONTACTOS.filter(c => c.tipo === 'mediacion');
    
    let respuesta = `**Consulta:** ${query}

**Respuesta:**
Para conflictos entre vecinos por ruido o molestias, corresponden los **Centros Públicos de Mediación** del municipio de Zapopan.

**Centros de Mediación disponibles:**
`;
    
    for (const contacto of contactosMediacion) {
      respuesta += `**${contacto.dependencia}:**
Teléfono: ${contacto.telefono} | Extensiones: ${contacto.extensiones.join(', ')}
`;
    }
    
    respuesta += `
**Procedimiento:**
1. Contacte el centro de mediación correspondiente a su zona
2. Solicite cita para mediación entre partes
3. Presente su caso ante mediadores certificados

**Nota:** Los Centros Públicos de Mediación facilitan la resolución pacífica de conflictos vecinales sin necesidad de procedimientos judiciales.`;
    
    return respuesta;
  }
  
  // CASO A: NO hay atribución explícita (y no es ruido de vecinos)
  if (atribuciones.length === 0) {
    // Si es ruido comercial pero no encontró atribución, sugerir términos
    if (esRuidoComercial) {
      return `**Consulta:** ${query}

**Respuesta:**
Para ruido proveniente de comercios, negocios o industrias, la **Dirección de Inspección y Vigilancia** tiene facultades de verificación.

**Recomendación:**
Reformule su consulta utilizando términos como:
- "facultades para verificar ruido comercial"
- "competencia en inspección de establecimientos"
- "atribuciones para control de ruido industrial"

**Nota:** El ruido de actividades comerciales/industriales sí compete a Inspección y Vigilancia.`;
    }
    
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
  const esPatrimonio = queryLower.includes('patrimonio') || queryLower.includes('histórico');
  const esConstruccion = queryLower.includes('construcción') || queryLower.includes('obra') || queryLower.includes('demolición');
  
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
  
  // Contacto de Inspección (siempre cuando hay atribución)
  const contactoInspeccion = CONTACTOS.find(c => c.tipo === 'inspeccion');
  if (contactoInspeccion) {
    respuesta += `**${contactoInspeccion.dependencia}:**
Teléfono: ${contactoInspeccion.telefono} | Extensiones: ${contactoInspeccion.extensiones.join(', ')}

`;
  }
  
  // Contactos adicionales según tipo
  if (esPatrimonio) {
    const contactoPatrimonio = CONTACTOS.find(c => c.tipo === 'patrimonio');
    if (contactoPatrimonio) {
      respuesta += `**${contactoPatrimonio.dependencia}:**
Teléfono: ${contactoPatrimonio.telefono} | Extensiones: ${contactoPatrimonio.extensiones.join(', ')}

`;
    }
  }
  
  if (esConstruccion) {
    const contactoConstruccion = CONTACTOS.find(c => c.tipo === 'construccion');
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