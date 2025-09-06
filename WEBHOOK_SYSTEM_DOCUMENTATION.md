# 📚 Sistema Automático de Webhooks - Agendo

## 🎯 Resumen

He implementado un sistema completo y automático para la gestión de webhooks en tu aplicación Agendo. Este sistema elimina la necesidad de configurar manualmente las URLs de webhook cada vez que cambias la configuración, especialmente cuando usas ngrok para desarrollo.

## 🚀 Características Principales

### ✅ **Actualización Automática al Iniciar**
- El backend verifica y actualiza automáticamente todos los webhooks al iniciar
- No necesitas configurar manualmente nada después de cambiar tu `.env`

### ✅ **Monitoreo de Cambios en .env**
- Detecta automáticamente cuando cambias la variable `WEBHOOK_BASE_URL` en tu archivo `.env`
- Actualiza instantáneamente los webhooks en Evolution API

### ✅ **API de Gestión Manual**
- Endpoints REST para gestionar webhooks manualmente cuando sea necesario
- Verificación de estado y diagnósticos

### ✅ **Sistema Robusto**
- Manejo de errores y reintentos
- Logs detallados para debugging
- Validación de configuraciones

---

## 🏗️ Arquitectura del Sistema

### **Componentes Principales:**

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA DE WEBHOOKS                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌──────────────────┐               │
│  │   Env Watcher   │───▶│ Webhook Manager  │               │
│  │                 │    │                  │               │
│  │ • Monitorea .env│    │ • Actualiza URLs │               │
│  │ • Detecta cambios│    │ • Valida config  │               │
│  └─────────────────┘    │ • Maneja errores │               │
│                         └──────────────────┘               │
│                                  │                         │
│                                  ▼                         │
│  ┌─────────────────┐    ┌──────────────────┐               │
│  │ Evolution API   │◀───│ HTTP Client      │               │
│  │                 │    │                  │               │
│  │ • Recibe updates│    │ • Envía requests │               │
│  │ • Actualiza URLs│    │ • Maneja auth    │               │
│  └─────────────────┘    └──────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Archivos Implementados

### **1. `backend/app/services/webhook_manager.py`**
**Función**: Servicio principal para gestión de webhooks

**Características**:
- ✅ Actualización automática de webhooks
- ✅ Validación de configuraciones
- ✅ Manejo de múltiples instancias
- ✅ Sistema de reintentos
- ✅ Logs detallados

**Métodos principales**:
```python
async def update_all_webhooks(db: AsyncSession) -> Dict[str, Any]
async def on_settings_change(db: AsyncSession) -> None
async def get_current_webhook_url() -> Optional[str]
```

### **2. `backend/app/services/env_watcher.py`**
**Función**: Monitor de cambios en archivo `.env`

**Características**:
- ✅ Detección automática de cambios en `.env`
- ✅ Actualización instantánea de webhooks
- ✅ Sistema de debounce para evitar múltiples actualizaciones
- ✅ Manejo de errores robusto

**Funcionalidades**:
```python
async def start_env_watcher() -> None
async def stop_env_watcher() -> None
class EnvFileHandler(FileSystemEventHandler)
```

### **3. `backend/app/api/webhook_management.py`**
**Función**: Endpoints REST para gestión manual

**Endpoints disponibles**:
```http
GET  /api/v1/webhooks/status          # Ver estado actual
POST /api/v1/webhooks/update          # Actualizar webhooks
POST /api/v1/webhooks/validate        # Validar configuración
```

### **4. Modificaciones en `backend/app/main.py`**
**Función**: Integración con el ciclo de vida de la aplicación

**Cambios realizados**:
- ✅ Inicialización automática de webhooks al startup
- ✅ Activación del monitor de archivos
- ✅ Limpieza apropiada al shutdown
- ✅ Manejo de errores durante inicialización

---

## 🔧 Configuración y Uso

### **1. Variables de Entorno**

Agrega en tu archivo `backend/.env`:

```bash
# URL base para webhooks (se actualiza automáticamente)
WEBHOOK_BASE_URL=https://tu-ngrok-url.ngrok.app

# Configuración de Evolution API
EVOLUTION_API_URL=https://n8n-evolution-api.stlwni.easypanel.host
EVOLUTION_API_KEY=F6ECDD08-1DC2-4A47-9241-7D8941E2E235
```

### **2. Flujo Automático**

1. **Al iniciar el backend**:
   ```bash
   cd backend && source .venv/bin/activate && python run_dev.py
   ```
   
2. **El sistema automáticamente**:
   - 🔍 Lee la configuración actual
   - 🔄 Actualiza todos los webhooks en Evolution API
   - 👀 Inicia el monitor de archivos
   - ✅ Confirma que todo esté funcionando

3. **Cuando cambies el .env**:
   - 📝 Editas `WEBHOOK_BASE_URL=https://nueva-url.ngrok.app`
   - 🚀 El sistema detecta el cambio automáticamente
   - 🔄 Actualiza los webhooks sin reiniciar
   - ✅ Logs confirman la actualización

### **3. Gestión Manual (Opcional)**

Si necesitas control manual, puedes usar los endpoints:

```bash
# Ver estado actual
curl http://localhost:8000/api/v1/webhooks/status

# Forzar actualización
curl -X POST http://localhost:8000/api/v1/webhooks/update \\
  -H "Content-Type: application/json" \\
  -d '{}'

# Actualizar instancia específica
curl -X POST http://localhost:8000/api/v1/webhooks/update \\
  -H "Content-Type: application/json" \\
  -d '{"instance_name": "TENANT_8d7dckoinva"}'
```

---

## 🛠️ Dependencias Agregadas

### **Nuevas dependencias agregadas**:
```
watchdog>=3.0.0  # Para monitoreo de archivos
```

**Instalación**:
```bash
cd backend && uv add watchdog
```

### **Gestión de Dependencias con UV**:
- **Agregar**: `uv add paquete`
- **Instalar**: `uv sync`
- **Ejecutar**: `uv run python script.py`
- **Actualizar**: `uv lock --upgrade`

---

## 📊 Logs y Debugging

### **Logs del Sistema**

El sistema genera logs detallados para debugging:

```
🚀 Starting Awendo Backend...
✅ Database initialized successfully
🔄 Initializing webhooks...
✅ Webhook updated for instance: TENANT_8d7dckoinva
👀 Environment file watcher started
🎉 Awendo Backend started successfully!
```

### **Logs de Cambios**

Cuando detecta cambios:
```
📁 Environment file changed: .env
🔄 Updating webhooks due to settings change...
✅ All webhooks updated successfully
```

### **Logs de Errores**

En caso de problemas:
```
❌ Failed to update webhook for TENANT_8d7dckoinva: HTTP 400
🔄 Retrying in 5 seconds... (attempt 1/3)
```

---

## 🔒 Seguridad y Mejores Prácticas

### **✅ Implementado:**
- Validación de configuraciones antes de actualizar
- Manejo seguro de API keys
- Sistema de reintentos con backoff
- Logs que no exponen información sensible

### **🛡️ Recomendaciones:**
- Mantén tu `.env` fuera del control de versiones
- Usa URLs HTTPS para webhooks en producción
- Configura ngrok con dominio fijo para desarrollo estable

---

## 🚨 Troubleshooting

### **Problema**: Webhooks no se actualizan automáticamente
**Solución**:
1. Verifica que `watchdog` esté instalado: `uv list | grep watchdog`
2. Revisa los logs del backend para errores
3. Usa el endpoint manual: `POST /api/v1/webhooks/update`

### **Problema**: Error "HTTP 400" al actualizar webhook
**Solución**:
1. Verifica que `EVOLUTION_API_KEY` sea correcta
2. Confirma que la URL de webhook sea accesible
3. Revisa que la instancia exista en Evolution API

### **Problema**: Monitor de archivos no funciona
**Solución**:
1. El sistema funciona sin el monitor (solo no será automático)
2. Verifica permisos de lectura en el directorio
3. Usa gestión manual mientras tanto

---

## 🎯 Beneficios del Sistema

### **Para Desarrollo:**
- 🚀 **Cero configuración manual** después del setup inicial
- ⚡ **Detección instantánea** de cambios en configuración
- 🔄 **Actualización automática** sin reiniciar servicios
- 📝 **Logs claros** para debugging

### **Para Producción:**
- 🛡️ **Sistema robusto** con manejo de errores
- 🔄 **Reintentos automáticos** en caso de fallas
- 📊 **Monitoreo** del estado de webhooks
- 🎯 **API REST** para integración con otros sistemas

---

## 📈 Próximos Pasos (Opcional)

### **Mejoras Futuras Posibles:**
1. **Dashboard Web**: Interfaz gráfica para gestión de webhooks
2. **Notificaciones**: Alerts cuando fallan las actualizaciones
3. **Múltiples Entornos**: Configuración diferente para dev/prod
4. **Backup de Configuraciones**: Historial de cambios

---

## ✅ Resumen de Limpieza Realizada

### **Archivos Eliminados:**
- ❌ `backend/clean_all.py` - Script de limpieza obsoleto
- ❌ `backend/clean_fresh.py` - Script de limpieza obsoleto  
- ❌ `backend/nuclear_cleanup.py` - Script de limpieza obsoleto
- ❌ `backend/configure_supabase.py` - Configuración obsoleta
- ❌ `backend/env_supabase_template.txt` - Template obsoleto

### **Código Limpiado:**
- ✅ Imports no utilizados en `webhooks.py`
- ✅ URL hardcodeada removida de `instance_service.py`
- ✅ Dependencias organizadas y documentadas

### **Estructura Final Limpia:**
```
backend/
├── app/
│   ├── agents/           # Agentes conversacionales
│   ├── api/             # Endpoints REST
│   ├── core/            # Configuración central
│   ├── database/        # Conexión a BD
│   ├── models/          # Modelos de datos
│   └── services/        # Servicios de negocio
├── requirements.txt     # Dependencias
├── run_dev.py          # Script de desarrollo
└── uv.lock             # Lock de dependencias
```

---

## 🎉 ¡Sistema Listo!

Tu backend ahora tiene un sistema completamente automático de gestión de webhooks. **No necesitas hacer nada más** - simplemente:

1. **Cambia la URL en tu `.env`** cuando sea necesario
2. **El sistema se encarga del resto** automáticamente
3. **Monitorea los logs** para confirmar que todo funciona
4. **Usa los endpoints manuales** si necesitas control adicional

**¡Tu flujo de desarrollo ahora es mucho más eficiente! 🚀**
