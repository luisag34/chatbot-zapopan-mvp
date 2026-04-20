const http = require('http');
const url = require('url');
const fs = require('fs');
const path = require('path');

// CONFIGURACIÓN
const PORT = process.env.PORT || 3000;
const TOKEN = 'vercel_public_access';

// CARGA DE DOCUMENTOS REALES (RAG)
let DOCUMENTOS_RAG = [];

// Función para cargar documentos JSONL
function cargarDocumentosRAG() {
  DOCUMENTOS_RAG = [];
  
  // Cargar documentos de cada carpeta (jerarquía: 002 → 001 → 003 → 004)
  const carpetas = ['002', '001', '003', '004'];
  
  for (const carpeta of carpetas) {
    const carpetaPath = path.join(__dirname, '..', 'documents', carpeta);
    
    if (fs.existsSync(carpetaPath)) {
      const archivos = fs.readdirSync(carpetaPath).filter(f => f.endsWith('.jsonl'));
      
      for (const archivo of archivos) {
        const filePath = path.join(carpetaPath, archivo);
        try {
          const contenido = fs.readFileSync(filePath, 'utf8');
          const lineas = contenido.split('\n').filter(line => line.trim() !== '');
          
          for (const linea of lineas) {
            try {
              const documento = JSON.parse(linea);
              documento.carpeta = carpeta; // Agregar carpeta de origen
              DOCUMENTOS_RAG.push(documento);
            } catch (e) {
              console.error(`Error parseando línea en ${archivo}:`, e.message);
            }
          }
        } catch (e) {
          console.error(`Error leyendo ${filePath}:`, e.message);
        }
      }
    }
  }
  
  console.log(`✅ Documentos RAG cargados: ${DOCUMENTOS_RAG.length} registros`);
}

// Cargar documentos al iniciar
cargarDocumentosRAG();

// FUNCIONES DE BÚSQUEDA RAG REAL
function buscarAtribucionExplicita(query) {
  const queryLower = query.toLowerCase();
  const atribuciones = [];
  
  // Buscar en documentos con tipo "atribucion_explicita" o "marco_legal"
  for (const doc of DOCUMENTOS_RAG) {
    if (doc.tipo && (doc.tipo === 'atribucion_explicita' || doc.tipo === 'marco_legal')) {
      const textoLower = doc.text.toLowerCase();
      
      // Buscar frases clave de atribución
      const frasesAtribucion = [
        'facultad de la dirección de inspección y vigilancia',
        'corresponde a la dirección de inspección y vigilancia',
        'competencia de la dirección de inspección y vigilancia',
        'atribuciones de la dirección de inspección y vigilancia',
        'es facultad de la dirección de inspección y vigilancia'
      ];
      
      for (const frase of frasesAtribucion) {
        if (textoLower.includes(frase)) {
          // Verificar si la consulta está relacionada con las keywords del documento
          let relevancia = 0;
          if (doc.keywords) {
            for (const keyword of doc.keywords) {
              if (queryLower.includes(keyword.toLowerCase())) {
                relevancia++;
              }
            }
          }
          
          atribuciones.push({
            texto: doc.text,
            fuente: doc.source || 'Documento oficial',
            articulo: doc.articulo || 'No especificado',
            tipo: doc.tipo,
            carpeta: doc.carpeta,
            relevancia: relevancia,
            keywords: doc.keywords || []
          });
          break; // No duplicar el mismo documento
        }
      }
    }
  }
  
  // Ordenar por relevancia (más keywords coincidentes primero)
  atribuciones.sort((a, b) => b.relevancia - a.relevancia);
  
  return atribuciones;
}

function obtenerContactosRelevantes(query, atribucionesEncontradas) {
  const queryLower = query.toLowerCase();
  const contactos = [];
  
  // Buscar contactos en documentos con tipo "contacto_principal", "mediacion", etc.
  for (const doc of DOCUMENTOS_RAG) {
    if (doc.tipo && (doc.tipo === 'contacto_principal' || doc.tipo === 'mediacion' || 
                     doc.tipo === 'construccion' || doc.tipo === 'comercio' || 
                     doc.tipo === 'proteccion_civil')) {
      
      // Determinar relevancia basada en la consulta
      let relevancia = 0;
      
      // Ruido vecinal → Centros de Mediación
      if (queryLower.includes('ruido') && queryLower.includes('vecino')) {
        if (doc.tipo === 'mediacion') {
          relevancia = 10; // Alta prioridad
        }
      }
      
      // Ruido comercial → Inspección y Vigilancia
      if (queryLower.includes('ruido') && (queryLower.includes('comercial') || 
          queryLower.includes('negocio') || queryLower.includes('bar') || 
          queryLower.includes('restaurante'))) {
        if (doc.tipo === 'contacto_principal') {
          relevancia = 10;
        }
      }
      
      // Construcción → Subdirección de Construcción
      if (queryLower.includes('construcción') || queryLower.includes('obra') || 
          queryLower.includes('permiso') || queryLower.includes('licencia')) {
        if (doc.tipo === 'construccion') {
          relevancia = 10;
        }
      }
      
      // Comercio → Subdirección de Comercio
      if (queryLower.includes('comercio') || queryLower.includes('negocio') || 
          queryLower.includes('establecimiento')) {
        if (doc.tipo === 'comercio') {
          relevancia = 10;
        }
      }
      
      // Protección Civil → Subdirección correspondiente
      if (queryLower.includes('protección civil') || queryLower.includes('seguridad') || 
          queryLower.includes('emergencia')) {
        if (doc.tipo === 'proteccion_civil') {
          relevancia = 10;
        }
      }
      
      // Si hay atribuciones encontradas, incluir contacto principal
      if (atribucionesEncontradas.length > 0 && doc.tipo === 'contacto_principal') {
        relevancia = Math.max(relevancia, 5);
      }
      
      if (relevancia > 0) {
        contactos.push({
          dependencia: doc.dependencia || 'Dependencia municipal',
          telefono: doc.telefono || 'No disponible',
          extension: doc.extension || doc.extensiones ? doc.extensiones[0] : '',
          horario: doc.horario || 'Lunes a Viernes 8:00-15:00',
          responsable: doc.responsable || 'No especificado',
          tipo: doc.tipo,
          relevancia: relevancia
        });
      }
    }
  }
  
  // Ordenar por relevancia
  contactos.sort((a, b) => b.relevancia - a.relevancia);
  
  // Eliminar duplicados (misma dependencia)
  const contactosUnicos = [];
  const dependenciasVistas = new Set();
  
  for (const contacto of contactos) {
    if (!dependenciasVistas.has(contacto.dependencia)) {
      dependenciasVistas.add(contacto.dependencia);
      contactosUnicos.push(contacto);
    }
  }
  
  return contactosUnicos.slice(0, 3); // Máximo 3 contactos
}

// FUNCIÓN PRINCIPAL DE GENERACIÓN DE RESPUESTA (MANTIENE LÓGICA ORIGINAL)
function generarRespuesta(query, atribuciones) {
  const queryLower = query.toLowerCase();
  
  // CASO 1: Sin atribución explícita encontrada
  if (atribuciones.length === 0) {
    // Distinción crítica: ruido vecinos vs ruido comercial
    if (queryLower.includes('ruido')) {
      if (queryLower.includes('vecino') || queryLower.includes('vecinos') || 
          queryLower.includes('residencial') || queryLower.includes('casa')) {
        return "Para conflictos por ruido entre vecinos (particulares), la competencia corresponde a los **Centros Públicos de Mediación**, no a la Dirección de Inspección y Vigilancia. Los Centros de Mediación ayudan a resolver conflictos vecinales de manera pacífica y voluntaria.";
      } else if (queryLower.includes('comercial') || queryLower.includes('negocio') || 
                 queryLower.includes('bar') || queryLower.includes('restaurante') || 
                 queryLower.includes('local')) {
        return "Para ruido proveniente de establecimientos comerciales, bares, restaurantes o negocios, **sí corresponde a la Dirección de Inspección y Vigilancia**. Sin embargo, no encontré una atribución explícita en los documentos oficiales que asigne esta facultad específicamente.";
      }
    }
    
    // Respuesta genérica para otros casos sin atribución
    return "No encontré una atribución explícita en los documentos oficiales que asigne esta facultad específicamente a la Dirección de Inspección y Vigilancia. Es posible que corresponda a otra dependencia o que la atribución no esté documentada explícitamente.";
  }
  
  // CASO 2: Con atribución explícita encontrada
  const mejorAtribucion = atribuciones[0]; // La más relevante
  
  // Obtener contactos relevantes (solo si hay atribución)
  const contactos = obtenerContactosRelevantes(query, atribuciones);
  
  // Construir respuesta
  let respuesta = `✅ **Encontré atribución explícita:**\n\n`;
  respuesta += `**${mejorAtribucion.fuente}** - ${mejorAtribucion.articulo}\n`;
  respuesta += `"${mejorAtribucion.texto}"\n\n`;
  
  // Agregar contactos si existen
  if (contactos.length > 0) {
    respuesta += `**📞 Contactos relevantes:**\n`;
    for (const contacto of contactos) {
      respuesta += `• **${contacto.dependencia}**: ${contacto.telefono}`;
      if (contacto.extension) respuesta += ` ext. ${contacto.extension}`;
      if (contacto.responsable) respuesta += ` (${contacto.responsable})`;
      respuesta += ` - ${contacto.horario}\n`;
    }
  } else {
    respuesta += `**📞 Contacto general:**\n`;
    respuesta += `• **Dirección de Inspección y Vigilancia**: 3338182200 - Lunes a Viernes 8:00-15:00\n`;
  }
  
  return respuesta;
}

// SERVER HTTP
const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;
  
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  // Health check
  if (path === '/health' || path === '/api/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'ok',
      service: 'Chatbot Zapopan - Sistema RAG REAL',
      version: '4.0',
      criteria: 'explicit_attribution_required',
      rag_enabled: true,
      documentos_cargados: DOCUMENTOS_RAG.length,
      timestamp: new Date().toISOString()
    }));
    return;
  }
  
  // RAG Status
  if (path === '/api/rag/status') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      rag_enabled: true,
      documentos_totales: DOCUMENTOS_RAG.length,
      carpetas_cargadas: ['002', '001', '003', '004'],
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
        const atribuciones = buscarAtribucionExplicita(query);
        const response = generarRespuesta(query, atribuciones);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: true,
          query: query,
          response: response,
          has_explicit_attribution: atribuciones.length > 0,
          attribution_count: atribuciones.length,
          attribution_details: atribuciones.length > 0 ? atribuciones[0] : null,
          rag_system: true,
          timestamp: new Date().toISOString()
        }));
        
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          success: false, 
          error: 'Error procesando solicitud',
          details: error.message 
        }));
      }
    });
    
    return;
  }
  
  // Default 404
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ success: false, error: 'Endpoint no encontrado' }));
});

server.listen(PORT, () => {
  console.log(`🚀 Servidor RAG REAL ejecutándose en puerto ${PORT}`);
  console.log(`📚 Documentos cargados: ${DOCUMENTOS_RAG.length}`);
  console.log(`🏰 Sistema: Chatbot Zapopan con RAG real`);
});

module.exports = server;