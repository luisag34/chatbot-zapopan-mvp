#!/usr/bin/env python3
"""
Script para cargar documentos JSONL RAG a ChromaDB
Los documentos YA están procesados en formato RAG optimizado
"""

import os
import json
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import sys

# Configuración
DATA_DIR = "data/documents"
CHROMA_DIR = "data/rag_index"
COLLECTION_NAME = "inspeccion_v03_documents"

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

def process_rag_jsonl_files():
    """Procesar todos los archivos JSONL RAG"""
    print("🔍 BUSCANDO ARCHIVOS JSONL RAG...")
    
    all_documents = []
    all_metadatas = []
    all_ids = []
    
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
                        # Extraer metadatos del documento RAG
                        doc_id = f"{nivel}_{os.path.basename(file)}_{i}"
                        text = doc.get('text', '') or doc.get('text_normativo', '') or doc.get('chunk_text', '')
                        
                        if not text:
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
                            'document_title': doc.get('document_title', '')
                        }
                        
                        all_documents.append(text)
                        all_metadatas.append(metadata)
                        all_ids.append(doc_id)
    
    print(f"\n📊 RESUMEN: {len(all_documents)} chunks encontrados")
    return all_documents, all_metadatas, all_ids

def create_chroma_collection(documents: List[str], metadatas: List[Dict], ids: List[str]):
    """Crear colección ChromaDB con los documentos"""
    print("\n🏗️ CREANDO COLECCIÓN CHROMADB...")
    
    # Configurar ChromaDB
    chroma_client = chromadb.PersistentClient(
        path=CHROMA_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Eliminar colección existente si existe
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
        print("  ♻️ Colección existente eliminada")
    except:
        print("  ✅ No había colección existente")
    
    # Crear nueva colección
    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Documentos RAG para Chatbot Inspección y Vigilancia Zapopan"}
    )
    
    # Agregar documentos en lotes (ChromaDB tiene límite de lote)
    batch_size = 100
    total_batches = (len(documents) + batch_size - 1) // batch_size
    
    print(f"  📦 Procesando {total_batches} lotes de {batch_size} documentos cada uno...")
    
    for i in range(0, len(documents), batch_size):
        batch_end = min(i + batch_size, len(documents))
        batch_docs = documents[i:batch_end]
        batch_metas = metadatas[i:batch_end]
        batch_ids = ids[i:batch_end]
        
        collection.add(
            documents=batch_docs,
            metadatas=batch_metas,
            ids=batch_ids
        )
        
        print(f"  ✅ Lote {i//batch_size + 1}/{total_batches}: {len(batch_docs)} documentos")
    
    # Verificar colección
    count = collection.count()
    print(f"\n🎉 COLECCIÓN CREADA EXITOSAMENTE")
    print(f"   📊 Total documentos: {count}")
    print(f"   📁 Ubicación: {CHROMA_DIR}")
    print(f"   🏷️ Nombre: {COLLECTION_NAME}")
    
    return collection

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 CARGA DE DOCUMENTOS RAG A CHROMADB")
    print("=" * 60)
    
    # Verificar que existe directorio de datos
    if not os.path.exists(DATA_DIR):
        print(f"❌ Directorio de datos no encontrado: {DATA_DIR}")
        sys.exit(1)
    
    # Procesar archivos JSONL
    documents, metadatas, ids = process_rag_jsonl_files()
    
    if not documents:
        print("❌ No se encontraron documentos para procesar")
        sys.exit(1)
    
    # Crear colección ChromaDB
    collection = create_chroma_collection(documents, metadatas, ids)
    
    # Ejemplo de búsqueda de prueba
    print("\n🔍 PRUEBA DE BÚSQUEDA SEMÁNTICA...")
    results = collection.query(
        query_texts=["inspección y vigilancia facultades"],
        n_results=3
    )
    
    print(f"  ✅ Búsqueda exitosa")
    print(f"  📝 Primer resultado: {results['documents'][0][0][:100]}...")
    
    print("\n" + "=" * 60)
    print("✅ CARGA COMPLETADA EXITOSAMENTE")
    print("=" * 60)

if __name__ == "__main__":
    main()