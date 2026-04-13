#!/usr/bin/env python3
"""
Frontend Streamlit para Chatbot Inspección y Vigilancia
Con todos los Core UX Principles integrados
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configuración
BACKEND_URL = "http://localhost:8000"
SESSION_TOKEN_KEY = "chatbot_token"
SESSION_USER_KEY = "chatbot_user"
SESSION_HISTORY_KEY = "chatbot_history"

# Estilos CSS personalizados
st.markdown("""
<style>
    /* Estilos generales */
    .main-header {
        background-color: #003366;
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .bot-message {
        background-color: #f1f8e9;
        border-left-color: #4caf50;
    }
    
    .quick-reply-button {
        margin: 5px;
        border-radius: 20px;
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        padding: 8px 16px;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .quick-reply-button:hover {
        background-color: #e0e0e0;
        transform: translateY(-2px);
    }
    
    .error-message {
        background-color: #ffebee;
        border-left-color: #f44336;
        padding: 15px;
        border-radius: 10px;
    }
    
    .success-message {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
        padding: 15px;
        border-radius: 10px;
    }
    
    /* Sidebar */
    .sidebar-user {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Quick-reply buttons (Principio UX 2 & 4)
QUICK_REPLIES = [
    "📊 Comercio y establecimientos",
    "🏗️ Construcción y obras", 
    "🌿 Medio ambiente",
    "📋 Procedimientos administrativos",
    "🚨 Denuncias ciudadanas",
    "❓ Consulta general"
]

# Ejemplos interactivos (Principio UX 4)
EXAMPLES = [
    "¿Puede Inspección clausurar un negocio?",
    "¿Qué hacer si mi vecino construye sin permiso?",
    "¿Cómo denunciar ruido excesivo?",
    "¿Qué documentos necesito para abrir un restaurante?"
]

# Mensaje inicial (Principio UX 1)
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

def init_session_state():
    """Inicializar estado de sesión"""
    if SESSION_HISTORY_KEY not in st.session_state:
        st.session_state[SESSION_HISTORY_KEY] = []
    if "quick_replies" not in st.session_state:
        st.session_state.quick_replies = QUICK_REPLIES.copy()
    if "examples" not in st.session_state:
        st.session_state.examples = EXAMPLES.copy()
    if "last_query" not in st.session_state:
        st.session_state.last_query = None

def is_logged_in():
    """Verificar si usuario está logueado"""
    return SESSION_TOKEN_KEY in st.session_state and SESSION_USER_KEY in st.session_state

def login_user(username, password):
    """Autenticar usuario en backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state[SESSION_TOKEN_KEY] = data["access_token"]
            st.session_state[SESSION_USER_KEY] = data["user"]
            return True, "Login exitoso"
        else:
            return False, "Usuario o contraseña incorrectos"
            
    except requests.exceptions.RequestException as e:
        return False, f"Error de conexión: {str(e)}"

def logout_user():
    """Cerrar sesión"""
    for key in [SESSION_TOKEN_KEY, SESSION_USER_KEY]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state[SESSION_HISTORY_KEY] = []

def send_chat_query(query):
    """Enviar consulta al backend"""
    if not is_logged_in():
        return None, "No autenticado"
    
    try:
        headers = {"Authorization": f"Bearer {st.session_state[SESSION_TOKEN_KEY]}"}
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/chat/query",
            json={"query": query},
            headers=headers,
            timeout=30
        )
        response_time = int((time.time() - start_time) * 1000)
        
        if response.status_code == 200:
            data = response.json()
            
            # Formatear respuesta según estructura de 5 pasos
            formatted_response = format_chat_response(data["response"])
            
            # Agregar a historial (Principio UX 3: Contextual Awareness)
            st.session_state[SESSION_HISTORY_KEY].append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "response": formatted_response,
                "response_time": response_time
            })
            
            # Limitar historial a últimas 10 conversaciones
            if len(st.session_state[SESSION_HISTORY_KEY]) > 10:
                st.session_state[SESSION_HISTORY_KEY].pop(0)
            
            return formatted_response, None
            
        else:
            return None, f"Error del servidor: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return None, f"Error de conexión: {str(e)}"

def format_chat_response(response_data):
    """Formatear respuesta según estructura de 5 pasos"""
    if not response_data:
        return "❌ No se pudo procesar la respuesta"
    
    formatted = ""
    
    # 1. Análisis de situación
    if "analisis_situacion" in response_data:
        formatted += f"✅ **ANÁLISIS DE SITUACIÓN:**\n{response_data['analisis_situacion']}\n\n"
    
    # 2. Clasificación de atribuciones
    if "clasificacion_atribuciones" in response_data:
        formatted += f"📋 **CLASIFICACIÓN DE ATRIBUCIONES:**\n{response_data['clasificacion_atribuciones']}\n\n"
    
    # 3. Sustento legal
    if "sustento_legal" in response_data and response_data['sustento_legal']:
        formatted += f"⚖️ **SUSTENTO LEGAL:**\n"
        for sustento in response_data['sustento_legal']:
            formatted += f"• {sustento}\n"
        formatted += "\n"
    
    # 4. Dependencias con atribuciones
    if "dependencias_atribuciones" in response_data and response_data['dependencias_atribuciones']:
        formatted += f"📞 **DEPENDENCIAS CON ATRIBUCIONES:**\n"
        for dep in response_data['dependencias_atribuciones']:
            formatted += f"• **{dep.get('dependencia', 'Dependencia')}:** {dep.get('funciones', 'Funciones')}\n"
            if dep.get('contacto'):
                formatted += f"  Contacto: {dep['contacto']}\n"
        formatted += "\n"
    
    # 5. Fuentes
    if "fuentes" in response_data and response_data['fuentes']:
        formatted += f"📚 **FUENTES:**\n"
        for fuente in response_data['fuentes']:
            formatted += f"• {fuente.get('documento', 'Documento')}"
            if fuente.get('nivel'):
                formatted += f" (Nivel: {fuente['nivel']})"
            if fuente.get('cita'):
                formatted += f" - {fuente['cita']}"
            formatted += "\n"
    
    return formatted

def display_error_message(error_msg):
    """Mostrar mensaje de error (Principio UX 5)"""
    st.markdown(f"""
    <div class="error-message">
    ⚠️ **ERROR**
    
    {error_msg}
    
    **Sugerencias:**
    • Verifique su conexión a internet
    • Reformule su consulta
    • Intente nuevamente en unos momentos
    </div>
    """, unsafe_allow_html=True)

def display_no_results_message(query):
    """Mostrar mensaje cuando no hay resultados (Principio UX 5)"""
    st.markdown(f"""
    <div class="error-message">
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
    </div>
    """, unsafe_allow_html=True)

def display_login_page():
    """Página de login"""
    st.markdown("<div class='main-header'><h1>🔐 Chatbot Inspección y Vigilancia Zapopan</h1></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Inicio de Sesión")
        
        with st.form("login_form"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar")
            
            if submit:
                if not username or not password:
                    st.error("Por favor complete todos los campos")
                else:
                    with st.spinner("Autenticando..."):
                        success, message = login_user(username, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        
        st.markdown("---")
        st.markdown("**Credenciales MVP:**")
        st.code("Usuario: administrador_supremo\nContraseña: Zapopan2026")
        
        st.markdown("⚠️ **Nota MVP:**")
        st.info("Sistema de demostración. En producción cada usuario tendría credenciales únicas.")

def display_chat_page():
    """Página principal del chat"""
    # Sidebar (Principio UX 7: Visual Design)
    with st.sidebar:
        st.markdown("<div class='sidebar-user'>", unsafe_allow_html=True)
        st.markdown(f"### 👤 {st.session_state[SESSION_USER_KEY]['username']}")
        st.markdown(f"**Rol:** {st.session_state[SESSION_USER_KEY]['role']}")
        st.markdown(f"**Departamento:** {st.session_state[SESSION_USER_KEY]['department']}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Historial reciente (Principio UX 3)
        if st.session_state[SESSION_HISTORY_KEY]:
            st.markdown("### 📜 Historial Reciente")
            for i, item in enumerate(st.session_state[SESSION_HISTORY_KEY][-3:]):
                with st.expander(f"Consulta {i+1}: {item['query'][:30]}..."):
                    st.text(f"Consulta: {item['query']}")
                    st.text(f"Tiempo: {item['response_time']}ms")
        
        # Botón logout
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout_user()
            st.rerun()
        
        # Solo admin puede ver estado del sistema
        if st.session_state[SESSION_USER_KEY]['role'] == 'administrador_supremo':
            st.markdown("---")
            if st.button("📊 Estado del Sistema", use_container_width=True):
                try:
                    headers = {"Authorization": f"Bearer {st.session_state[SESSION_TOKEN_KEY]}"}
                    response = requests.get(f"{BACKEND_URL}/system/status", headers=headers)
                    if response.status_code == 200:
                        status_data = response.json()
                        st.success("✅ Sistema operativo")
                        st.json(status_data)
                    else:
                        st.error("Error obteniendo estado")
                except:
                    st.error("Error de conexión")
    
    # Header principal
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<div class='main-header'><h1>🤖 Chatbot Inspección y Vigilancia</h1><p>Sistema de consulta normativa especializado</p></div>", unsafe_allow_html=True)
    
    # Área de chat
    chat_container = st.container()
    
    # Quick-reply buttons (Principio UX 2 & 4)
    st.markdown("### 💬 Consultas Rápidas")
    cols = st.columns(3)
    for i, reply in enumerate(st.session_state.quick_replies):
        with cols[i % 3]:
            if st.button(reply, use_container_width=True, key=f"quick_{i}"):
                st.session_state.last_query = reply
                st.rerun()
    
    # Ejemplos (Principio UX 4)
    with st.expander("📋 Ejemplos de consultas"):
        cols = st.columns(2)
        for i, example in enumerate(st.session_state.examples):
            with cols[i % 2]:
                if st.button(example, use_container_width=True, key=f"example_{i}"):
                    st.session_state.last_query = example
                    st.rerun()
    
    # Input de texto principal
    st.markdown("### 🔍 Consulta Específica")
    query = st.text_input(
        "Escriba su consulta sobre facultades normativas:",
        placeholder="Ej: '¿Qué facultades tiene Inspección en comercio ambulante?'",
        key="chat_input"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        send_button = st.button("📤 Enviar", use_container_width=True)
    with col2:
        clear_button = st.button("🗑️ Limpiar", use_container_width=True)
    
    # Procesar consulta pendiente
    if st.session_state.last_query:
        query = st.session_state.last_query
        st.session_state.last_query = None
    
    # Manejar envío de consulta
    if send_button and query:
        with st.spinner("🔍 Consultando documentos normativos..."):
            response, error = send_chat_query(query)
            
            with chat_container:
                # Mostrar consulta del usuario
                st.markdown(f"""
                <div class="chat-message user-message">
                👤 **Usuario:** {query}
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar respuesta o error
                if error:
                    display_error_message(error)
                elif response and "NO SE ENCONTRÓ FUNDAMENTO" in response:
                    display_no_results_message(query)
                elif response:
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                    🤖 **Chatbot:**\n\n{response}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("No se recibió respuesta del servidor")
    
    # Manejar limpieza
    if clear_button:
        st.session_state[SESSION_HISTORY_KEY] = []
        st.rerun()
    
    # Mostrar historial de chat
    with chat_container:
        if st.session_state[SESSION_HISTORY_KEY]:
            st.markdown("---")
            st.markdown("### 📜 Historial de Conversación")
            
            for item in reversed(st.session_state[SESSION_HISTORY_KEY][-5:]):
                # Consulta del usuario
                st.markdown(f"""
                <div class="chat-message user-message">
                👤 **Usuario ({datetime.fromisoformat(item['timestamp']).strftime('%H:%M')}):** {item['query']}
                </div>
                """, unsafe_allow_html=True)
                
                # Respuesta del bot
                st.markdown(f"""
                <div class="chat-message bot-message">
                🤖 **Chatbot ({item['response_time']}ms):**\n\n{item['response']}
                </div>
                """, unsafe_allow_html=True)

def main():
    """Función principal"""
    # Configurar página
