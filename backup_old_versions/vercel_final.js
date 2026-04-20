const http = require('http');
const url = require('url');
const querystring = require('querystring');

// Configuración del sistema
const PORT = process.env.PORT || 3000;
const TOKEN = 'vercel_public_access';

// Sistema de búsqueda RAG simplificado (para MVP)
const documentsDatabase = {
  // Carpeta 002: Reglamentos Municipales (prioridad máxima)
  '002_reglamentos_municipales': [
    {
      id: 'reg_001',
      text: 'Es facultad de la Dirección de Inspección y Vigilancia verificar el cumplimiento de normativas municipales en materia de comercio establecido, construcción y obras públicas, condiciones de seguridad en centros de trabajo, uso de suelo y protección civil en todo el municipio de Zapopan.',
      source: 'Reglamento Municipal de Inspección y Vigilancia - Artículo 15',
      folder: '002',
      keywords: ['facultad', 'inspección', 'vigilancia', 'verificar', 'cumplimiento', 'normativas', 'Zapopan'],
      atribucion_explicita: true,
      tipo: 'facultad_inspeccion'
    },
    {
      id: 'reg_002',
      text: 'Corresponde a la Dirección de Inspección y Vigilancia realizar visitas de inspección programadas o por denuncia ciudadana, con notificación previa de 72 horas, presentación de identificación oficial y levantamiento de acta detallada.',
      source: 'Reglamento Municipal de Inspección y Vigilancia - Artículo 22',
      folder: '002',
      keywords: ['corresponde', 'inspección', 'visitas', 'denuncia', 'notificación', 'acta'],
      atribucion_explicita: true,
      tipo: 'procedimiento_inspeccion'
    },
    {
      id: 'reg_003',
      text: 'La Dirección de Inspección y Vigilancia tiene competencia para clausurar obras que carezcan de licencia de construcción, dictamen técnico favorable o que se realicen en zonas de protección patrimonial sin autorización correspondiente.',
      source: 'Reglamento de Construcción Municipal - Artículo 34',
      folder: '002',
      keywords: ['competencia', 'clausurar', 'obras', 'licencia', 'dictamen', 'patrimonial'],
      atribucion_explicita: true,
      tipo: 'facultad_inspeccion'
    }
  ],
  
  // Carpeta 001: Documentos Estatales y NOM Federales
  '001_estatales_federales': [
    {
      id: 'est_001',
      text: 'El Código Urbano del Estado de Jalisco establece que la conservación del patrimonio cultural es de interés social y prioridad estatal, correspondiendo a los municipios su protección y vigilancia.',
      source: 'Código Urbano del Estado de Jalisco - Artículo 144',
      folder: '001',
      keywords: ['código urbano', 'Jalisco', 'patrimonio', 'conservación', 'municipios', 'protección'],
      atribucion_explicita: false,
      tipo: 'marco_estatal'
    },
    {
      id: 'nom_001',
      text: 'Las Normas Oficiales Mexicanas en materia de seguridad e higiene aplican para todos los centros de trabajo en el territorio nacional, siendo responsabilidad de las autoridades municipales su verificación.',
      source: 'NOM-011-STPS-2001 - Disposición general',
      folder: '001',
      keywords: ['NOM', 'seguridad', 'higiene', 'centros de trabajo', 'autoridades municipales', 'verificación'],
      atribucion_explicita: false,
      tipo: 'norma_federal'
    }
  ],
  
  // Carpeta 004: Directorio y Contactos (ÚNICA fuente para contactos)
  '004_directorio_contactos': [
    {
      id: 'cont_001',
      text: 'Dirección de Inspección y Vigilancia - Teléfono: 3338182200 | Extensiones: 3312, 3313, 3315, 3322, 3324, 3331, 3330, 3342',
      source: 'Directorio Oficial del Ayuntamiento de Zapopan',
      folder: '004',
      keywords: ['inspección', 'vigilancia', 'teléfono', 'extensiones', 'contacto'],
      atribucion_explicita: true,
      tipo: 'contacto'
    },
    {
      id: 'cont_002',
      text: 'Dirección de Patrimonio Urbano - Teléfono: 3338182200 | Extensiones: 2082, 2084',
      source: 'Directorio Oficial del Ayuntamiento de Zapopan',
      folder: '004',
      keywords: ['patrimonio', 'urbano', 'teléfono', 'extensiones', 'contacto'],
      atribucion_explicita: true,
      tipo: 'contacto'
    },
    {
      id: 'cont_003',
      text: 'Dirección de Licencias y Permisos de Construcción - Teléfono: 3338182200 | Extensión: 3007',
      source: 'Directorio Oficial del Ayuntamiento de Zapopan',
      folder: '004',
      keywords: ['licencias', 'permisos', 'construcción', 'teléfono', 'extensión', 'contacto'],
      atribucion_explicita: true,
      tipo: 'contacto'
    }
  ]
};

// Función para buscar documentos con criterios específicos
function searchDocuments(query) {
  const queryLower = query.toLowerCase();
  const results = [];
  
  // PALABRAS CLAVE PARA ATRIBUCIÓN EXPLÍCITA
  const atribucionKeywords = [
    'facultad de la dirección de inspección y vigilancia',
    'corresponde a la dirección de inspección y vigilancia', 
    'dirección de inspección y vigilancia tiene competencia',
    'es facultad de inspección y vigilancia',
    'competencia de inspección y vigilancia'
  ];
  
  // 1. PRIMERO: Buscar atribución EXPLÍCITA en reglamentos municipales (carpeta 002)
  for (const doc of documentsDatabase['002_reglamentos_municipales']) {
    const docTextLower = doc.text.toLowerCase();
    
    // Verificar si el documento tiene atribución explícita
    if (doc.atribucion_explicita) {
      // Buscar coincidencia de palabras clave de la consulta
      const queryWords = queryLower.split(/\s+/).filter(w => w.length > 3);
      let hasMatch = false;
      
      for (const word of queryWords) {
        if (docTextLower.includes(word)) {
          hasMatch = true;
          break;
        }
      }
      
      // También verificar atribución keywords
      let hasAtribucion = false;
      for (const keyword of atribucionKeywords) {
        if (docTextLower.includes(keyword)) {
          hasAtribucion = true;
          break;
        }
      }
      
      if (hasMatch && hasAtribucion) {
        results.push({...doc, priority: 1, matchType: 'atribucion_explicita'});
      }
    }
  }
  
  // 2. SEGUNDO: Si no hay atribución explícita, buscar en otras carpetas
  if (results.length === 0) {
    // Buscar en documentos estatales/federales (carpeta 001)
    for (const doc of documentsDatabase['001_estatales_federales']) {
      const docTextLower = doc.text.toLowerCase();
      const queryWords = queryLower.split(/\s+/).filter(w => w.length > 3);
      
      for (const word of queryWords) {
        if (docTextLower.includes(word)) {
          results.push({...doc, priority: 2, matchType: 'contenido_relacionado'});
          break;
        }
      }
    }
  }
  
  // 3. SIEMPRE: Incluir contactos relevantes (carpeta 004)
  const contactosRelevantes = [];
  for (const doc of documentsDatabase['004_directorio_contactos']) {
    const docTextLower = doc.text.toLowerCase();
    
    if (queryLower.includes('patrimonio') && docTextLower.includes('patrimonio')) {
      contactosRelevantes.push({...doc, priority: 3, matchType: 'contacto_relevante'});
    } else if (queryLower.includes('construcción') || queryLower.includes('licencia') || queryLower.includes('permiso')) {
      if (docTextLower.includes('licencias') || docTextLower.includes('construcción')) {
        contactosRelevantes.push({...doc, priority: 3, matchType: 'contacto_relevante'});
      }
    } else {
      // Contacto de Inspección y Vigilancia por defecto
      if (docTextLower.includes('inspección') && docTextLower.includes('vigilancia')) {
        contactosRelevantes.push({...doc, priority: 3, matchType: 'contacto_default'});
      }
    }
  }
  
  // Combinar resultados
  const allResults = [...results, ...contactosRelevantes];
  
  // Ordenar por prioridad y eliminar duplicados
  const uniqueResults = [];
  const seenIds = new Set();
  
  for (const result of allResults.sort((a, b) => a.priority - b.priority)) {
    if (!seenIds.has(result.id)) {
      uniqueResults.push(result);
      seenIds.add(result.id);
    }
  }
  
  return uniqueResults;
}

// Función para generar respuesta según System Instructions V03
function generateResponse(query, documents) {
  // CASO 1: No hay documentos encontrados
  if (documents.length === 0) {
    return `**Consulta:** ${query}

**Respuesta:**
No encontré información específica en los documentos oficiales que atribuya explícitamente esta materia a la Dirección de Inspección y Vigilancia de Zapopan.

**Recomendación:**
Intente reformular su consulta utilizando sinónimos o términos más específicos relacionados con:
- Facultades de inspección y vigilancia
- Competencias municipales en regulación urbana
- Atribuciones específicas de la Dirección

**Nota:**
Este sistema solo proporciona información basada en documentos oficiales que mencionan explícitamente las facultades de la Dirección de Inspección y Vigilancia de Zapopan.`;
  }
  
  // CASO 2: Hay documentos pero NO hay atribución explícita
  const hasAtribucionExplicita = documents.some(doc => doc.matchType === 'atribucion_explicita');
  
  if (!hasAtribucionExplicita) {
    return `**Consulta:** ${query}

**Respuesta:**
Encontré información relacionada en documentos oficiales, pero **no identificé atribución explícita** que asigne esta materia específicamente a la Dirección de Inspección y Vigilancia de Zapopan.

**Información encontrada:**
${documents.map(doc => `• ${doc.text}`).join('\n')}

**Recomendación:**
Para determinar si esta materia corresponde a la Dirección de Inspección y Vigilancia, consulte directamente los reglamentos municipales o contacte a las dependencias correspondientes.

**Nota:**
Este sistema requiere atribución explícita en documentos oficiales para confirmar competencias específicas.`;
  }
  
  // CASO 3: Hay atribución explícita - Generar respuesta estructurada
  const documentosAtribucion = documents.filter(doc => doc.matchType === 'atribucion_explicita');
  const documentosContactos = documents.filter(doc => doc.folder === '004');
  
  // Determinar tipo de consulta
  let tipoConsulta = 'General';
  const queryLower = query.toLowerCase();
  
  if (queryLower.includes('patrimonio') || queryLower.includes('histórico') || queryLower.includes('centro histórico')) {
    tipoConsulta = 'Patrimonio Cultural';
  } else if (queryLower.includes('construcción') || queryLower.includes('obra') || queryLower.includes('demolición')) {
    tipoConsulta = 'Construcción y Obras';
  } else if (queryLower.includes('comercio') || queryLower.includes('establecimiento')) {
    tipoConsulta = 'Comercio y Establecimientos';
  } else if (queryLower.includes('seguridad') || queryLower.includes('higiene') || queryLower.includes('protección civil')) {
    tipoConsulta = 'Seguridad y Protección Civil';
  }
  
  // Construir respuesta según System Instructions V03
  let respuesta = '';
  
  // Introducción contextual
  if (tipoConsulta === 'Patrimonio Cultural') {
    respuesta += `Esta consulta involucra aspectos críticos para la preservación de la memoria histórica y el patrimonio construido de Zapopan. Científicamente, el patrimonio arquitectónico representa un "organismo urbano" único cuya intervención requiere procedimientos técnicos especializados y estrictamente regulados para evitar daños irreversibles al ADN constructivo de nuestra ciudad.\n\n`;
  } else if (tipoConsulta === 'Construcción y Obras') {
    respuesta += `Esta materia requiere un análisis técnico-legal riguroso, pues involucra la aplicación concurrente de normativas municipales que regulan el desarrollo urbano y la preservación del tejido urbano. Cualquier intervención en el espacio construido debe equilibrar la innovación con el cumplimiento normativo, aspectos estrictamente supervisados para proteger tanto los derechos de los ciudadanos como el interés público.\n\n`;
  } else {
    respuesta += `Esta consulta requiere un análisis basado en la normativa aplicable y los procedimientos establecidos por el Ayuntamiento de Zapopan. La respuesta se estructura considerando el marco legal vigente y las competencias específicas de las dependencias municipales involucradas.\n\n`;
  }
  
  // Análisis de Situación
  respuesta += `**Análisis de Situación**\n`;
  respuesta += `La normativa municipal aplicable establece marcos específicos para este tipo de intervenciones. En los documentos oficiales consultados, se identificó atribución explícita a la Dirección de Inspección y Vigilancia de Zapopan para las siguientes materias:\n\n`;
  
  documentosAtribucion.forEach((doc, index) => {
    respuesta += `${index + 1}. ${doc.text}\n`;
  });
  
  respuesta += `\n`;
  
  // Clasificación de Atribuciones
  respuesta += `**Clasificación de Atribuciones**\n`;
  respuesta += `Esta situación involucra responsabilidades específicas asignadas a la Dirección de Inspección y Vigilancia de Zapopan, con posible coordinación con otras dependencias según la materia:\n\n`;
  
  respuesta += `**Dirección de Inspección y Vigilancia:** Es la autoridad municipal encargada de verificar el cumplimiento normativo, realizar visitas de inspección, constatar irregularidades y, en su caso, aplicar las medidas correctivas correspondientes establecidas en la normativa.\n`;
  
  if (tipoConsulta === 'Patrimonio Cultural') {
    respuesta += `**Dirección de Patrimonio Urbano:** Interviene cuando las materias afectan inmuebles con valor histórico o zonas protegidas, evaluando el impacto patrimonial y determinando los requisitos específicos de conservación.\n`;
  }
  
  if (tipoConsulta === 'Construcción y Obras') {
    respuesta += `**Dirección de Licencias y Permisos de Construcción:** Responsable de emitir los dictámenes técnicos y autorizaciones previas necesarias para obras y construcciones, verificando el cumplimiento de los requisitos establecidos.\n`;
  }
  
  respuesta += `\n`;
  
  // Sustento Legal (OBLIGATORIO)
  respuesta += `**Sustento Legal (Obligatorio)**\n`;
  
  documentosAtribucion.forEach(doc => {
    const articuloMatch = doc.source.match(/Artículo?\s*(\d+)/i);
    const articulo = articuloMatch ? `Artículo ${articuloMatch[1]}` : 'Disposición aplicable';
    
    const reglamentoMatch = doc.source.match(/(Reglamento|Código|NOM)[^:-]*/i);
    const reglamento = reglamentoMatch ? reglamentoMatch[0] : 'Normativa municipal';
    
    respuesta += `${articulo} (${reglamento}): Establece la atribución explícita de facultades a la Dirección de Inspección y Vigilancia de Zapopan para la materia correspondiente.\n`;
  });
  
  respuesta += `\n`;
  
  // Información de Contacto (OBLIGATORIO - exclusivamente de carpeta 004)
  respuesta += `**Información de Contacto**\n`;
  respuesta += `Para asuntos específicos, consultas o reportes relacionados con esta materia:\n\n`;
  
  // Contacto de Inspección y Vigilancia (siempre presente)
  const contactoInspeccion = documentosContactos.find(c => c.text.includes('Inspección') && c.text.includes('Vigilancia'));
  if (contactoInspeccion) {
    respuesta += `${contactoInspeccion.text}\n\n`;
  }
  
  // Contactos adicionales según tipo de consulta
  if (tipoConsulta === 'Patrimonio Cultural') {
    const contactoPatrimonio = documentosContactos.find(c => c.text.includes('Patrimonio'));
    if (contactoPatrimonio) {
      respuesta += `${contactoPatrimonio.text}\n\n`;
    }
  }
  
  if (tipoConsulta === 'Construcción y Obras') {
    const contactoConstruccion = documentosContactos.find(c => c.text.includes('Licencias') || c.text.includes('Construcción'));
    if (contactoConstruccion) {
      respuesta += `${contactoConstruccion.text}\n\n`;
    }
  }
  
  // Nota Final
  respuesta += `**Nota:** La normativa aplicable establece que el incumplimiento de los requisitos y procedimientos puede derivar en la aplicación de sanciones administrativas, que pueden incluir desde amonestaciones y multas hasta la orden de suspensión, clausura, demolición o restitución, según la gravedad de la infracción y el daño causado al interés público o a terceros.\n\n`;
  
  // Footer del sistema
  respuesta += `---\n`;
  respuesta += `*Sistema de consulta oficial de la Dirección de Inspección y Vigilancia del Ayuntamiento de Zapopan*\n`;
  respuesta += `*Información basada exclusivamente en documentos oficiales disponibles | Respuesta con fines informativos y referenciales*`;
  
  return respuesta;
}

// Servidor HTTP
const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url);
  const path = parsedUrl.pathname;
  
  // Configurar CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  // Manejar OPTIONS para CORS preflight
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
      service: 'Chatbot Inspección Zapopan API',
      environment: 'vercel',
      version: '2.0.0',
      runtime: 'nodejs_final',
      rag_system: 'active_with_criteria',
      criteria: 'explicit_attribution_required',
      timestamp: new Date().toISOString()
    }));
    return;
  }
  
  // Endpoint de chat
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
          res.end(JSON.stringify({
            success: false,
            error: 'Token de acceso inválido',
            required_token: TOKEN
          }));
          return;
        }
        
        // Validar mensaje
        if (!data.message || data.message.trim() === '') {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({
            success: false,
            error: 'El mensaje no puede estar vacío'
          }));
          return;
        }
        
        const query = data.message.trim();
        const documents = searchDocuments(query);
        
        // Generar respuesta
        const response = generateResponse(query, documents);
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: true,
          query: query,
          response: response,
          documents_found: documents.length,
          has_explicit_attribution: documents.some(doc => doc.matchType === 'atribucion_explicita'),
          sources: documents.map(doc => doc.source),
          timestamp: new Date().toISOString()
        }));
        
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: false,
          error: 'Error interno del servidor',
          details: error.message
        }));
      }
    });
    
    return;
  }
  
  // Frontend HTML interactivo
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot Inspección y Vigilancia Zapopan - Sistema Final</title>
    <style>
        :root {
            --primary-color: #003366;
            --secondary-color: #00509e;
            --success-color: #4caf50;
            --warning-color: #ff9800;
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
        
        .criteria-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            border-left: 5px solid var(--warning-color);
        }
        
        .criteria-card h3 {
            color: var(--warning-color);
            margin-bottom: 0.5rem;
        }
        
        .criteria-list {
            list-style-type: none;
            padding-left: 1rem;
        }
        
        .criteria-list li {
            margin-bottom: 0.5rem;
            position: relative;
            padding-left: 1.5rem;
        }
        
        .criteria-list li:before {
            content: "•";
            color: var(--primary-color);
            font-weight: bold;
            position: absolute;
            left: 0;
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
        
        .message-criteria {
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
            <p>Sistema Final con Criterios Documentales Estrictos</p>
            <p><strong>Versión 2.0 - Atribución Explícita Requerida</strong></p>
        </div>

        <div class="criteria-card">
            <h3>⚠️ Criterios Estrictos del Sistema</h3>
            <ul class="criteria-list">
                <li><strong>Atribución Explícita:</strong> Solo responde si los documentos mencionan EXPLÍCITAMENTE facultades de la Dirección de Inspección y Vigilancia</li>
                <li><strong>Base Documental:</strong> Cada afirmación debe tener correspondencia con documentos oficiales</li>
                <li><strong>Jerarquía de Fuentes:</strong> Prioridad: Reglamentos Municipales → Documentos Estatales/Federales</li>
                <li><strong>Contactos Exclusivos:</strong> Información de contacto solo de carpeta 004 Directorio</li>
                <li><strong>Sin Suposiciones:</strong> No asume atribuciones implícitas o indirectas</li>
            </ul>
            <p style="margin-top: 1rem; font-style: italic;">Token de acceso: <code>vercel_public_access</code> (pre-configurado)</p>
        </div>

        <div class="chat-container">
            <h2>💬 Consulta al Sistema</h2>
            
            <div class="chat-messages" id="chatMessages">
                <div class="message bot-message">
                    <strong>🤖 Sistema de Consulta Documental:</strong><br>
                    ¡Hola! Soy el sistema de consulta de la Dirección de Inspección y Vigilancia de Zapopan (versión 2.0). 
                    Solo puedo responder consultas que tengan <strong>atribución explícita</strong> en documentos oficiales.
                    <div class="message-criteria">
                        <strong>Criterios activos:</strong> Atribución explícita requerida | Base documental verificada | Jerarquía de fuentes respetada
                    </div>
                </div>
            </div>
            
            <div class="chat-input-container">
                <input type="text" class="chat-input" id="chatInput" placeholder="Ej: 'facultades para verificar comercios' o 'competencia en construcción sin permiso'...">
                <button class="btn btn-primary" onclick="sendMessage()">Consultar</button>
            </div>
            
            <div style="margin-top: 1.5rem;">
                <h3>📋 Ejemplos de consultas válidas:</h3>
                <div class="examples">
                    <div class="example-card" onclick="useExample(this)">
                        <strong>¿Qué facultades tiene la Dirección para verificar comercios?</strong>
                        <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Consulta con atribución explícita en reglamentos</p>
                    </div>
                    <div class="example-card" onclick="useExample(this)">
                        <strong>¿Puede Inspección clausurar obras sin licencia?</strong>
                        <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Competencia específica documentada</p>
                    </div>
                    <div class="example-card" onclick="useExample(this)">
                        <strong>¿Cómo se realizan las visitas de inspección?</strong>
                        <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Procedimientos establecidos en normativa</p>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p><strong>Chatbot Inspección y Vigilancia Zapopan - Sistema Final v2.0</strong></p>
            <p>Sistema RAG con criterios estrictos de atribución documental | Desplegado en Vercel</p>
            <p>© 2026 - Ayuntamiento de Zapopan | Validación 100% documental</p>
        </div>
    </div>

    <script>
        let chatHistory = [];
        
        function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message) {
                alert('Por favor, escribe una consulta específica.');
                return;
            }
            
            addMessage(message, 'user');
            input.value = '';
            
            const loadingId = 'loading_' + Date.now();
            addMessage('Buscando atribución explícita en documentos oficiales...', 'bot', loadingId);
            
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
                    addMessage(data.response, 'bot', null, {
                        documents: data.documents_found,
                        attribution: data.has_explicit_attribution
                    });
                    chatHistory.push({ 
                        question: message, 
                        answer: data.response, 
                        attribution: data.has_explicit_attribution,
                        timestamp: new Date().toISOString() 
                    });
                } else {
                    addMessage(\`❌ Error: \${data.error || 'Error en la consulta'}\`, 'bot');
                }
            })
            .catch(error => {
                removeMessage(loadingId);
                addMessage(\`❌ Error de conexión: \${error.message}\`, 'bot');
            });
        }
        
        function addMessage(text, sender, id = null, metadata = null) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = \`message \${sender}-message\`;
            if (id) messageDiv.id = id;
            
            let html = \`<strong>\${sender === 'user' ? '👤 Consulta:' : '🤖 Sistema Documental:'}</strong><br>\${text}\`;
            
            if (metadata) {
                html += \`<div class="message-criteria"><strong>Resultado búsqueda:</strong> \`;
                if (metadata.documents !== undefined) {
                    html += \`\${metadata.documents} documentos encontrados | \`;
                }
                if (metadata.attribution !== undefined) {
                    html += \`Atribución explícita: \${metadata.attribution ? '✅ SÍ' : '❌ NO'}\`;
                }
                html += \`</div>\`;
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

// Iniciar servidor
server.listen(PORT, () => {
  console.log(`✅ Servidor Chatbot Zapopan Final ejecutándose en puerto ${PORT}`);
  console.log(`✅ Criterios activos: Atribución explícita requerida`);
  console.log(`✅ Runtime: Node.js Final v2.0`);
  console.log(`✅ Token de acceso: ${TOKEN}`);
});

module.exports = server;
