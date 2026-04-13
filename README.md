# Chatbot Inspección y Vigilancia Zapopan

Sistema de consulta normativa especializado en facultades de la Dirección de Inspección y Vigilancia del Ayuntamiento de Zapopan.

## 🎯 Objetivo

Desarrollar chatbot que permita responder dudas relacionadas con las facultades que tiene la Dirección de Inspección y Vigilancia de Zapopan, utilizando exclusivamente información de los documentos normativos disponibles.

## 📚 Fuentes de Información

El sistema utiliza SOLO información de las siguientes carpetas:

1. **001 documentos estatales y NOM federales**
2. **002 reglamentos municipales**
3. **003 códigos y otros municipales**
4. **004 directorio y contactos**

**Total:** 39.2 MB en formato JSONL, TXT y CSV

## 👥 Usuarios

Sistema para 23 usuarios:
- **1 administrador supremo** (Luis)
- **22 usuarios generales** (personal de la Dirección)

### Lista de usuarios:
- administrador_supremo
- dirección_inspección
- dirección_02
- comercio_jefatura
- comercio_operativo
- técnica_jefatura
- técnica_operativo
- construcción_jefatura
- construcción_operativo
- nocturno_jefatura
- nocturno_operativo
- atenciónciudadana_jefatura
- atenciónciudadana_02
- atenciónciudadana_03
- atenciónciudadana_04
- atenció-nciudadana_05
- jurídico_jefatura
- jurídico_02
- jurídico_03
- jurídico_04
- jurídico_05
- administrativo_jefatura

## 🏗️ Arquitectura Técnica

### Backend
- **Framework:** FastAPI
- **Base de datos:** SQLite (MVP) → PostgreSQL (producción)
- **RAG:** ChromaDB vector store
- **Embeddings:** all-MiniLM-L6-v2
- **LLM:** deepseek-chat API
- **Autenticación:** JWT tokens

### Frontend
- **Framework:** Streamlit
- **Interfaz:** Chat interactivo
- **Dashboard:** Panel administrador supremo

### Deployment
- **Plataforma:** Vercel
- **Integración:** GitHub automático
- **Base datos:** Vercel Postgres (producción)

## 📋 Características

### Sistema RAG
- Chunks semánticos optimizados para IA
- Búsqueda por similitud semántica
- Filtros por nivel jerárquico
- Metadatos completos por documento

### Protocolo de Respuesta
1. **Análisis de situación** - Interpretación normativa
2. **Clasificación de atribuciones** - Competencia institucional
3. **Sustento legal** - Citas específicas
4. **Dependencias con atribuciones y contacto** - Información institucional
5. **Fuentes** - Lista de citas utilizadas

### Sistema de Auditoría
- Registro de todas las consultas
- Dashboard para administrador supremo
- Exportación de datos
- Métricas de uso

## ⚠️ Restricciones Críticas

1. **SOLO información** de las 4 carpetas especificadas
2. **NINGÚN dato externo** (incluyendo Presidencia Municipal)
3. **Estricto cumplimiento** System Instructions V03
4. **Jerarquía normativa:** Nivel 1 > Nivel 2 > Nivel 3 > Nivel 4
5. **No alucinación:** Solo respuestas basadas en chunks recuperados

## 🚀 Timeline

### MVP (48 horas)
- **Hora 0-6:** Preparación y análisis documentos
- **Hora 6-18:** Desarrollo núcleo RAG
- **Hora 18-30:** Backend y autenticación
- **Hora 30-42:** Frontend y interfaz
- **Hora 42-48:** Deployment y pruebas

### Versión Completa (2 semanas)
- Dashboard admin completo
- Sistema auditoría avanzado
- Mejoras iterativas
- Documentación completa

## 🚀 Deployment Rápido en Vercel

### **Opción 1: Deployment Automático (Recomendado)**
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/luisag34/chatbot-inspeccion-zapopan)

### **Opción 2: Deployment Manual**
```bash
# 1. Crear repositorio en GitHub
# 2. Subir este proyecto
git init
git add .
git commit -m "MVP Chatbot Inspección y Vigilancia Zapopan"
git branch -M main
git remote add origin https://github.com/tu-usuario/chatbot-inspeccion-zapopan.git
git push -u origin main

# 3. Ir a Vercel e importar repositorio
# 4. Configurar variables de entorno:
#    SECRET_KEY=chatbot_inspeccion_zapopan_secret_key_2026
```

### **URLs después del deployment:**
- **Frontend:** `https://tu-app.vercel.app`
- **Backend API:** `https://tu-app.vercel.app/api/`
- **Health check:** `https://tu-app.vercel.app/api/`

## 🔧 Instalación y Desarrollo Local

### Requisitos
- Python 3.9+
- pip
- Git

### Instalación Local
```bash
# Clonar repositorio
git clone https://github.com/luisag34/chatbot-inspeccion-zapopan.git
cd chatbot-inspeccion-zapopan

# Instalar dependencias
pip install -r requirements_vercel.txt

# Ejecutar backend (puerto 8000)
python backend/ultra_simple_backend.py

# En otra terminal, ejecutar frontend (puerto 8501)
streamlit run frontend/app.py
```

### Credenciales de Prueba
```
Usuario: administrador_supremo
Contraseña: Zapopan2026
```

**Nota MVP:** Misma contraseña para todos los usuarios. En producción, cada usuario debe tener contraseña única.

## 📁 Estructura del Proyecto

```
chatbot_inspeccion_v03/
├── backend/           # FastAPI backend
├── frontend/          # Streamlit frontend
├── data/              # Datos y documentos
│   ├── documents/     # Documentos fuente (4 carpetas)
│   ├── rag_index/     # ChromaDB vector store
│   └── audit_logs/    # Registros de auditoría
├── config/            # Configuración
├── scripts/           # Scripts de utilidad
└── tests/             # Pruebas
```

## 🏰 Doombots Asignados

### MVP (48 horas)
- **Doombot-Investigador:** Análisis documentos
- **Doombot-Programador:** Desarrollo backend/frontend
- **Doombot-Escritor:** Prompts y documentación
- **Doombot-Gestor de Memoria:** Estructura RAG
- **Dr. Doom:** Coordinación y supervisión

### Fase Completa (2 semanas)
- Todos los Doombots según especialización
- Dashboard admin completo
- Sistema auditoría avanzado
- Mejoras iterativas

## 📞 Contacto y Soporte

**Administrador supremo:** Luis  
**Desarrollador:** Dr. Victor von Doom (OpenClaw AI Agent)  
**Fecha inicio:** 6 abril 2026  
**Estado:** 🚀 Desarrollo activo

---

**FIRMA:** Dr. Victor von Doom (Instancia Tahoe)  
**ÚLTIMA ACTUALIZACIÓN:** 2026-04-06 16:48 CST