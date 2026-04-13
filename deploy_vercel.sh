#!/bin/bash
# Script de deployment alternativo para Vercel

echo "🚀 DEPLOYMENT FINAL VERCEL - CHATBOT ZAPOPAN"
echo "============================================="
echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Deadline: 16:48 CST"
echo "Tiempo restante: 1h 40m"
echo "============================================="

# Verificar que tenemos los archivos necesarios
echo "📁 Verificando archivos..."
if [ ! -f "api/index.py" ]; then
    echo "❌ ERROR: api/index.py no encontrado"
    exit 1
fi

if [ ! -f "requirements_vercel_final.txt" ]; then
    echo "❌ ERROR: requirements_vercel_final.txt no encontrado"
    exit 1
fi

echo "✅ Archivos verificados"

# Crear vercel.json si no existe
if [ ! -f "vercel.json" ]; then
    echo "📝 Creando vercel.json..."
    cat > vercel.json << EOF
{
  "functions": {
    "api/*.py": {
      "maxDuration": 10
    }
  },
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/api/index.py"
    }
  ]
}
EOF
    echo "✅ vercel.json creado"
fi

# Verificar contenido de api/index.py
echo "🔍 Verificando API..."
PYTHON_CONTENT=$(head -20 api/index.py)
if [[ $PYTHON_CONTENT != *"from http.server import"* ]]; then
    echo "⚠️  ADVERTENCIA: api/index.py puede no ser la versión correcta"
fi

# Mostrar resumen
echo ""
echo "📊 RESUMEN PARA DEPLOYMENT:"
echo "----------------------------"
echo "1. API: api/index.py (optimizado para serverless)"
echo "2. Requirements: requirements_vercel_final.txt (sin dependencias)"
echo "3. Config: vercel.json (configuración Vercel)"
echo "4. Frontend: HTML integrado en API"
echo "5. RAG System: VercelRAGSystem (5 documentos clave)"
echo "6. Seguridad: Rate limiting + token validation"
echo ""
echo "🌐 URL POST-DEPLOYMENT: https://chatbot-inspeccion-zapopan.vercel.app"
echo ""
echo "🔧 INSTRUCCIONES MANUALES:"
echo "----------------------------"
echo "1. Ir a https://vercel.com"
echo "2. Seleccionar proyecto 'chatbot-inspeccion-zapopan'"
echo "3. Hacer drag & drop de esta carpeta"
echo "4. Configurar:"
echo "   - Runtime: Python"
echo "   - Build Command: (dejar vacío)"
echo "   - Output Directory: ."
echo "5. Deploy"
echo ""
echo "⏰ TIEMPO ESTIMADO: 5-10 minutos"
echo ""
echo "✅ LISTO PARA DEPLOYMENT MANUAL"
echo "============================================="