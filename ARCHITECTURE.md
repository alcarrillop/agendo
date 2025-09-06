# Awendo Architecture Documentation

## 🏗️ Project Structure

```
agendo/
├── backend/                     # Python FastAPI Backend
│   ├── app/
│   │   ├── agents/             # LangGraph conversational agents
│   │   │   └── conversation_agent.py
│   │   ├── api/                # REST API endpoints
│   │   │   ├── agent.py        # Agent configuration APIs
│   │   │   ├── evolution.py    # WhatsApp Evolution API
│   │   │   └── webhooks.py     # Webhook handlers
│   │   ├── core/               # Core configuration
│   │   │   └── config.py
│   │   ├── database/           # Database connection & models
│   │   │   └── connection.py
│   │   ├── models/             # SQLAlchemy models
│   │   │   └── database.py
│   │   ├── services/           # External service integrations
│   │   │   ├── calendar_service.py    # Google Calendar
│   │   │   └── evolution_service.py   # Evolution API
│   │   └── main.py             # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── run_dev.py             # Development server
│   └── .env.example           # Environment variables template
│
├── frontend/                   # Next.js Frontend
│   ├── src/app/
│   │   ├── api/               # Legacy APIs (being phased out)
│   │   ├── connect/           # WhatsApp connection page
│   │   ├── dashboard/         # Test dashboard
│   │   ├── setup/             # Agent configuration wizard
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Landing page
│   ├── public/                # Static assets
│   ├── package.json           # Node.js dependencies
│   └── .env.example           # Environment variables template
│
├── setup.py                   # Project setup script
└── README.md                  # Project documentation
```

## 🔄 Data Flow

### 1. WhatsApp Message Flow
```
Customer WhatsApp Message
    ↓
Evolution API
    ↓ (webhook)
Backend: /api/v1/webhooks/evolution
    ↓
LangGraph Conversation Agent
    ↓
Agent Response + Actions
    ↓
Evolution API (send message)
    ↓
Customer WhatsApp
```

### 2. Setup Flow
```
Frontend Setup Wizard
    ↓
1. Connect WhatsApp (Evolution API)
    ↓
2. Connect Google Calendar (OAuth)
    ↓
3. Configure Agent Behavior
    ↓
Backend: Save Configuration
    ↓
Agent Ready to Handle Messages
```

## 🤖 LangGraph Agent Workflow

The conversational agent uses a sophisticated LangGraph workflow:

```
Incoming Message
    ↓
Check Working Hours
    ├─ Within Hours → Detect Intent
    └─ Outside Hours → Out-of-Hours Message
                ↓
        Intent Detection (LLM)
        ├─ Greeting → Handle Greeting
        ├─ Booking → Handle Booking
        ├─ Info → Handle Info Request
        └─ Unknown → Handle Unknown
                ↓
        Generate Response
                ↓
        [Optional] Book Appointment
                ↓
        Send Response to Customer
```

## 🗄️ Database Schema

### Core Tables

**instances**
- Stores WhatsApp instances from Evolution API
- Tracks connection status and metadata

**agent_configs**
- Agent behavior and personality settings
- Business context and working hours
- Google Calendar integration tokens

**conversations**
- Customer conversation threads
- Conversation state and context

**messages**
- Individual messages within conversations
- Both incoming and outgoing messages

**calendar_events**
- Appointments booked through the agent
- Links to Google Calendar events

## 🔌 External Integrations

### Evolution API (WhatsApp)
- **Purpose**: Direct WhatsApp integration without Meta dependency
- **Endpoints**: Instance management, message sending, webhooks
- **Authentication**: API key-based

### Google Calendar API
- **Purpose**: Automatic appointment booking
- **Authentication**: OAuth 2.0 with refresh tokens
- **Scopes**: Calendar read/write, user profile

### OpenAI API
- **Purpose**: Powers the LangGraph conversational agent
- **Model**: GPT-4o-mini for cost efficiency
- **Usage**: Intent detection, response generation

### Supabase (PostgreSQL)
- **Purpose**: Primary database for all application data
- **Features**: Real-time subscriptions, row-level security
- **Connection**: SQLAlchemy with async support

## 🔐 Security Considerations

### Authentication & Authorization
- Google OAuth 2.0 for calendar access
- Evolution API key authentication
- Supabase service role key for database access

### Data Protection
- Sensitive tokens stored encrypted in database
- Environment variables for all secrets
- CORS configured for frontend-only access

### Webhook Security
- Webhook signature verification (when available)
- Request ID tracking for audit trails
- Background processing to prevent timeouts

## 🚀 Deployment Architecture

### Development
```
localhost:3000 (Frontend) ←→ localhost:8000 (Backend)
                                    ↓
                            External Services:
                            - Evolution API
                            - Supabase
                            - Google Calendar
                            - OpenAI
```

### Production
```
Vercel/Netlify (Frontend) ←→ Railway/Render (Backend)
                                    ↓
                            External Services:
                            - Evolution API (Self-hosted)
                            - Supabase (Managed)
                            - Google Calendar (Google Cloud)
                            - OpenAI (OpenAI Platform)
```

## 📊 Performance Considerations

### Backend Optimizations
- Async/await throughout the application
- Background task processing for webhooks
- Connection pooling for database
- Efficient LLM usage with context management

### Frontend Optimizations
- Next.js App Router for optimal performance
- Client-side state management
- Optimistic UI updates
- Proper error boundaries

### Scalability
- Stateless backend design
- Database-backed conversation state
- Horizontal scaling ready
- Rate limiting for external APIs

## 🔧 Development Workflow

### Backend Development
```bash
cd backend
python run_dev.py  # Auto-reload enabled
```

### Frontend Development
```bash
cd frontend
npm run dev  # Hot reload enabled
```

### Testing Strategy
- Unit tests for agent logic
- Integration tests for API endpoints
- End-to-end tests for complete workflows
- Mock external services for testing

## 📈 Monitoring & Observability

### Logging
- Structured logging with request IDs
- Different log levels for development/production
- External service call tracking

### Health Checks
- `/health` endpoint for service monitoring
- Database connection checks
- External service availability checks

### Metrics (Future)
- Conversation success rates
- Response times
- Booking conversion rates
- Error rates by endpoint

## 🔮 Future Enhancements

### Technical
- WebSocket support for real-time updates
- Redis caching for frequently accessed data
- Message queuing for high-volume scenarios
- Multi-language support

### Features
- Advanced conversation analytics
- Customer satisfaction tracking
- Integration with CRM systems
- Voice message support
- Image/document handling

### Business
- Multi-tenant architecture
- White-label solutions
- Advanced reporting dashboard
- API rate limiting and billing
