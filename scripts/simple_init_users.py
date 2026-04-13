#!/usr/bin/env python3
"""
Script SIMPLE para inicializar usuarios (sin bcrypt para MVP)
"""

import json
import hashlib
import base64

# Lista de usuarios según especificación
users_list = [
    "administrador_supremo",
    "dirección_inspección",
    "dirección_02",
    "comercio_jefatura",
    "comercio_operativo",
    "técnica_jefatura",
    "técnica_operativo",
    "construcción_jefatura",
    "construcción_operativo",
    "nocturno_jefatura",
    "nocturno_operativo",
    "atenciónciudadana_jefatura",
    "atenciónciudadana_02",
    "atenciónciudadana_03",
    "atenciónciudadana_04",
    "atenció-nciudadana_05",
    "jurídico_jefatura",
    "jurídico_02",
    "jurídico_03",
    "jurídico_04",
    "jurídico_05",
    "administrativo_jefatura"
]

def simple_hash(password: str) -> str:
    """Hash simple para MVP (en producción usar bcrypt)"""
    # SHA256 + salt básico
    salt = "chatbot_zapopan_2026"
    combined = password + salt
    return hashlib.sha256(combined.encode()).hexdigest()

def create_users_config():
    """Crear configuración de usuarios"""
    
    users_config = {
        "system": {
            "name": "Chatbot Inspección y Vigilancia Zapopan",
            "version": "1.0.0",
            "created": "2026-04-06",
            "security_note": "MVP - En producción usar bcrypt con salts únicos"
        },
        "users": {}
    }
    
    # Contraseña por defecto (corta para evitar problemas)
    default_password = os.getenv("DEFAULT_PASSWORD", "ChangeThisPasswordInProduction2026")
    
    # Crear usuarios
    for username in users_list:
        role = "administrador_supremo" if username == "administrador_supremo" else "usuario"
        
        # Determinar departamento basado en nombre de usuario
        if "comercio" in username:
            department = "comercio"
        elif "técnica" in username:
            department = "técnica"
        elif "construcción" in username:
            department = "construcción"
        elif "nocturno" in username:
            department = "nocturno"
        elif "atenciónciudadana" in username:
            department = "atención_ciudadana"
        elif "jurídico" in username:
            department = "jurídico"
        elif "administrativo" in username:
            department = "administrativo"
        elif "dirección" in username:
            department = "dirección"
        else:
            department = "general"
        
        # Permisos basados en rol
        if role == "administrador_supremo":
            permissions = ["chat", "audit", "admin", "users"]
        elif "jefatura" in username:
            permissions = ["chat", "audit_department"]
        else:
            permissions = ["chat"]
        
        users_config["users"][username] = {
            "username": username,
            "password_hash": simple_hash(default_password),
            "role": role,
            "department": department,
            "permissions": permissions,
            "created": "2026-04-06",
            "active": True,
            "note": "Contraseña: Zapopan2026 (cambiar en producción)"
        }
    
    return users_config

def main():
    """Función principal"""
    print("🔧 INICIALIZANDO USUARIOS (MVP SIMPLE)...")
    
    # Crear configuración
    config = create_users_config()
    
    # Guardar en archivo
    output_path = "config/users.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuración guardada en: {output_path}")
    print(f"📊 Total usuarios: {len(config['users'])}")
    print(f"   • Administrador supremo: 1")
    print(f"   • Usuarios generales: {len(config['users']) - 1}")
    print(f"   • Departamentos: 7 diferentes")
    
    print("\n🔑 CREDENCIALES POR DEFECTO (MVP):")
    print(f"   • Usuario: administrador_supremo")
    print(f"   • Contraseña: Zapopan2026")
    print(f"   • Mismo para todos los usuarios (MVP)")
    
    print("\n⚠️ ADVERTENCIA MVP:")
    print("   • Hash simple SHA256 (NO seguro para producción)")
    print("   • Misma contraseña para todos (MVP)")
    print("   • En producción: bcrypt + salts únicos + contraseñas individuales")
    
    print("\n🎉 INICIALIZACIÓN MVP COMPLETADA")

if __name__ == "__main__":
    main()