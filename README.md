# Agendo - De chat a cita en segundos

Una aplicación MVP web-first para convertir conversaciones de WhatsApp en citas automáticamente, usando Twilio WhatsApp Business API.

## 🚀 Características

- **Landing Page**: Página principal con branding Agendo y CTAs para pruebas rápidas
- **WhatsApp Integration**: Webhook que responde automáticamente a mensajes
- **Test Dashboard**: Interfaz para enviar mensajes de prueba
- **Twilio Sandbox**: Integración completa con Twilio WhatsApp sandbox

## 📋 Requisitos Previos

- Node.js 18+ 
- Cuenta de Twilio con WhatsApp Sandbox configurado
- npm o yarn

## ⚙️ Configuración

### 1. Clonar e instalar dependencias

```bash
git clone <tu-repo>
cd agendo
npm install
```

### 2. Configurar variables de entorno

Crea un archivo `.env.local` en la raíz del proyecto:

```env
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_SANDBOX_NUMBER=14155238886
TWILIO_SANDBOX_CODE=your_sandbox_code
PUBLIC_WEBHOOK_URL=https://tu-dominio.vercel.app/api/whatsapp/webhook
```

### 3. Configurar Twilio WhatsApp Sandbox

1. Ve a la [Consola de Twilio](https://console.twilio.com/)
2. Navega a **Messaging > Try it out > Send a WhatsApp message**
3. Sigue las instrucciones para unirte al sandbox
4. Obtén tus credenciales y código del sandbox

### 4. Ejecutar en desarrollo

```bash
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000) para ver la aplicación.

## 🌐 Deploy en Vercel

### 1. Deploy automático

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/tu-usuario/agendo)

### 2. Deploy manual

```bash
npm install -g vercel
vercel
```

### 3. Configurar variables de entorno en Vercel

En tu dashboard de Vercel, ve a Settings > Environment Variables y agrega:

- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN` 
- `TWILIO_WHATSAPP_FROM`
- `TWILIO_SANDBOX_NUMBER`
- `TWILIO_SANDBOX_CODE`
- `PUBLIC_WEBHOOK_URL` (tu dominio de Vercel + `/api/whatsapp/webhook`)

### 4. Configurar webhook en Twilio

En la consola de Twilio, configura el webhook URL:
```
https://tu-dominio.vercel.app/api/whatsapp/webhook
```

## 🧪 Pruebas

### Probar el webhook (30 segundos)

1. Ve a tu aplicación desplegada
2. Haz clic en **"Probar ya"**
3. Se abrirá WhatsApp con el mensaje pre-escrito `join <código>`
4. Envía el mensaje
5. Deberías recibir "Recibido ✅" como respuesta

### Probar envío de mensajes

1. Ve a `/dashboard` en tu aplicación
2. Ingresa tu número de WhatsApp (con código de país)
3. Escribe un mensaje de prueba
4. Haz clic en **"Enviar Prueba"**
5. Deberías recibir el mensaje en WhatsApp

## 📡 API Endpoints

### Webhook de WhatsApp
```
POST /api/whatsapp/webhook
Content-Type: application/x-www-form-urlencoded
```

Recibe webhooks de Twilio y responde automáticamente con "Recibido ✅".

### Enviar Mensaje
```
POST /api/whatsapp/send
Content-Type: application/json

{
  "to": "+1234567890",
  "body": "Tu mensaje aquí"
}
```

### Ejemplos con cURL

#### Enviar mensaje de prueba:
```bash
curl -X POST https://tu-dominio.vercel.app/api/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "body": "Mensaje de prueba desde cURL"
  }'
```

#### Probar webhook (simulación):
```bash
curl -X POST https://tu-dominio.vercel.app/api/whatsapp/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp%3A%2B1234567890&Body=Hola&MessageSid=test123"
```

## 🏗️ Estructura del Proyecto

```
src/
├── app/
│   ├── api/
│   │   └── whatsapp/
│   │       ├── webhook/route.ts    # Webhook para recibir mensajes
│   │       └── send/route.ts       # API para enviar mensajes
│   ├── connect/page.tsx            # Página placeholder para conectar número
│   ├── dashboard/page.tsx          # Dashboard de pruebas
│   ├── layout.tsx                  # Layout principal
│   └── page.tsx                    # Landing page
```

## 🔍 Logging y Debug

Los logs incluyen un `requestId` único para rastrear cada operación:

```
[abc123] Webhook received
[abc123] Body: From=whatsapp%3A%2B1234567890&Body=test
[abc123] Echo reply sent. Message SID: SMxxxxx
```

## ✅ Acceptance Criteria

- ✅ Enviar "join \<code\>" al Sandbox → webhook registra y responde "Recibido ✅"
- ✅ Desde `/dashboard`, enviar mensaje de prueba con 200 OK
- ✅ README con setup, env y curl de prueba
- ✅ 200 OK inmediato en webhook
- ✅ Logging básico con request_id

## 🛠️ Stack Tecnológico

- **Frontend**: Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **Backend**: Next.js API Routes
- **WhatsApp**: Twilio WhatsApp Business API
- **Deploy**: Vercel
- **Styling**: Tailwind CSS with dark mode support

## 📝 Notas de Desarrollo

- El webhook responde 200 OK inmediatamente y procesa el mensaje de forma asíncrona
- Validación de firma de Twilio para seguridad
- Interfaz responsive con soporte para modo oscuro
- Manejo de errores robusto con logging detallado

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.
