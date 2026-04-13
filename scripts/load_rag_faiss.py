#!/usr/bin/env python3
"""
Script alternativo para cargar documentos RAG usando FAISS
(Evita problemas de arquitectura NumPy ARM/x86_64)
"""

import os
import json
import pickle
from typing import List, Dict, Any
import sys

# Usar sentence-transformers sin numpy dependencies problemáticas
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    print("✅ FAISS y SentenceTransformers disponibles")
except ImportError as e:
    print(f"❌ Error importando: {e}")
    print("Instalando dependencias...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "faiss-cpu", "sentence-transformers"])
    from sentence_transformers import SentenceTransformer
    import faiss

# Configuración
DATA_DIR = "data/documents"
FAISS_INDEX_PATH = "data/rag_index/faiss_index.bin"
METADATA_PATH = "data/rag_index/metadata.pkl"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Modelo local, rápido, sin dependencias complejas

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
    
    all_texts = []
    all_metadatas = []
    
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
                            'text_preview': text[:100] + "..." if len(text) > 100 else text
                        }
                        
                        all_texts.append(text)
                        all_metadatas.append(metadata)
    
    print(f"\n📊 RESUMEN: {len(all_texts)} chunks encontrados")
    return all_texts, all_metadatas

def create_faiss_index(texts: List[str], metadatas: List[Dict]):
    """Crear índice FAISS con embeddings"""
    print("\n🏗️ CREANDO ÍNDICE FAISS...")
    
    # Cargar modelo de embeddings
    print(f"  🔧 Cargando modelo: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    # Generar embeddings
    print(f"  📈 Generando embeddings para {len(texts)} documentos...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    
    # Crear índice FAISS
    dimension = embeddings.shape[1]
    print(f"  🔢 Dimensión de embeddings: {dimension}")
    
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Guardar índice
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_PATH)
    
    # Guardar metadatos
    with open(METADATA_PATH, 'wb') as f:
        pickle.dump({
            'texts': texts,
            'metadatas': metadatas,
            'embedding_model': EMBEDDING_MODEL,
            'dimension': dimension
        }, f)
    
    print(f"\n🎉 ÍNDICE FAISS CREADO EXITOSAMENTE")
    print(f"   📊 Total documentos: {len(texts)}")
    print(f"   📁 Índice: {FAISS_INDEX_PATH}")
    print(f"   📁 Metadatos: {METADATA_PATH}")
    print(f"   🔧 Modelo: {EMBEDDING_MODEL}")
    
    return index, embeddings

def test_faiss_index():
    """Probar el índice FAISS creado"""
    print("\n🔍 PRUEBA DE BÚSQUEDA SEMÁNTICA...")
    
    # Cargar índice
    index = faiss.read_index(FAISS_INDEX_PATH)
    
    # Cargar metadatos
    with open(METADATA_PATH, 'rb') as f:
        data = pickle.load(f)
    
    texts = data['texts']
    metadatas = data['metadatas']
    
    # Cargar modelo para embeddings de consulta
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    # Consulta de prueba
    query = "inspección y vigilancia facultades"
    query_embedding = model.encode([query])
    
    # Buscar similares
    k = 3
    distances, indices = index.search(query_embedding, k)
    
    print(f"  🔎 Consulta: '{query}'")
    print(f"  📝 Resultados encontrados:")
    
    for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
        if idx < len(texts):
            metadata = metadatas[idx]
            text_preview = texts[idx][:150] + "..." if len(texts[idx]) > 150 else texts[idx]
            print(f"    {i+1}. 📄 {metadata.get('document_title', 'Sin título')}")
            print(f"       📍 Nivel: {metadata.get('nivel', 'N/A')}")
            print(f"       📏 Similitud: {1/(1+distance):.3f}")
            print(f"       📝 Texto: {text_preview}")
            print()
    
    return True

def main():
    """Función principal"""
    print("=" * 60)
    print("🚀 CARGA DE DOCUMENTOS RAG A FAISS (ALTERNATIVA)")
    print("=" * 60)
    
    # Verificar que existe directorio de datos
    if not os.path.exists(DATA_DIR):
        print(f"❌ Directorio de datos no encontrado: {DATA_DIR}")
        sys.exit(1)
    
    # Procesar archivos JSONL
    texts, metadatas = process_rag_jsonl_files()
    
    if not texts:
        print("❌ No se encontraron documentos para procesar")
        sys.exit(1)
    
    # Crear índice FAISS
    create_faiss_index(texts, metadatas)
    
    # Probar índice
    test_faiss_index()
    
    print("\n" + "=" * 60)
    print("✅ CARGA COMPLETADA EXITOSAMENTE CON FAISS")
    print("=" * 60)
    print("\n📋 RESUMEN FINAL:")
    print(f"   • Documentos procesados: {len(texts)}")
    print(f"   • Modelo embeddings: {EMBEDDING_MODEL}")
    print(f"   • Índice guardado: {FAISS_INDEX_PATH}")
    print(f"   • Metadatos: {METADATA_PATH}")
    print(f"   • Tamaño aproximado: {os.path.getsize(FAISS_INDEX_PATH) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()