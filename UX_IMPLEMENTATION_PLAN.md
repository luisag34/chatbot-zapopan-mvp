# IMPLEMENTACIÓN DE CORE UX PRINCIPLES FOR CHATBOTS

**Proyecto:** Chatbot Inspección y Vigilancia Zapopan  
**Fecha:** 6 abril 2026  
**Estado:** Integración completa en desarrollo

---

## 🎯 1. SET EXPECTATIONS EARLY

### **Implementación Técnica:**
```python
# En frontend/initial_message.py
INITIAL_MESSAGE = """
🤖 **CHATBOT DE INSPECCIÓN Y VIGILANCIA ZAPOPAN**

**¿Qué puedo hacer?**
• Responder consultas sobre facultades normativas
• Analizar situaciones que puedan constituir faltas administrativas
• Identificar dependencias responsables según normativa
• Proporcionar sustento legal específico

**¿Qué NO puedo hacer?**
• Inventar normas o artículos no existentes
• Responder sobre temas fuera del ámbito municipal
• Proporcionar información no contenida en documentos oficiales
• Sustituir asesoría legal personalizada

**Fuentes:** Solo documentos normativos de Zapopan (4 carpetas especificadas)
"""
```

### **Componentes Visuales:**
- **Banner inicial** con iconos y texto claro
- **Tooltip** en input de texto recordando limitaciones
- **Info button** con detalles expandibles

### **Timeline:** Hora 5-6 del desarrollo

---

## 🔄 2. DESIGN FOR CONVERSATION FLOW

### **Implementación Técnica:**
```python
# Estructura de respuesta obligatoria (5 pasos)
RESPONSE_TEMPLATE = """
✅ **ANÁLISIS DE SITUACIÓN:**
{analisis}

📋 **CLASIFICACIÓN DE ATRIBUCIONES:**
{clasificacion}

⚖️ **SUSTENTO LEGAL:**
{sustento}

📞 **DEPENDENCIAS CON ATRIBUCIONES:**
{dependencias}

📚 **FUENTES:**
{fuentes}
"""
```

### **Quick-Reply Buttons:**
```python
QUICK_REPLIES = [
    "📊 Comercio y establecimientos",
    "🏗️ Construcción y obras", 
    "🌿 Medio ambiente",
    "📋 Procedimientos administrativos",
    "🚨 Denuncias ciudadanas",
    "❓ Consulta general"
]
```

### **Guided Questions:**
- Después de cada respuesta: "¿Necesita información sobre algún aspecto específico?"
- Para consultas amplias: "¿Se refiere a [opción A] o [opción B]?"

### **Timeline:** Hora 4-5 del desarrollo

---

## 🧠 3. CONTEXTUAL AWARENESS

### **Implementación Técnica:**
```python
# Sistema de memoria por sesión
class SessionMemory:
    def __init__(self, user_id):
        self.user_id = user_id
        self.last_queries = []  # Últimas 5 consultas
        self.conversation_context = {}
        
    def add_query(self, query, response):
        self.last_queries.append({
            'timestamp': datetime.now(),
            'query': query,
            'response_summary': response[:100]
        })
        if len(self.last_queries) > 5:
            self.last_queries.pop(0)
    
    def get_context(self):
        return {
            'recent_queries': self.last_queries,
            'user_department': self.conversation_context.get('department')
        }
```

### **Features:**
- **Recordar consultas anteriores:** "Retomando su consulta sobre..."
- **Evitar repetición:** "Como mencioné en mi respuesta anterior..."
- **Contexto departamental:** Personalizar respuestas según área del usuario

### **Timeline:** Hora 3-4 del desarrollo

---

## 📱 4. PROVIDE MULTIPLE INPUT OPTIONS

### **Implementación Técnica:**

#### **A. Texto Libre:**
```python
# Input principal con placeholder sugerente
st.chat_input("Ej: '¿Qué facultades tiene Inspección en comercio ambulante?'")
```

#### **B. Botones Predefinidos (10 consultas comunes):**
```python
COMMON_QUERIES = [
    "Facultades en comercio establecido",
    "Procedimiento para denuncias",
    "Requisitos para permisos de construcción",
    "Sanciones por contaminación ambiental",
    "Horarios de atención ciudadana",
    "Documentación para inspecciones",
    "Áreas de competencia por departamento",
    "Plazos para resolución de expedientes",
    "Recursos contra resoluciones",
    "Coordinación con otras dependencias"
]
```

#### **C. Categorías Temáticas:**
```python
CATEGORIES = {
    "comercio": ["establecido", "ambulante", "tianguis", "permisos"],
    "construccion": ["obras", "permisos", "licencias", "inspecciones"],
    "medio_ambiente": ["residuos", "contaminación", "ruido", "olores"],
    "procedimientos": ["denuncias", "multas", "recursos", "apelaciones"]
}
```

#### **D. Ejemplos Interactivos:**
```python
EXAMPLES = [
    "¿Puede Inspección clausurar un negocio?",
    "¿Qué hacer si mi vecino construye sin permiso?",
    "¿Cómo denunciar ruido excesivo?",
    "¿Qué documentos necesito para abrir un restaurante?"
]
```

### **Timeline:** Hora 4-5 del desarrollo

---

## ⚠️ 5. HANDLE ERRORS GRACEFULLY

### **Implementación Técnica:**

#### **A. Sin Resultados:**
```python
NO_RESULTS_MESSAGE = """
❌ **NO SE ENCONTRÓ FUNDAMENTO NORMATIVO**

La consulta "{query}" no encontró correspondencia en los documentos normativos disponibles.

**Posibles razones:**
1. El tema no está regulado en la normativa municipal
2. La consulta es demasiado específica o técnica
3. Los documentos no contemplan ese escenario

**Sugerencias:**
• Reformule su consulta usando términos más generales
• Consulte las categorías disponibles en los botones
• Contacte directamente a la dependencia correspondiente
"""
```

#### **B. Consulta Irrelevante:**
```python
IRRELEVANT_QUERY_MESSAGE = """
⚠️ **CONSULTA FUERA DEL ÁMBITO**

La consulta "{query}" no corresponde a una materia regulada por la Dirección de Inspección y Vigilancia.

**Ámbitos de competencia:**
• Comercio establecido y ambulante
• Construcción y obras
• Medio ambiente municipal
• Procedimientos administrativos

**Alternativas:**
• Consulte sobre temas dentro de las áreas mencionadas
• Use los botones de consultas comunes como guía
"""
```

#### **C. Error Técnico:**
```python
TECHNICAL_ERROR_MESSAGE = """
🔧 **ERROR TÉCNICO**

Disculpe las molestias, hubo un error técnico al procesar su consulta.

**Por favor:**
1. Reformule su consulta
2. Intente nuevamente en unos momentos
3. Si persiste, reporte el problema al administrador

**Error ID:** {error_id}
"""
```

### **Timeline:** Hora 5-6 del desarrollo

---

## 👥 6. PROACTIVE HUMAN HANDOFF

### **Implementación Técnica:**

#### **A. Para Casos Complejos:**
```python
HUMAN_HANDOFF_MESSAGE = """
👥 **CONSULTA COMPLEJA - ESCALACIÓN RECOMENDADA**

Para el caso específico de "{query}", se recomienda contactar directamente con:

**{dependencia}**
• **Contacto:** {contacto}
• **Horario:** {horario}
• **Ubicación:** {ubicacion}

**Motivo de escalación:**
{razon}

**Documentación sugerida para llevar:**
{documentacion}
"""
```

#### **B. Información de Contacto:**
- Integrar datos del directorio institucional (carpeta 004)
- Mostrar solo cuando aplicable según normativa
- Incluir horarios y procedimientos de atención

#### **C. Botón de Escalación:**
```python
if query_complexity > THRESHOLD:
    st.button("📞 Necesito hablar con un especialista humano", 
              on_click=escalate_to_human)
```

### **Timeline:** Hora 6 del desarrollo

---

## 🎨 7. VISUAL DESIGN

### **Implementación Técnica:**

#### **A. Interfaz Streamlit:**
```python
# Configuración de tema
st.set_page_config(
    page_title="Chatbot Inspección y Vigilancia",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
    }
    .bot-message {
        background-color: #f1f8e9;
        border-left: 5px solid #4caf50;
    }
    .quick-reply-button {
        margin: 5px;
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)
```

#### **B. Branding Institucional:**
- **Colores:** Azul institucional (#003366) + Verde (#4CAF50)
- **Logo:** Inspección y Vigilancia Zapopan
- **Tipografía:** Arial/Helvetica para legibilidad

#### **C. Jerarquía Visual:**
1. **Header:** Logo + título + usuario actual
2. **Sidebar:** Navegación + información de usuario
3. **Chat Area:** Historial de conversación
4. **Input Area:** Texto + botones + ejemplos
5. **Footer:** Información legal + contacto

### **Timeline:** Hora 5-6 del desarrollo

---

## 🔧 8. ITERATIVE TESTING

### **Implementación Técnica:**

#### **A. Sistema de Auditoría:**
```python
class AuditSystem:
    def __init__(self):
        self.logs = []
        
    def log_interaction(self, user_id, query, response, metadata):
        log_entry = {
            'timestamp': datetime.now(),
            'user_id': user_id,
            'query': query,
            'response_preview': response[:200],
            'response_time_ms': metadata.get('response_time'),
            'rag_results_count': metadata.get('rag_results'),
            'error': metadata.get('error'),
            'user_feedback': None
        }
        self.logs.append(log_entry)
        
    def analyze_logs(self):
        # Análisis de dead ends
        # Consultas comunes
        # Tiempos de respuesta
        # Errores frecuentes
        pass
```

#### **B. Dashboard Admin:**
- **Métricas clave:** Consultas/día, tiempo respuesta, satisfacción
- **Dead ends identificados:** Consultas sin respuesta
- **Consultas comunes:** Top 10 temas solicitados
- **Errores técnicos:** Frecuencia y tipos

#### **C. Feedback Loop:**
```python
# Botón de feedback en cada respuesta
if st.button("👍 Esta respuesta fue útil"):
    log_feedback(user_id, query_id, "positive")
    
if st.button("👎 Necesito más información"):
    log_feedback(user_id, query_id, "negative", 
                 st.text_input("¿Qué faltó?"))
```

#### **D. Mejora Continua:**
- **Análisis semanal:** Revisión de logs y métricas
- **Ajustes iterativos:** Mejora de prompts y respuestas
- **Actualización documentos:** Incorporar nuevas normativas
- **Testing con usuarios:** Sesiones de prueba con personal real

### **Timeline:** Post-MVP (Semanas 2-3)

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### **Fase 1: MVP (48 horas)**
- **Hora 1-2:** Setup y carga documentos ✅
- **Hora 3-4:** Backend básico + autenticación
- **Hora 4-5:** Frontend con principios UX 1-4
- **Hora 5-6:** Principios UX 5-7 + integración
- **Hora 6-8:** Testing + deployment Vercel

### **Fase 2: Mejora UX (Semana 1)**
- Sistema de memoria contextual
- Dashboard admin básico
- Feedback loop inicial
- Ajustes basados en primeros usos

### **Fase 3: Optimización (Semana 2)**
- Sistema auditoría completo
- Análisis de métricas UX
- Mejoras iterativas
- Documentación completa

---

**FIRMA:** Dr. Victor von Doom  
**FECHA:** 2026-04-06 17:00 CST  
**ESTADO:** 🚀 Desarrollo activo con UX integrado