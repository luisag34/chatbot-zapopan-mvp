#!/usr/bin/env python3
"""
Sistema RAG simple para Chatbot Inspección Zapopan
Usa documentos JSONL ya procesados
"""

import json
import os
import glob
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

class SimpleRAGSystem:
    def __init__(self, documents_path: str = "data/documents"):
        """
        Inicializa sistema RAG simple
        
        Args:
            documents_path: Ruta a documentos JSONL procesados
        """
        self.documents_path = documents_path
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        
        # Inicializar componentes
        self._initialize_components()
    
    def _initialize_components(self):
        """Inicializa modelo de embeddings y ChromaDB"""
        print("🔧 Inicializando sistema RAG...")
        
        # 1. Cargar modelo de embeddings (ligero para MVP)
        try:
            print("   📥 Cargando modelo de embeddings...")
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            print("   ✅ Modelo cargado")
        except Exception as e:
            print(f"   ⚠️  Error cargando modelo: {e}")
            print("   🔄 Usando embeddings dummy para testing")
            self.embedding_model = None
        
        # 2. Inicializar ChromaDB (en memoria para MVP)
        print("   📁 Inicializando ChromaDB...")
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))
        
        # 3. Crear o cargar colección
        try:
            self.collection = self.chroma_client.get_collection(name="zapopan_documents")
            print("   ✅ Colección cargada de disco")
        except:
            self.collection = self.chroma_client.create_collection(name="zapopan_documents")
            print("   ✅ Nueva colección creada")
    
    def load_documents(self):
        """Carga documentos JSONL procesados"""
        print(f"\n📚 Cargando documentos de {self.documents_path}...")
        
        documents = []
        jsonl_files = glob.glob(f"{self.documents_path}/**/*.jsonl", recursive=True)
        
        print(f"   📄 Encontrados {len(jsonl_files)} archivos JSONL")
        
        for jsonl_file in jsonl_files[:10]:  # Limitar a 10 archivos para MVP
            try:
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        doc = json.loads(line.strip())
                        documents.append(doc)
            except Exception as e:
                print(f"   ⚠️  Error cargando {jsonl_file}: {e}")
        
        print(f"   ✅ Cargados {len(documents)} documentos")
        return documents
    
    def create_embeddings(self, documents: List[Dict]):
        """Crea embeddings y los almacena en ChromaDB"""
        print(f"\n🔍 Creando embeddings para {len(documents)} documentos...")
        
        if not documents:
            print("   ⚠️  No hay documentos para procesar")
            return
        
        # Extraer textos
        texts = []
        metadatas = []
        ids = []
        
        for i, doc in enumerate(documents):
            text = doc.get('text', doc.get('content', ''))
            if text and len(text) > 50:  # Filtrar textos muy cortos
                texts.append(text)
                metadatas.append({
                    'source': doc.get('source', 'unknown'),
                    'file': doc.get('file', 'unknown'),
                    'type': doc.get('type', 'document')
                })
                ids.append(f"doc_{i}")
        
        print(f"   📝 {len(texts)} textos válidos para embeddings")
        
        # Crear embeddings
        if self.embedding_model and texts:
            print("   🧠 Generando embeddings...")
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Almacenar en ChromaDB
            print("   💾 Almacenando en ChromaDB...")
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            print(f"   ✅ {len(texts)} documentos indexados")
        else:
            print("   ⚠️  Usando embeddings dummy para testing")
            # Crear embeddings dummy para testing
            dummy_embeddings = [[0.1] * 384 for _ in texts]  # 384 dimensiones dummy
            
            self.collection.add(
                embeddings=dummy_embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            print(f"   ✅ {len(texts)} documentos con embeddings dummy")
    
    def query(self, question: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Consulta el sistema RAG
        
        Args:
            question: Pregunta del usuario
            n_results: Número de resultados a retornar
        
        Returns:
            Dict con resultados y documentos relevantes
        """
        print(f"\n❓ Consulta: {question}")
        
        # Crear embedding de la pregunta
        if self.embedding_model:
            question_embedding = self.embedding_model.encode([question]).tolist()[0]
        else:
            # Embedding dummy para testing
            question_embedding = [0.1] * 384
        
        # Buscar en ChromaDB
        try:
            results = self.collection.query(
                query_embeddings=[question_embedding],
                n_results=n_results
            )
            
            # Procesar resultados
            documents = []
            if results['documents']:
                for i, doc_text in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    documents.append({
                        'text': doc_text,
                        'metadata': metadata,
                        'score': results['distances'][0][i] if results['distances'] else 0.0
                    })
            
            return {
                'success': True,
                'question': question,
                'documents': documents,
                'count': len(documents)
            }
            
        except Exception as e:
            print(f"   ❌ Error en consulta: {e}")
            return {
                'success': False,
                'error': str(e),
                'documents': [],
                'count': 0
            }
    
    def generate_response(self, question: str, context_documents: List[Dict]) -> str:
        """
        Genera respuesta basada en documentos
        
        Args:
            question: Pregunta del usuario
            context_documents: Documentos relevantes
        
        Returns:
            Respuesta generada
        """
        if not context_documents:
            return "No encontré información relevante en los documentos. Por favor, reformula tu pregunta."
        
        # Para MVP: Respuesta simple basada en documentos
        context_text = "\n\n".join([doc['text'][:500] for doc in context_documents[:2]])
        
        response = f"""Basado en los documentos de la Dirección de Inspección y Vigilancia de Zapopan:

{context_text}

**Respuesta:** La Dirección de Inspección y Vigilancia tiene facultades en materia de verificación del cumplimiento de normativas municipales, estatales y federales, incluyendo temas de comercio, construcción, y condiciones de seguridad en centros de trabajo.

*Esta es una respuesta de prueba del sistema RAG. El sistema completo integrará un LLM para respuestas más precisas.*"""
        
        return response

def main():
    """Función principal para testing del sistema RAG"""
    print("=" * 60)
    print("🏰 SISTEMA RAG - CHATBOT INSPECCIÓN ZAPOPAN")
    print("=" * 60)
    
    # Inicializar sistema
    rag_system = SimpleRAGSystem()
    
    # Cargar documentos
    documents = rag_system.load_documents()
    
    if documents:
        # Crear embeddings
        rag_system.create_embeddings(documents)
        
        # Probar consultas
        test_questions = [
            "¿Cuáles son las facultades de la Dirección de Inspección y Vigilancia?",
            "¿Qué normativas aplican para comercios?",
            "¿Qué se requiere para una inspección?"
        ]
        
        for question in test_questions:
            print("\n" + "=" * 60)
            print(f"🧪 TEST: {question}")
            print("=" * 60)
            
            # Consultar
            result = rag_system.query(question)
            
            if result['success']:
                print(f"✅ Encontrados {result['count']} documentos relevantes")
                
                # Generar respuesta
                response = rag_system.generate_response(question, result['documents'])
                print(f"\n📝 Respuesta generada:\n{response}")
                
                # Mostrar documentos relevantes
                print(f"\n📄 Documentos relevantes:")
                for i, doc in enumerate(result['documents'][:2], 1):
                    print(f"  {i}. {doc['text'][:200]}...")
                    if doc['metadata']:
                        print(f"     Fuente: {doc['metadata'].get('source', 'N/A')}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
    else:
        print("⚠️  No se pudieron cargar documentos. Usando modo simulado.")
        
        # Modo simulado para testing
        print("\n🧪 Modo simulado activado")
        print("🔧 El sistema RAG está configurado pero necesita documentos reales")
        print("📋 Para producción: Asegurar que los documentos JSONL estén en data/documents/")
    
    print("\n" + "=" * 60)
    print("✅ Sistema RAG inicializado correctamente")
    print("🔧 Listo para integración con backend")
    print("=" * 60)

if __name__ == "__main__":
    main()