#!/usr/bin/env python3
"""
Sistema RAG MVP ultra-simple para Chatbot Inspección Zapopan
Sin dependencias externas - Solo JSONL processing
"""

import json
import os
import glob
import hashlib
from typing import List, Dict, Any

class UltraSimpleRAG:
    """Sistema RAG ultra-simple sin embeddings complejos"""
    
    def __init__(self, documents_path: str = "data/documents"):
        self.documents_path = documents_path
        self.documents = []
        self.index = {}  # Simple index por palabras clave
        
    def load_documents(self):
        """Carga documentos JSONL"""
        print(f"📚 Cargando documentos de {self.documents_path}...")
        
        jsonl_files = glob.glob(f"{self.documents_path}/**/*.jsonl", recursive=True)
        print(f"   📄 Encontrados {len(jsonl_files)} archivos JSONL")
        
        loaded_count = 0
        for jsonl_file in jsonl_files[:5]:  # Limitar para MVP
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        doc = json.loads(line.strip())
                        self.documents.append(doc)
                        loaded_count += 1
                        
                        # Indexar palabras clave simples
                        text = doc.get('text', doc.get('content', ''))
                        if text:
                            words = text.lower().split()[:20]  # Primeras 20 palabras
                            for word in words:
                                if len(word) > 3:  # Palabras de más de 3 letras
                                    if word not in self.index:
                                        self.index[word] = []
                                    self.index[word].append(len(self.documents) - 1)
            except Exception as e:
                print(f"   ⚠️  Error cargando {jsonl_file}: {e}")
        
        print(f"   ✅ Cargados {loaded_count} documentos")
        print(f"   🔍 Índice con {len(self.index)} palabras clave")
        return loaded_count
    
    def simple_search(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Búsqueda simple por palabras clave
        
        Args:
            query: Consulta del usuario
            max_results: Máximo de resultados
        
        Returns:
            Lista de documentos relevantes
        """
        query_words = query.lower().split()
        relevant_docs = {}
        
        # Buscar documentos que contengan palabras de la consulta
        for word in query_words:
            if word in self.index:
                for doc_idx in self.index[word]:
                    if doc_idx not in relevant_docs:
                        relevant_docs[doc_idx] = 0
                    relevant_docs[doc_idx] += 1
        
        # Ordenar por relevancia
        sorted_docs = sorted(relevant_docs.items(), key=lambda x: x[1], reverse=True)
        
        # Obtener documentos
        results = []
        for doc_idx, score in sorted_docs[:max_results]:
            if doc_idx < len(self.documents):
                doc = self.documents[doc_idx].copy()
                doc['relevance_score'] = score
                results.append(doc)
        
        return results
    
    def generate_response(self, query: str, context_docs: List[Dict]) -> str:
        """
        Genera respuesta basada en documentos
        
        Args:
            query: Pregunta del usuario
            context_docs: Documentos relevantes
        
        Returns:
            Respuesta generada
        """
        if not context_docs:
            return "No encontré información específica en los documentos sobre este tema. Por favor, consulta directamente los reglamentos o contacta a la Dirección de Inspección y Vigilancia."
        
        # Extraer información de documentos
        sources = []
        key_points = []
        
        for doc in context_docs[:2]:  # Usar máximo 2 documentos
            text = doc.get('text', '')[:300]  # Primeros 300 caracteres
            source = doc.get('source', doc.get('file', 'Documento oficial'))
            
            if text:
                key_points.append(f"- {text}...")
                sources.append(source)
        
        # Construir respuesta
        response = f"""**Consulta:** {query}

**Información encontrada en documentos oficiales:**

{chr(10).join(key_points)}

**Fuentes:** {', '.join(set(sources))}

**Nota:** Esta información está basada en documentos oficiales de la Dirección de Inspección y Vigilancia de Zapopan. Para consultas específicas o interpretación legal, contacta directamente con la dependencia."""
        
        return response
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Procesa una consulta completa
        
        Args:
            query: Pregunta del usuario
        
        Returns:
            Dict con respuesta y metadatos
        """
        print(f"\n❓ Consulta: {query}")
        
        # Buscar documentos relevantes
        relevant_docs = self.simple_search(query)
        print(f"   🔍 Encontrados {len(relevant_docs)} documentos relevantes")
        
        # Generar respuesta
        response = self.generate_response(query, relevant_docs)
        
        # Preparar resultado
        result = {
            'success': True,
            'query': query,
            'response': response,
            'documents_found': len(relevant_docs),
            'sources': list(set([doc.get('source', 'unknown') for doc in relevant_docs])),
            'system': 'UltraSimpleRAG MVP'
        }
        
        return result

def test_system():
    """Función de testing"""
    print("=" * 60)
    print("🏰 SISTEMA RAG MVP - CHATBOT INSPECCIÓN ZAPOPAN")
    print("=" * 60)
    
    # Inicializar sistema
    rag = UltraSimpleRAG()
    
    # Cargar documentos
    doc_count = rag.load_documents()
    
    if doc_count == 0:
        print("\n⚠️  No se pudieron cargar documentos. Usando modo de demostración.")
        
        # Modo demostración con datos dummy
        rag.documents = [
            {
                'text': 'La Dirección de Inspección y Vigilancia tiene facultades para verificar el cumplimiento de normativas municipales en materia de comercio, construcción y condiciones de seguridad.',
                'source': 'Reglamento Municipal de Inspección',
                'file': 'reglamento_inspeccion.jsonl'
            },
            {
                'text': 'Los comercios deben cumplir con las normas de seguridad e higiene establecidas en las NOM federales y reglamentos municipales.',
                'source': 'NOM-011-STPS-2001',
                'file': 'nom_seguridad.jsonl'
            }
        ]
        print("   🔧 Cargados 2 documentos de demostración")
    
    # Probar consultas
    test_queries = [
        "¿Cuáles son las facultades de la Dirección de Inspección y Vigilancia?",
        "¿Qué normativas aplican para comercios?",
        "¿Qué se requiere para una inspección?"
    ]
    
    for query in test_queries:
        print("\n" + "=" * 60)
        print(f"🧪 TEST: {query}")
        print("=" * 60)
        
        result = rag.process_query(query)
        
        if result['success']:
            print(f"✅ Documentos encontrados: {result['documents_found']}")
            print(f"📝 Respuesta:\n{result['response']}")
            if result['sources']:
                print(f"📄 Fuentes: {', '.join(result['sources'])}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("✅ Sistema RAG MVP listo para integración")
    print("🔧 Sistema: UltraSimpleRAG (sin embeddings complejos)")
    print("📊 Documentos cargados:", len(rag.documents))
    print("=" * 60)
    
    return rag

if __name__ == "__main__":
    rag_system = test_system()