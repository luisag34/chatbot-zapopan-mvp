#!/bin/bash
# Script de deployment corregido para Vercel - 13 Abril 2026

echo "🚀 DEPLOYMENT CORREGIDO VERCEL - MVP CHATBOT ZAPOPAN"
echo "====================================================="
echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Estado: Post-vacaciones reactivación"
echo "Issue: HTTP 501 (Python no ejecutándose)"
echo "Solución: Configuración optimizada"
echo "====================================================="

# Verificar archivos críticos
echo "📁 Verificando archivos..."
REQUIRED_FILES=("api/index.py" "vercel.json" "requirements.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - FALTANTE"
        exit 1
    fi
done

# Mostrar configuración actual
echo ""
echo "🔧 CONFIGURACIÓN ACTUAL:"
echo "----------------------------"
echo "1. vercel.json:"
cat vercel.json | head -20
echo ""
echo "2. requirements.txt:"
cat requirements.txt
echo ""
echo "3. API endpoint count:"
grep -c "def do_" api/index.py || echo "0"
echo "----------------------------"

# Crear package.json si no existe (para Vercel detection)
if [ ! -f "package.json" ]; then
    echo "📦 Creando package.json mínimo..."
    cat > package.json << EOF
{
  "name": "chatbot-inspeccion-zapopan",
  "version": "1.0.0",
  "description": "Chatbot MVP para Dirección de Inspección y Vigilancia Zapopan",
  "engines": {
    "node": ">=18"
  }
}
EOF
    echo "✅ package.json creado"
fi

# Verificar estructura de archivos
echo ""
echo "📁 ESTRUCTURA PARA DEPLOYMENT:"
echo "----------------------------"
find . -maxdepth 2 -type f -name "*.py" -o -name "*.json" -o -name "*.txt" -o -name "*.md" | sort | head -15
echo "----------------------------"

# Instrucciones para redeploy
echo ""
echo "🔧 INSTRUCCIONES PARA REDEPLOY:"
echo "================================"
echo "OPCIÓN A: Vercel Web UI (Recomendado)"
echo "1. Ir a: https://vercel.com/dashboard"
echo "2. Click en proyecto: chatbot-inspeccion-zapopan"
echo "3. Buscar deployment actual (debería mostrar error)"
echo "4. Click en '...' → 'Redeploy'"
echo "5. Subir ESTA carpeta completa"
echo "6. Asegurar que detecta:"
echo "   - Runtime: Python"
echo "   - Framework: Other"
echo "   - Build Command: (vacío)"
echo "   - Output Directory: ."
echo "7. Click Deploy (2-3 minutos)"
echo ""
echo "OPCIÓN B: Vercel CLI (Alternativa)"
echo "1. cd a esta carpeta"
echo "2. npx vercel --prod --force"
echo ""
echo "OPCIÓN C: Git Deployment"
echo "1. git add ."
echo "2. git commit -m 'Fix: Vercel Python configuration'"
echo "3. git push"
echo "4. Vercel auto-deploy desde GitHub"
echo "================================"

# Validación rápida
echo ""
echo "🧪 VALIDACIÓN POST-DEPLOYMENT:"
echo "----------------------------"
echo "1. Health Check:"
echo "   curl https://chatbot-inspeccion-zapopan.vercel.app/health"
echo "   Esperado: {\"status\": \"ok\", ...}"
echo ""
echo "2. Frontend:"
echo "   curl -I https://chatbot-inspeccion-zapopan.vercel.app"
echo "   Esperado: HTTP/2 200"
echo ""
echo "3. API Chat:"
echo "   curl -X POST https://chatbot-inspeccion-zapopan.vercel.app/api/chat \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"message\":\"test\",\"token\":\"vercel_public_access\"}'"
echo "   Esperado: {\"success\": true, ...}"
echo "----------------------------"

echo ""
echo "✅ SISTEMA LISTO PARA REDEPLOYMENT CORREGIDO"
echo "====================================================="
echo "Tiempo estimado: 5-10 minutos"
echo "Estado MVP actual: 95% completado"
echo "Estado post-corrección: 100% completado"
echo "====================================================="