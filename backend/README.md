# 🚀 Agendo Backend

FastAPI backend con sistema automático de gestión de webhooks para WhatsApp.

## 📦 Gestión de Dependencias (UV)

Este proyecto usa **UV** para gestión de dependencias. **No usamos** `requirements.txt`, `pip`, ni `virtualenv`.

### 🔧 Comandos Principales

```bash
# Instalar todas las dependencias
uv sync

# Agregar nueva dependencia
uv add nombre-paquete

# Agregar dependencia de desarrollo
uv add --dev nombre-paquete

# Ejecutar el servidor
uv run python run_dev.py

# Ejecutar cualquier script
uv run python script.py

# Actualizar dependencias
uv lock --upgrade
```

### 📁 Archivos de Dependencias

- **`pyproject.toml`** - Define las dependencias del proyecto
- **`uv.lock`** - Lock file con versiones exactas (como package-lock.json)
- **NO** usamos `requirements.txt`

## 🚀 Inicio Rápido

```bash
# 1. Clonar y entrar al directorio
cd backend

# 2. Instalar dependencias
uv sync

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 4. Ejecutar servidor
uv run python run_dev.py
```

## 🌐 URLs Importantes

- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Webhook Status**: http://localhost:8000/api/v1/webhooks/status

## 🔧 Configuración

### Variables de Entorno Requeridas

```bash
# Base de datos (Supabase)
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Evolution API (WhatsApp)
EVOLUTION_API_URL=your-evolution-api-url
EVOLUTION_API_KEY=your-evolution-api-key

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Google Calendar
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Webhook (para ngrok)
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.app
```

## 🏗️ Estructura del Proyecto

```
backend/
├── app/
│   ├── agents/          # Agentes conversacionales
│   ├── api/            # Endpoints REST
│   ├── core/           # Configuración
│   ├── database/       # Conexión a BD
│   ├── models/         # Modelos de datos
│   └── services/       # Servicios de negocio
├── pyproject.toml      # Dependencias
├── uv.lock            # Lock file
└── run_dev.py         # Script de desarrollo
```

## 🛠️ Desarrollo

### Agregar Nueva Dependencia

```bash
# Dependencia principal
uv add fastapi

# Dependencia de desarrollo
uv add --dev pytest

# Dependencia específica de versión
uv add "fastapi>=0.104.0"
```

### Ejecutar Tests

```bash
uv run pytest
```

### Formatear Código

```bash
uv run black .
uv run isort .
```

## 🚨 Troubleshooting

### Backend no inicia
```bash
uv sync  # Reinstalar dependencias
uv run python run_dev.py
```

### Dependencias desactualizadas
```bash
uv lock --upgrade
uv sync
```

### Problemas con UV
```bash
# Reinstalar UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verificar instalación
uv --version
```

## 📚 Más Información

- [Documentación UV](https://docs.astral.sh/uv/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

---

**Nota**: Este proyecto NO usa `requirements.txt`, `pip`, ni `virtualenv`. Todo se gestiona con UV para mayor velocidad y confiabilidad.
