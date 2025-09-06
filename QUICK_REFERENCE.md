# 🚀 Agendo - Referencia Rápida

## 📋 Comandos Esenciales

### **Levantar Todos los Servicios**
```bash
# Terminal 1: Backend
cd backend && source .venv/bin/activate && python run_dev.py

# Terminal 2: Frontend  
cd frontend && npm run dev

# Terminal 3: Ngrok
ngrok http 8000
```

### **Actualizar Webhook URL**
```bash
# Opción 1: Automática (Recomendada)
# Solo edita backend/.env:
WEBHOOK_BASE_URL=https://nueva-url.ngrok.app

# Opción 2: Manual
curl -X POST http://localhost:8000/api/v1/webhooks/update
```

## 🔗 URLs Importantes

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000  
- **API Docs**: http://localhost:8000/docs
- **Ngrok Dashboard**: http://localhost:4040
- **Health Check**: http://localhost:8000/health

## 📊 Verificar Estado

### **Webhook Status**
```bash
curl http://localhost:8000/api/v1/webhooks/status
```

### **Probar Webhook**
```bash
curl -X POST http://localhost:8000/api/v1/webhooks/evolution \
  -H "Content-Type: application/json" \
  -d '{"event": "messages.upsert", "instance": "TENANT_8d7dckoinva", "data": {"messages": [{"key": {"remoteJid": "test@s.whatsapp.net", "fromMe": false}, "message": {"conversation": "test"}}]}}'
```

## 🛠️ Troubleshooting

### **Backend no inicia**
```bash
cd backend
uv sync  # Instala dependencias desde pyproject.toml
uv run python run_dev.py
```

### **Webhook no actualiza**
1. Verifica `.env` tiene `WEBHOOK_BASE_URL`
2. Revisa logs del backend
3. Usa actualización manual: `POST /api/v1/webhooks/update`

### **Mensajes no llegan**
1. Verifica ngrok esté corriendo
2. Confirma webhook URL en Evolution API
3. Revisa logs del backend para errores

## 📁 Archivos Clave

- **Configuración**: `backend/.env`
- **Logs**: Terminal del backend
- **Documentación**: `WEBHOOK_SYSTEM_DOCUMENTATION.md`
- **Base de datos**: `backend/agendo.db`

## 🎯 Flujo de Desarrollo

1. **Iniciar servicios** con los comandos de arriba
2. **Cambiar ngrok URL** en `backend/.env` cuando sea necesario
3. **El sistema actualiza webhooks** automáticamente
4. **Probar enviando mensajes** desde WhatsApp
5. **Revisar logs** para debugging

## ✅ Todo Funciona Cuando...

- ✅ Backend responde en http://localhost:8000/health
- ✅ Frontend carga en http://localhost:3000
- ✅ Ngrok muestra URL pública activa
- ✅ Webhook status muestra "configured"
- ✅ Mensajes de WhatsApp generan respuestas del agente
