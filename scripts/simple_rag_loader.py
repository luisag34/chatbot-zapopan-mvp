#!/usr/bin/env python3
"""
Cargador RAG simple sin dependencias problemáticas
Usa búsqueda de texto simple para MVP
"""

import os
import json
import pickle
import re
from typing import List, Dict, Any
import sys

# Configuración
DATA_DIR = "data/documents"
INDEX_PATH = "data/rag_index/simple_index.pkl"

def load_jsonl_file(filepath: str) -> List[Dict[str, Any]]:
    """Cargar archivo JSONL"""
    documents = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    documents.append(json.loads(line))
        print(f"  ✅ Cargados {len(documents)} documentos de {os.path.basename(filepath)}")
        return documents
    except Exception as e:
        print(f"  ❌ Error cargando {filepath}: {e}")
        return []

def get_document_level(folder_path: str) -> str:
    """Determinar nivel jerárquico basado en carpeta"""
    folder_name = os.path.basename(folder_path)
    
    if "001 documentos estatales" in folder_name:
        return "nivel_1"
    elif "002 reglamentos municipales" in folder_name:
        return "nivel_2"
    elif "003 códigos y otros municipales" in folder_name:
        return "nivel_3"
    elif "004 directorio y contactos" in folder_name:
        return "nivel_4"
    else:
        return "desconocido"

def extract_keywords(text: str) -> List[str]:
    """Extraer palabras clave simples del texto"""
    # Eliminar caracteres especiales y convertir a minúsculas
    clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
    # Dividir en palabras y filtrar palabras comunes
    words = clean_text.split()
    common_words = {'el', 'la', 'los', 'las', 'de', 'en', 'y', 'a', 'que', 'se', 'por', 'con', 'para', 'un', 'una', 'unos', 'unas', 'del', 'al'}
    keywords = [word for word in words if word not in common_words and len(word) > 3]
    return list(set(keywords))[:20]  # Máximo 20 palabras clave

def process_rag_jsonl_files():
    """Procesar todos los archivos JSONL RAG"""
    print("🔍 BUSCANDO ARCHIVOS JSONL RAG...")
    
    all_documents = []
    
    # Recorrer las 4 carpetas principales
    for level_folder in os.listdir(DATA_DIR):
        level_path = os.path.join(DATA_DIR, level_folder)
        if not os.path.isdir(level_path):
            continue
            
        nivel = get_document_level(level_path)
        print(f"\n📂 Procesando: {level_folder} ({nivel})")
        
        # Buscar archivos JSONL RAG
        for root, dirs, files in os.walk(level_path):
            for file in files:
                if file.endswith('_dataset_rag.jsonl') or file.endswith('_chunks_ia.jsonl'):
                    filepath = os.path.join(root, file)
                    documents = load_jsonl_file(filepath)
                    
                    for i, doc in enumerate(documents):
                        # Extraer texto del documento RAG
                        text = doc.get('text', '') or doc.get('text_normativo', '') or doc.get('chunk_text', '')
                        
                        if not text or len(text.strip()) < 10:
                            continue
                            
                        # Metadatos básicos
                        metadata = {
                            'nivel': nivel,
                            'source_file': file,
                            'folder': level_folder,
                            'document_type': doc.get('document_type', ''),
                            'jurisdiction_level': doc.get('jurisdiction_level', ''),
                            'article': doc.get('article', ''),
                            'numeral': doc.get('numeral', ''),
                            'citation_short': doc.get('citation_short', ''),
                            'id_juridico': doc.get('id_juridico', ''),
                            'document_title': doc.get('document_title', ''),
                            'keywords': extract_keywords(text),
                            'text_length': len(text)
                        }
                        
                        all_documents.append({
                            'text': text,
                            'metadata': metadata,
                            'id': f"{nivel}_{os.path.basename(file)}_{i}"
                        })
    
    print(f"\n📊 RESUMEN: {len(all_documents)} chunks encontrados")
    return all_documents

def create_simple_index(documents: List[Dict]):
    """Crear índice simple basado en palabras clave"""
    print("\n🏗️ CREANDO ÍNDICE SIMPLE DE BÚSQUEDA...")
    
    # Crear índice invertido simple
    keyword_index = {}
    
    for doc in documents:
        doc_id = doc['id']
        keywords = doc['metadata']['keywords']
        
        for keyword in keywords:
            if keyword not in keyword_index:
                keyword_index[keyword] = []
            keyword_index[keyword].append(doc_id)
    
    # Guardar índice
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    
    index_data = {
        'documents': documents,
        'keyword_index': keyword_index,
        'total_documents': len(documents)
    }
    
    with open(INDEX_PATH, 'wb') as f:
        pickle.dump(index_data, f)
    
    print(f"\n🎉 ÍNDICE SIMPLE CREADO EXITOSAMENTE")
    print(f"   📊 Total documentos: {len(documents)}")
    print(f"   🔑 Palabras clave únicas: {len(keyword_index)}")
    print(f"   📁 Índice guardado: {INDEX_PATH}")
    print(f"   📏 Tamaño: {os.path.getsize(INDEX_PATH) / 1024 / 1024:.2f} MB")
    
    return index_data

def search_simple_index(query: str, index_data: Dict, top_k: int = 5) -> List[Dict]:
    """Búsqueda simple por palabras clave"""
    query_keywords = extract_keywords(query)
    scores = {}
    
    # Buscar documentos que contengan palabras clave de la consulta
    for keyword in query_keywords:
        if keyword in index_data['keyword_index']:
            for doc_id in index_data['keyword_index'][keyword]:
                if doc_id not in scores:
                    scores[doc_id] = 0
                scores[doc_id] += 1
    
    # Ordenar por puntaje
    sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    # Recuperar documentos completos
    results = []
    for doc_id, score in sorted_docs:
        for doc in index_data['documents']:
            if doc['id'] == doc_id:
                results.append({
                    'document': doc,
                    'score': score,
                    'match_keywords': query_keywords
                })
                break
    
    return results

def test_simple_index():
    """Probar el índice simple creado"""
    print("\n🔍 PRUEBA DE BÚSQUEDA SIMPLE...")
    
    # Cargar índice
    with open(INDEX_PATH, 'rb') as f:
        index_data = pickle.load(f)
    
    # Consultas de prueba
    test_queries = [
        "inspección y vigilancia facultades",
        "reglamento de construcción",
        "comercio en vía pública"
    ]
    
    for query in test_queries:
        print(f"\n  🔎 Consulta: '{query}'")
        results = search_simple_index(query, index_data, top_k=2)
        
        if results:
            print(f"  📝 Resultados encontrados: {len(results)}")
            for i, result in enumerate(results):
                doc = result['document']
                metadata = doc['metadata']
                text_preview = doc['text'][:150] + "..." if len(doc['text']) > 150 else doc['text']
                print(f"    {i+1}. 📄 {metadata.get('document_title', 'Sin título')}")
                print(f"       📍 Nivel: {metadata.get('nivel', 'N/A')}")
                print(f"       📏 Puntaje: {result['score']}")
                print(f"       📝 Texto: {text_preview}")
        else:
            print(f"  ❌ No se encontraron resultados")
    
    return True

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 CARGA DE DOCUMENTOS RAG - SISTEMA SIMPLE")
    print("=" * 60)
    
    # Verificar que existe directorio de datos
    if not os.path.exists(DATA_DIR):
        print(f"❌ Directorio de datos no encontrado: {DATA_DIR}")
        sys.exit(1)
    
    # Procesar archivos JSONL
    documents = process_rag_jsonl_files()
    
    if not documents:
        print("❌ No se encontraron documentos para procesar")
        sys.exit(1)
    
    # Crear índice simple
    index_data = create_simple_index(documents)
    
    # Probar índice
    test_simple_index()
    
    print("\n" + "=" * 60)
    print("✅ CARGA COMPLETADA EXITOSAMENTE (SISTEMA SIMPLE)")
    print("=" * 60)
    print("\n📋 RESUMEN FINAL:")
    print(f"   • Documentos procesados: {len(documents)}")
    print(f"   • Índice guardado: {INDEX_PATH}")
    print(f"   • Sistema: Búsqueda por palabras clave")
    print(f"   • Compatible: 100% Python puro, sin dependencias problemáticas")

if __name__ == "__main__":
    main()