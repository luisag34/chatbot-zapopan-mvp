// FUNCIONES RAG REAL - Búsqueda en documentos JSONL (VERSIÓN MEJORADA)
const fs = require('fs');
const path = require('path');

// Cargar todos los documentos JSONL de una carpeta
function cargarDocumentosCarpeta(carpeta) {
    const documentos = [];
    try {
        const carpetaPath = path.join(__dirname, '..', 'documents', carpeta);
        if (!fs.existsSync(carpetaPath)) {
            console.warn(`Carpeta ${carpeta} no existe`);
            return documentos;
        }
        
        const archivos = fs.readdirSync(carpetaPath);
        for (const archivo of archivos) {
            if (archivo.endsWith('.jsonl')) {
                const filePath = path.join(carpetaPath, archivo);
                const contenido = fs.readFileSync(filePath, 'utf8');
                const lineas = contenido.split('\n').filter(line => line.trim());
                
                for (const linea of lineas) {
                    try {
                        const doc = JSON.parse(linea);
                        doc._archivo = archivo;
                        doc._carpeta = carpeta;
                        documentos.push(doc);
                    } catch (e) {
                        console.error(`Error parseando ${carpeta}/${archivo}:`, e.message, 'Línea:', linea.substring(0, 50));
                    }
                }
            }
        }
    } catch (e) {
        console.error(`Error cargando carpeta ${carpeta}:`, e.message);
    }
    return documentos;
}

// Buscar atribuciones explícitas en documentos (BÚSQUEDA MEJORADA)
function buscarAtribucionesEnDocumentos(query) {
    const queryLower = query.toLowerCase();
    const palabrasClave = queryLower.split(/\s+/).filter(p => p.length > 3);
    const resultados = [];
    
    // Jerarquía documental: 002 → 001 → 003
    const carpetas = ['002', '001', '003'];
    
    for (const carpeta of carpetas) {
        const documentos = cargarDocumentosCarpeta(carpeta);
        
        for (const doc of documentos) {
            if (!doc.text) continue;
            
            const textoLower = doc.text.toLowerCase();
            let coincidencias = 0;
            
            // Buscar palabras clave
            for (const palabra of palabrasClave) {
                if (textoLower.includes(palabra)) {
                    coincidencias++;
                }
            }
            
            // Buscar frases clave de atribución
            const frasesAtribucion = [
                'dirección de inspección y vigilancia',
                'facultad de',
                'competencia de', 
                'corresponde a',
                'atribuciones de'
            ];
            
            let tieneAtribucion = false;
            for (const frase of frasesAtribucion) {
                if (textoLower.includes(frase)) {
                    tieneAtribucion = true;
                    coincidencias += 2; // Bonus por atribución explícita
                    break;
                }
            }
            
            if (coincidencias > 0 || tieneAtribucion) {
                resultados.push({
                    ...doc,
                    carpeta: carpeta,
                    relevancia: calcularRelevancia(doc.text, queryLower, carpeta, coincidencias, tieneAtribucion)
                });
            }
        }
        
        // Si encontramos resultados con atribución explícita, priorizar
        const resultadosConAtribucion = resultados.filter(r => r.relevancia >= 8);
        if (resultadosConAtribucion.length > 0 && carpeta === '002') {
            break; // Prioridad máxima: reglamentos municipales con atribución
        }
    }
    
    // Ordenar por relevancia
    return resultados.sort((a, b) => b.relevancia - a.relevancia);
}

// Calcular relevancia mejorada
function calcularRelevancia(texto, query, carpeta, coincidencias, tieneAtribucion) {
    let score = 0;
    const textoLower = texto.toLowerCase();
    
    // Bonus por carpeta (jerarquía documental)
    const bonusCarpeta = { '002': 10, '001': 5, '003': 3 };
    score += bonusCarpeta[carpeta] || 0;
    
    // Bonus por atribución explícita
    if (tieneAtribucion) score += 8;
    
    // Bonus por coincidencias de palabras
    score += coincidencias * 2;
    
    // Bonus por artículo específico
    if (textoLower.includes('artículo')) score += 3;
    
    // Bonus por reglamento municipal
    if (textoLower.includes('reglamento municipal')) score += 4;
    
    return score;
}

// Obtener contactos relevantes (MANTENIDO)
function obtenerContactosRelevantes(categoria) {
    const contactos = cargarDocumentosCarpeta('004');
    const resultados = [];
    
    for (const contacto of contactos) {
        if (!contacto.dependencia) continue;
        
        const mapeoCategorias = {
            'construccion': ['construccion', 'contacto_principal'],
            'comercio': ['comercio', 'contacto_principal'],
            'ruido_comercial': ['comercio', 'contacto_principal'],
            'ruido_vecinos': ['mediacion'],
            'mediacion': ['mediacion'],
            'proteccion_civil': ['proteccion_civil', 'contacto_principal'],
            'general': ['contacto_principal']
        };
        
        const tiposBuscados = mapeoCategorias[categoria] || ['contacto_principal'];
        
        if (tiposBuscados.includes(contacto.tipo)) {
            resultados.push(contacto);
        }
    }
    
    return resultados;
}

module.exports = {
    buscarAtribucionesEnDocumentos,
    obtenerContactosRelevantes,
    cargarDocumentosCarpeta
};
