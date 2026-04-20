const http = require('http');
const url = require('url');
const path = require('path');
const fs = require('fs');

// CONFIGURACIÓN
const PORT = process.env.PORT || 3000;
const TOKEN = 'vercel_public_access';

// CARGAR FUNCIONES RAG REAL
const { buscarAtribucionesEnDocumentos, obtenerContactosRelevantes } = require('./rag_functions');

// FUNCIONES AUXILIARES
function normalizarTexto(texto) {
    return texto.toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-z0-9\s]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

function contienePalabra(texto, palabra) {
    const regex = new RegExp(`\\b${palabra}\\b`, 'i');
    return regex.test(texto);
}

function determinarCategoriaConsulta(consulta) {
    const consultaLower = consulta.toLowerCase();
    
    // Distinción CRÍTICA: ruido vecinos vs ruido comercial
    if (contienePalabra(consultaLower, 'ruido') || contienePalabra(consultaLower, 'ruidoso')) {
        if (contienePalabra(consultaLower, 'vecino') || contienePalabra(consultaLower, 'vecinos') || 
            contienePalabra(consultaLower, 'fiesta') || contienePalabra(consultaLower, 'música') ||
            contienePalabra(consultaLower, 'perro') || contienePalabra(consultaLower, 'mascota')) {
            return 'ruido_vecinos';
        } else if (contienePalabra(consultaLower, 'bar') || contienePalabra(consultaLower, 'antro') ||
                  contienePalabra(consultaLower, 'restaurante') || contienePalabra(consultaLower, 'comercio') ||
                  contienePalabra(consultaLower, 'negocio') || contienePalabra(consultaLower, 'establecimiento')) {
            return 'ruido_comercial';
        }
    }
    
    if (contienePalabra(consultaLower, 'construcción') || contienePalabra(consultaLower, 'obra') || 
        contienePalabra(consultaLower, 'edificio') || contienePalabra(consultaLower, 'permiso') ||
        contienePalabra(consultaLower, 'licencia') || contienePalabra(consultaLower, 'demolición')) {
        return 'construccion';
    }
    
    if (contienePalabra(consultaLower, 'comercio') || contienePalabra(consultaLower, 'venta') ||
        contienePalabra(consultaLower, 'mercado') || contienePalabra(consultaLower, 'tienda') ||
        contienePalabra(consultaLower, 'puesto') || contienePalabra(consultaLower, 'vía pública')) {
        return 'comercio';
    }
    
    if (contienePalabra(consultaLower, 'protección civil') || contienePalabra(consultaLower, 'seguridad') ||
        contienePalabra(consultaLower, 'incendio') || contienePalabra(consultaLower, 'emergencia') ||
        contienePalabra(consultaLower, 'riesgo')) {
        return 'proteccion_civil';
    }
    
    if (contienePalabra(consultaLower, 'mediación') || contienePalabra(consultaLower, 'conflicto') ||
        contienePalabra(consultaLower, 'disputa') || contienePalabra(consultaLower, 'problema') ||
        contienePalabra(consultaLower, 'pelea')) {
        return 'mediacion';
    }
    
    return 'general';
}

function generarRespuesta(consulta) {
    const categoria = determinarCategoriaConsulta(consulta);
    const consultaNormalizada = normalizarTexto(consulta);
    
    // CASO 1: Ruido entre vecinos → Centros Públicos de Mediación
    if (categoria === 'ruido_vecinos') {
        const contactosMediacion = obtenerContactosRelevantes('mediacion');
        return {
            respuesta: `Para conflictos por ruido entre vecinos (fiestas, música, mascotas), te recomendamos acudir a los **Centros Públicos de Mediación**. Este tipo de conflictos entre particulares no es competencia de la Dirección de Inspección y Vigilancia.`,
            atribuciones: [],
            contactos: contactosMediacion,
            categoria: categoria,
            fuente: 'Sistema de clasificación automática'
        };
    }
    
    // BUSCAR ATRIBUCIONES REALES EN DOCUMENTOS
    const atribucionesEncontradas = buscarAtribucionesEnDocumentos(consultaNormalizada);
    
    // CASO 2: Sin atribuciones encontradas
    if (atribucionesEncontradas.length === 0) {
        return {
            respuesta: `No se encontraron atribuciones explícitas en los documentos oficiales para tu consulta sobre "${consulta}". Te recomendamos contactar directamente a la Dirección de Inspección y Vigilancia para verificar si tu caso aplica.`,
            atribuciones: [],
            contactos: [],
            categoria: categoria,
            fuente: 'Búsqueda en documentos oficiales'
        };
    }
    
    // CASO 3: Con atribuciones encontradas
    const mejorAtribucion = atribucionesEncontradas[0];
    const contactosRelevantes = obtenerContactosRelevantes(categoria);
    
    let respuesta = `Según **${mejorAtribucion.source}** (${mejorAtribucion.articulo}):\n\n`;
    respuesta += `"${mejorAtribucion.text}"\n\n`;
    
    if (contactosRelevantes.length > 0) {
        respuesta += `**Contactos relevantes:**\n`;
        contactosRelevantes.forEach(contacto => {
            respuesta += `• ${contacto.dependencia}: ${contacto.telefono}`;
            if (contacto.extension) respuesta += ` ext. ${contacto.extension}`;
            if (contacto.horario) respuesta += ` (${contacto.horario})`;
            respuesta += `\n`;
        });
    }
    
    return {
        respuesta: respuesta,
        atribuciones: atribucionesEncontradas.slice(0, 3),
        contactos: contactosRelevantes,
        categoria: categoria,
        fuente: mejorAtribucion.source
    };
}

// SERVER HTTP SIMPLIFICADO Y CORREGIDO
const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    
    // CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }
    
    // ENDPOINTS CORREGIDOS
    if (pathname === '/health' || pathname === '/api/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
            status: 'ok', 
            service: 'Chatbot Zapopan RAG Real',
            version: '3.2-rag-real',
            timestamp: new Date().toISOString() 
        }));
        return;
    }
    
    if (pathname === '/api/login') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
            token: TOKEN, 
            expiresIn: 3600,
            success: true 
        }));
        return;
    }
    
    if (pathname === '/api/chat') {
        if (req.method !== 'POST') {
            res.writeHead(405, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'Método no permitido', success: false }));
            return;
        }
        
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            try {
                const data = JSON.parse(body);
                
                // Validación básica
                if (!data.message || typeof data.message !== 'string') {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Consulta inválida', success: false }));
                    return;
                }
                
                // Validar token (simple)
                if (data.token !== TOKEN) {
                    res.writeHead(401, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'Token inválido', success: false }));
                    return;
                }
                
                // Generar respuesta con RAG REAL
                const respuesta = generarRespuesta(data.message);
                
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: true,
                    response: respuesta.respuesta,
                    atribuciones: respuesta.atribuciones,
                    contactos: respuesta.contactos,
                    categoria: respuesta.categoria,
                    fuente: respuesta.fuente,
                    timestamp: new Date().toISOString()
                }));
                
            } catch (error) {
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ 
                    error: 'Error procesando consulta', 
                    details: error.message,
                    success: false 
                }));
            }
        });
        return;
    }
    
    // Ruta por defecto
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ 
        message: 'API Chatbot Inspección Zapopan - RAG Real',
        version: '3.2-rag-real',
        endpoints: ['/health', '/api/login', '/api/chat'],
        status: 'operational',
        success: true
    }));
});

// Iniciar servidor
server.listen(PORT, () => {
    console.log(`🚀 Servidor RAG Real escuchando en puerto ${PORT}`);
    console.log(`📁 Documentos cargados: 4 carpetas con documentos JSONL`);
    console.log(`🏰 Sistema: Búsqueda real en documentos oficiales`);
});

module.exports = server;
