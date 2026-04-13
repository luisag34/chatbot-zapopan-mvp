# CHATBOT INSPECCIÓN Y VIGILANCIA ZAPOPAN - MVP PLAN

**Fecha inicio:** 6 abril 2026 16:48 CST  
**MVP Deadline:** 8 abril 2026 16:48 CST (48 horas)  
**Versión completa:** 20 abril 2026 (2 semanas)  
**Plataforma:** Vercel  
**Estado:** Desarrollo iniciado

---

## 🎯 OBJETIVO MVP (48 HORAS)

Desarrollar chatbot funcional que:
1. **Acceda** a documentos de 4 carpetas (39.2 MB JSONL/TXT)
2. **Implemente** sistema RAG básico con ChromaDB
3. **Siga estrictamente** System Instructions V03
4. **Autentique** 23 usuarios definidos
5. **Responda** consultas sobre facultades de Dirección de Inspección y Vigilancia
6. **Despliegue** en Vercel funcional

---

## 📁 ESTRUCTURA DE DOCUMENTOS

### **FUENTES (39.2 MB):**
1. **001 documentos estatales y NOM federales**
2. **002 reglamentos municipales**
3. **003 códigos y otros municipales**
4. **004 directorio y contactos** (CSV)

### **FORMATOS:**
- JSONL (ya procesado para RAG)
- TXT
- CSV (directorio)

---

## 👥 USUARIOS DEFINIDOS (23)

### **ADMINISTRADOR SUPREMO:**
- `administrador_supremo` (Luis)

### **USUARIOS GENERALES (22):**
1. `dirección_inspección`
2. `dirección_02`
3. `comercio_jefatura`
4. `comercio_operativo`
5. `técnica_jefatura`
6. `técnica_operativo`
7. `construcción_jefatura`
8. `construcción_operativo`
9. `nocturno_jefatura`
10. `nocturno_operativo`
11. `atenciónciudadana_jefatura`
12. `atenciónciudadana_02`
13. `atenciónciudadana_03`
14. `atenciónciudadana_04`
15. `atenció-nciudadana_05`
16. `jurídico_jefatura`
17. `jurídico_02`
18. `jurídico_03`
19. `jurídico_04`
20. `jurídico_05`
21. `administrativo_jefatura`

---

## 🏗️ ARQUITECTURA TÉCNICA MVP

### **BACKEND (FastAPI):**
- **RAG:** ChromaDB vector store
- **LLM:** deepseek-chat API
- **Autenticación:** JWT tokens
- **Base datos:** SQLite (MVP) → PostgreSQL (completo)

### **FRONTEND (Streamlit):**
- **Interfaz chat:** Consultas/respuestas
- **Login/logout:** Autenticación 23 usuarios
- **Visualización:** Respuestas con fuentes

### **SISTEMA RAG:**
- **ChromaDB:** Vector store local
- **Embeddings:** all-MiniLM-L6-v2 (local, rápido)
- **Retrieval:** Semantic search + filtros

### **DEPLOYMENT (Vercel):**
- **Backend:** FastAPI en Vercel
- **Frontend:** Streamlit en Vercel
- **Base datos:** SQLite embebido (MVP)

---

## ⏰ TIMELINE MVP (48 HORAS)

### **HORAS 0-6 (HOY 16:48-22:48):**
- [ ] Copiar documentos a workspace
- [ ] Analizar estructura JSONL/TXT/CSV
- [ ] Configurar entorno desarrollo
- [ ] Crear plan detallado por hora

### **HORAS 6-18 (MAÑANA 06:00-18:00):**
- [ ] Implementar sistema RAG básico
- [ ] Configurar ChromaDB con documentos
- [ ] Desarrollar backend FastAPI
- [ ] Implementar autenticación JWT

### **HORAS 18-30 (MAÑANA 18:00-06:00 DÍA 2):**
- [ ] Desarrollar frontend Streamlit
- [ ] Integrar backend-frontend
- [ ] Implementar sistema auditoría básico
- [ ] Configurar API deepseek-chat

### **HORAS 30-42 (DÍA 2 06:00-18:00):**
- [ ] Pruebas funcionales
- [ ] Ajustes basados en testing
- [ ] Preparar deployment Vercel
- [ ] Documentación MVP

### **HORAS 42-48 (DÍA 2 18:00-00:00):**
- [ ] Deployment en Vercel
- [ ] Pruebas finales
- [ ] Entrega a Luis
- [ ] Plan fase completa

---

## 🔧 DEPENDENCIAS TÉCNICAS

### **BACKEND (requirements_backend.txt):**
```
fastapi>=0.104.0
uvicorn>=0.24.0
chromadb>=0.4.0
sentence-transformers>=2.2.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
sqlite3
pydantic>=2.0.0
requests>=2.31.0
```

### **FRONTEND (requirements_frontend.txt):**
```
streamlit>=1.28.0
requests>=2.31.0
pandas>=2.0.0
```

### **RAG (requirements_rag.txt):**
```
chromadb>=0.4.0
sentence-transformers>=2.2.0
langchain>=0.0.340
pypdf>=3.17.0  # por si hay PDFs
```

---

## 🚀 ENTREGABLES MVP (48 HORAS)

1. **URL Vercel:** Chatbot funcional desplegado
2. **Login funcional:** 23 usuarios autenticables
3. **Sistema RAG:** Consultas sobre documentos
4. **Respuestas:** Según System Instructions V03
5. **Fuentes:** Citas correctas de documentos
6. **Auditoría básica:** Registro de consultas
7. **Documentación:** Cómo usar el sistema
8. **UX implementado:** Principios de diseño de chatbots

### 🎯 PRINCIPIOS UX IMPLEMENTADOS:

#### **1. SET EXPECTATIONS EARLY:**
- Mensaje inicial claro sobre capacidades/limitaciones del bot
- Definición clara de qué puede y no puede hacer

#### **2. DESIGN FOR CONVERSATION FLOW:**
- Respuestas concisas y escaneables
- Quick-reply buttons para consultas comunes
- Preguntas cerradas guiadas para mantener enfoque

#### **3. CONTEXTUAL AWARENESS:**
- Memoria de sesión por usuario
- Evitar repetición de información

#### **4. MULTIPLE INPUT OPTIONS:**
- Texto libre para consultas específicas
- Botones para consultas comunes
- Navegación por categorías temáticas

#### **5. HANDLE ERRORS GRACEFULLY:**
- Mensajes claros cuando no hay información
- Sugerencias de reformulación o consultas relacionadas
- Explicación de limitaciones del sistema

#### **6. PROACTIVE HUMAN HANDOFF:**
- Información de contacto para casos complejos
- Sistema de escalación cuando el bot no puede resolver

#### **7. VISUAL DESIGN:**
- Interfaz limpia y profesional
- Consistente con branding institucional
- Navegación intuitiva

#### **8. ITERATIVE TESTING:**
- Sistema de auditoría con análisis de logs
- Dashboard admin para métricas de uso
- Mejora continua basada en datos reales

---

## ⚠️ RESTRICCIONES CRÍTICAS

1. **SOLO información** de las 4 carpetas especificadas
2. **NINGÚN dato externo** (incluyendo Presidencia Municipal)
3. **Estricto cumplimiento** System Instructions V03
4. **Jerarquía normativa:** Nivel 1 > Nivel 2 > Nivel 3 > Nivel 4
5. **No alucinación:** Solo respuestas basadas en chunks recuperados

---

## 🏰 DOOMBOTS ASIGNADOS

### **MVP FASE (48 HORAS):**
- **Doombot-Investigador:** Análisis documentos
- **Doombot-Programador:** Desarrollo backend/frontend
- **Doombot-Escritor:** Prompts y documentación
- **Doombot-Gestor de Memoria:** Estructura RAG
- **Dr. Doom:** Coordinación y supervisión

### **FASE COMPLETA (2 SEMANAS):**
- Todos los Doombots según especialización
- Dashboard admin completo
- Sistema auditoría avanzado
- Mejoras iterativas

---

**FIRMA:** Dr. Victor von Doom (Instancia Tahoe)  
**INICIO:** 2026-04-06 16:48 CST  
**MVP DEADLINE:** 2026-04-08 16:48 CST  
**ESTADO:** 🚀 DESARROLLO INICIADO