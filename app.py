#!/usr/bin/env python3
"""
Chatbot Inspección y Vigilancia Zapopan - Streamlit App Integrada
Backend + Frontend en un solo archivo para Vercel deployment
"""

import streamlit as st
import json
import hashlib
import base64
import hmac
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, List

# ==================== CONFIGURACIÓN ====================
SECRET_KEY = os.getenv("SECRET_KEY", "")
SESSION_TOKEN_KEY = "chatbot_token"
SESSION_USER_KEY = "chatbot_user"
SESSION_HISTORY_KEY = "chatbot_history"

# Cargar usuarios desde archivo JSON
def load_users():
    try:
        with open("config/users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Usuarios por defecto si no existe archivo
        return {
            "users": {
                "administrador_supremo": {
                    "password_hash": "",  # CONTRASEÑA ROTADA - Configurar en producción
                    "role": "admin",
                    "name": "Administrador Supremo",
                    "department": "Dirección General"
                },
                "usuario_general_01": {
                    "password_hash": "",  # CONTRASEÑA ROTADA - Configurar en producción
                    "role": "user",
                    "name": "Usuario General 01",
                    "department": "Inspección y Vigilancia"
                }
            }
        }

USERS_CONFIG = load_users()

# ==================== BACKEND FUNCTIONS ====================

def simple_hash(password: str) -> str:
    """Hash simple para contraseñas (usar bcrypt en producción)"""
    salt = "zapopan_salt_2026"
    combined = password + salt
    return hashlib.sha256(combined.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    salt = "zapopan_salt_2026"
    combined = plain_password + salt
    computed_hash = hashlib.sha256(combined.encode()).hexdigest()
    return computed_hash == hashed_password

def create_simple_token(username: str) -> str:
    """Crear token simple (HMAC)"""
    timestamp = str(int(datetime.now().timestamp()))
    message = f"{username}:{timestamp}"
    signature = hmac.new(
        SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    token = base64.b64encode(f"{message}:{signature}".encode()).decode()
    return token

def verify_token(token: str) -> Optional[Dict]:
    """Verificar token y extraer información de usuario"""
    try:
        decoded = base64.b64decode(token).decode()
        message, signature = decoded.rsplit(":", 1)
        username, timestamp = message.split(":")
        
        # Verificar firma
        expected_signature = hmac.new(
            SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if signature != expected_signature:
            return None
            
        # Verificar expiración (24 horas)
        token_time = datetime.fromtimestamp(int(timestamp))
        if datetime.now() - token_time > timedelta(hours=24):
            return None
            
        # Obtener información del usuario
        if username in USERS_CONFIG["users"]:
            user_info = USERS_CONFIG["users"][username].copy()
            user_info["username"] = username
            return user_info
            
    except Exception:
        return None
    return None

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Autenticar usuario y devolver token"""
    if username in USERS_CONFIG["users"]:
        user_data = USERS_CONFIG["users"][username]
        if verify_password(password, user_data["password_hash"]):
            token = create_simple_token(username)
            user_info = user_data.copy()
            user_info["username"] = username
            user_info["token"] = token
            return user_info
    return None

# ==================== FRONTEND STREAMLIT ====================

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        background-color: #003366;
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .chat-message-user {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 5px solid #2196f3;
    }
    .chat-message-bot {
        background-color: #f1f8e9;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 5px solid #4caf50;
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #f9f9f9;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado de sesión
if SESSION_TOKEN_KEY not in st.session_state:
    st.session_state[SESSION_TOKEN_KEY] = None
if SESSION_USER_KEY not in st.session_state:
    st.session_state[SESSION_USER_KEY] = None
if SESSION_HISTORY_KEY not in st.session_state:
    st.session_state[SESSION_HISTORY_KEY] = []

def is_logged_in():
    """Verificar si usuario está logueado"""
    return st.session_state[SESSION_TOKEN_KEY] is not None and st.session_state[SESSION_USER_KEY] is not None

def login_user(username, password):
    """Autenticar usuario"""
    user_info = authenticate_user(username, password)
    if user_info:
        st.session_state[SESSION_TOKEN_KEY] = user_info["token"]
        st.session_state[SESSION_USER_KEY] = user_info
        st.session_state[SESSION_HISTORY_KEY] = []
        return True
    return False

def logout_user():
    """Cerrar sesión"""
    st.session_state[SESSION_TOKEN_KEY] = None
    st.session_state[SESSION_USER_KEY] = None
    st.session_state[SESSION_HISTORY_KEY] = []

# ==================== PÁGINA PRINCIPAL ====================

st.title("🏛️ Chatbot Inspección y Vigilancia Zapopan")
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.markdown("### Sistema de consulta sobre facultades de la Dirección de Inspección y Vigilancia")
st.markdown("Acceso restringido a personal autorizado")
st.markdown('</div>', unsafe_allow_html=True)

# Verificar autenticación
if not is_logged_in():
    # Página de login
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.subheader("🔐 Iniciar Sesión")
    
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ingresar", type="primary"):
            if login_user(username, password):
                st.success(f"¡Bienvenido {username}!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    
    with col2:
        if st.button("Limpiar"):
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Información sobre el sistema
    with st.expander("ℹ️ Acerca de este sistema"):
        st.markdown("""
        **Chatbot Inspección y Vigilancia Zapopan**
        
        Este sistema permite consultar información sobre:
        - Facultades de la Dirección de Inspección y Vigilancia
        - Documentos estatales y NOM federales
        - Reglamentos municipales
        - Códigos y normativa aplicable
        
        **Acceso:** Solo personal autorizado del Ayuntamiento de Zapopan
        """)
    
else:
    # Usuario autenticado - Interfaz principal
    user_info = st.session_state[SESSION_USER_KEY]
    
    # Barra superior con información de usuario
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown(f"**Usuario:** {user_info.get('name', user_info['username'])}")
    with col2:
        st.markdown(f"**Rol:** {user_info.get('role', 'user')}")
    with col3:
        if st.button("🚪 Cerrar Sesión"):
            logout_user()
            st.rerun()
    
    # Interfaz de chat
    st.subheader("💬 Consultas al Sistema")
    
    # Historial de chat
    chat_history = st.session_state[SESSION_HISTORY_KEY]
    for message in chat_history[-10:]:  # Mostrar últimos 10 mensajes
        if message["role"] == "user":
            st.markdown(f'<div class="chat-message-user"><strong>Tú:</strong> {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message-bot"><strong>Chatbot:</strong> {message["content"]}</div>', unsafe_allow_html=True)
    
    # Entrada de consulta
    query = st.text_input("Escribe tu consulta sobre facultades, documentos o normativa:", key="query_input")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("📤 Enviar", type="primary") and query:
            # Agregar mensaje de usuario al historial
            chat_history.append({"role": "user", "content": query, "timestamp": datetime.now().isoformat()})
            
            # Respuesta simulada del chatbot (en MVP real, aquí iría RAG)
            response = f"Consulta recibida: '{query}'\n\n"
            response += "**Sistema en desarrollo MVP**\n"
            response += "En la versión completa, aquí aparecería información relevante de:\n"
            response += "1. Documentos estatales