# 🏰 CREDENCIALES INTERNAS - Chatbot Inspección y Vigilancia Zapopan

**⚠️ DOCUMENTO CONFIDENCIAL - NO SUBIR A GITHUB ⚠️**

## 🔐 CREDENCIALES DE PRUEBA (MVP)

### **USUARIOS DE PRUEBA:**
| Usuario | Contraseña | Rol | Departamento |
|---------|------------|-----|--------------|
| `administrador_supremo` | `Zapopan2026` | admin | Dirección General |
| `usuario_general_01` | `Zapopan2026` | user | Inspección y Vigilancia |
| `inspector_01` | `Zapopan2026` | user | Inspección de Obras |
| `vigilancia_01` | `Zapopan2026` | user | Vigilancia Sanitaria |

### **USUARIOS REALES (23 USUARIOS CONFIGURADOS):**
Los 23 usuarios reales están configurados en `config/users.json` con:
- **Contraseñas:** Generadas aleatoriamente (cambiar en producción)
- **Roles:** `admin` o `user`
- **Departamentos:** Varios departamentos de la Dirección

## 🔒 SEGURIDAD EN PRODUCCIÓN

### **ACCIONES REQUERIDAS ANTES DE PRODUCCIÓN:**
1. **Cambiar todas las contraseñas** por contraseñas seguras únicas
2. **Eliminar usuarios de prueba** (`administrador_supremo`, etc.)
3. **Configurar autenticación real** con base de datos segura
4. **Implementar HTTPS** (Vercel ya lo proporciona)
5. **Rotar `SECRET_KEY`** por una clave segura aleatoria

### `SECRET_KEY` ACTUAL:
```
chatbot_inspeccion_zapopan_secret_key_2026_cambiar
```
**⚠️ CAMBIAR EN PRODUCCIÓN:** Generar clave aleatoria segura (mínimo 32 caracteres)

## 🌐 URLS DEL SISTEMA

### **PRODUCCIÓN:**
- **Frontend:** `https://chatbot-inspeccion-zapopan.vercel.app`
- **API Health:** `https://chatbot-inspeccion-zapopan.vercel.app/health`
- **API Login:** `https://chatbot-inspeccion-zapopan.vercel.app/api/login`

### **DESARROLLO LOCAL:**
- **Backend:** `http://localhost:8000`
- **Frontend:** `http://localhost:8501` (si se usa Streamlit)

## 📁 ESTRUCTURA DE USUARIOS

### **ARCHIVO `config/users.json`:**
```json
{
  "users": {
    "administrador_supremo": {
      "password_hash": "hash_generado",
      "role": "admin",
      "name": "Administrador Supremo",
      "department": "Dirección General"
    },
    // ... 22 usuarios más
  }
}
```

### **GENERAR NUEVAS CONTRASEÑAS:**
```bash
# Usar script de inicialización
python scripts/init_users.py --new-passwords
```

## 🚨 PROTOCOLO DE SEGURIDAD

### **SI SE EXPONEN CREDENCIALES:**
1. **Inmediatamente:** Cambiar todas las contraseñas
2. **Revocar:** `SECRET_KEY` actual
3. **Regenerar:** Tokens JWT existentes
4. **Auditar:** Logs de acceso no autorizado

### **MANTENIMIENTO PERIÓDICO:**
- **Cada 30 días:** Rotar `SECRET_KEY`
- **Cada 90 días:** Cambiar contraseñas de administradores
- **Cada 180 días:** Revisar y actualizar usuarios

## 📞 CONTACTO SEGURIDAD

**Administrador del sistema:** Luis Alberto Aguirre Gómez  
**Fecha creación:** 07 Abril 2026  
**Última actualización:** 07 Abril 2026  

---

**🏰 NOTA DE DR. DOOM:**  
*"La seguridad no es un producto, es un proceso. En Latveria digital, las credenciales son territorio soberano y se protegen con la misma ferocidad que las fronteras de la nación."*  
**- Dr. Victor von Doom🛡️**