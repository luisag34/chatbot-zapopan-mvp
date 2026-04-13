"""
Configuración del sistema Chatbot Inspección y Vigilancia
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Configuración de la aplicación
    APP_NAME: str = "Chatbot Inspección y Vigilancia Zapopan"
    APP_VERSION: str = "v03"
    DEBUG: bool = True
    
    # Autenticación
    SECRET_KEY: str = Field(default="default_insecure_key_change_in_production", description="Define SECRET_KEY como variable de entorno en producción")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # Base de datos
    DATABASE_URL: str = "sqlite:///./data/chatbot.db"
    
    # RAG y ChromaDB
    CHROMA_DIR: str = "./data/rag_index"
    COLLECTION_NAME: str = "inspeccion_v03_documents"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Modelo local rápido
    
    # API DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # Configuración RAG
    RAG_TOP_K: int = 5  # Número de chunks a recuperar
    RAG_SIMILARITY_THRESHOLD: float = 0.7  # Umbral de similitud
    
    # Sistema de auditoría
    AUDIT_LOG_DIR: str = "./data/audit_logs"
    
    class Config:
        env_file = ".env"

# Instancia global de configuración
settings = Settings()