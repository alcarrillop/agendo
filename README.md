# Awendo - Conversational WhatsApp Agent

A modern, intelligent WhatsApp conversational agent that automatically handles customer interactions and books appointments through Google Calendar integration.

## 🏗️ Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Frontend Web      │    │   Backend Python     │    │   Evolution API     │
│   (Next.js/TS)      │    │   (FastAPI+LangGraph)│    │   (WhatsApp)        │
├─────────────────────┤    ├──────────────────────┤    ├─────────────────────┤
│ • Landing Page      │    │ • Agent Logic        │    │ • WhatsApp Gateway  │
│ • Setup Wizard      │    │ • LangGraph Workflow │    │ • Message Routing   │
│ • Config Interface  │    │ • Context Management │    │ • QR Code Gen       │
│ • Google Calendar   │    │ • Calendar Booking   │    │                     │
│                     │    │ • Conversation State │    │                     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
         │                           │                           │
         └───── HTTP API ────────────┼──── Webhooks ─────────────┘
                                     │
                              ┌──────────────┐
                              │ Supabase     │
                              │ (PostgreSQL) │
                              │ • Configs    │
                              │ • Chats      │
                              │ • Users      │
                              └──────────────┘
```

## 🚀 Features

- **🏠 Modern Web Interface**: Clean setup wizard and configuration interface
- **📱 WhatsApp Integration**: Direct connection via Evolution API (no Meta dependency)
- **🤖 Intelligent Agent**: LangGraph-powered conversational AI with context awareness
- **📅 Calendar Integration**: Automatic appointment booking with Google Calendar
- **💾 Persistent Storage**: Supabase PostgreSQL for reliable data management
- **🕒 Business Hours**: Respects configured working hours
- **🔄 Real-time Processing**: Instant message processing and responses
- **📊 Conversation Tracking**: Full conversation history and analytics

## 📋 Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 18+** (for frontend)
- **Evolution API instance** (WhatsApp integration)
- **Supabase project** (database)
- **Google Cloud Project** (Calendar API)
- **OpenAI API key** (for conversational AI)

## ⚙️ Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <your-repo>
cd agendo

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
```

### 2. Configure Backend Environment

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database (Supabase)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Evolution API (WhatsApp)
EVOLUTION_API_URL=https://your-evolution-api-url.com
EVOLUTION_API_KEY=your-evolution-api-key

# Google Calendar
GOOGLE_CLIENT_ID=your-google-client-id.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OpenAI (for conversational AI)
OPENAI_API_KEY=sk-your-openai-api-key
```

### 3. Configure Frontend Environment

```bash
cd frontend
cp .env.example .env.local
```

Edit `.env.local`:

```env
# Backend API URL
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Google Calendar (same as backend)
GOOGLE_CLIENT_ID=your-google-client-id.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 4. Set Up External Services

#### Supabase Database
1. Create a [Supabase project](https://supabase.com)
2. Get your project URL and service role key
3. The backend will automatically create tables on first run

#### Evolution API
1. Deploy an [Evolution API](https://github.com/EvolutionAPI/evolution-api) instance
2. Configure webhook URL: `http://your-backend-url/api/v1/webhooks/evolution`
3. Get your API URL and key

#### Google Calendar API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project and enable Calendar API
3. Create OAuth 2.0 credentials:
   - Type: Web Application
   - Authorized redirect URIs: `http://localhost:8000/api/v1/auth/google/callback`

#### OpenAI API
1. Get your API key from [OpenAI Platform](https://platform.openai.com/)
2. Ensure you have credits/billing set up

### 5. Run the Application

Start both backend and frontend in separate terminals:

```bash
# Terminal 1: Backend
cd backend
python run_dev.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🧪 How to Use

### Complete Setup Flow (3 minutes)

1. **Open the frontend**: Go to http://localhost:3000
2. **Connect WhatsApp**: Click "Conectar tu número" → Scan QR code
3. **Connect Google Calendar**: Authorize your Google account
4. **Configure your agent**:
   - Agent name and personality
   - Business description
   - Working hours
5. **Activate your agent**: Save configuration

### Test the Conversational Agent

Once configured, customers can message your WhatsApp and the agent will:

- **Greet customers** with personalized messages
- **Answer business questions** based on your configuration
- **Schedule appointments** automatically in Google Calendar
- **Check availability** in real-time
- **Respect business hours** and send appropriate out-of-hours messages

#### Example Conversation:

```
Customer: "Hi, I want to schedule an appointment"
Agent: "Hello! I'm Sofia from [Your Business]. I'd be happy to help you schedule an appointment. What date and time work best for you? Please use DD/MM/YYYY and HH:MM format."

Customer: "Tomorrow at 2:00 PM"
Agent: "Perfect! I have availability tomorrow at 2:00 PM. Could you please confirm your full name for the appointment?"

Customer: "John Smith"
Agent: "✅ Appointment confirmed for John Smith tomorrow at 2:00 PM. You'll receive a calendar invitation shortly. See you then!"
```

## 📡 API Endpoints

### Webhook Endpoints
- `POST /api/v1/webhooks/evolution` - Evolution API webhook
- `GET /api/v1/webhooks/evolution/test` - Test webhook connectivity

### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/v1/status` - Detailed API status

## 🛠️ Development

### Backend Development

```bash
cd backend

# Run with auto-reload
python run_dev.py

# Run tests (when implemented)
pytest

# Code formatting
black app/
flake8 app/
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Linting
npm run lint
```

## 📊 Database Schema

The application uses the following main tables:

- **instances**: WhatsApp instances and connection status
- **agent_configs**: Agent configuration and behavior settings
- **conversations**: Customer conversation threads
- **messages**: Individual messages within conversations
- **calendar_events**: Booked appointments and calendar events

## 🔧 Configuration

### Agent Behavior

The conversational agent can be configured with:

- **Agent Name**: How the agent introduces itself
- **Business Purpose**: What your business does
- **Agent Behavior**: Personality and response style
- **Working Hours**: When the agent should be active
- **Google Calendar**: For automatic appointment booking

### LangGraph Workflow

The agent uses a sophisticated workflow:

1. **Working Hours Check**: Ensures responses during business hours
2. **Intent Detection**: Understands customer intent (greeting, booking, info)
3. **Context Management**: Maintains conversation context
4. **Response Generation**: Creates appropriate responses
5. **Action Execution**: Books appointments when needed

## 🚀 Deployment

### Backend Deployment

The backend can be deployed to any Python hosting service:

- **Railway/Render**: Easy deployment with git integration
- **Docker**: Use the provided Dockerfile (when created)
- **VPS**: Direct deployment with systemd service

### Frontend Deployment

Deploy the Next.js frontend to:

- **Vercel**: Seamless deployment with git integration
- **Netlify**: Static site deployment
- **Your own hosting**: Build and serve static files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the [API documentation](http://localhost:8000/docs) when running locally
2. Review the logs in both frontend and backend
3. Ensure all environment variables are properly configured
4. Verify external service connections (Evolution API, Supabase, Google Calendar)

---

**Built with ❤️ using FastAPI, LangGraph, Next.js, and Supabase**