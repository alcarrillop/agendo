'use client';

import Link from "next/link";
import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";

interface AgentConfig {
  instanceName: string;
  googleCalendarConnected: boolean;
  agentName: string;
  agentPurpose: string;
  agentBehavior: string;
  businessContext: string;
  faqs: FAQ[];
  workingHours: {
    enabled: boolean;
    start: string;
    end: string;
    timezone: string;
  };
}

interface FAQ {
  id: string;
  question: string;
  answer: string;
}

export default function SetupPage() {
  const searchParams = useSearchParams();
  const instanceName = searchParams.get('instance') || '';
  const startStep = searchParams.get('step') === 'calendar' ? 1 : 1;
  
  const [currentStep, setCurrentStep] = useState(startStep);
  const [config, setConfig] = useState<AgentConfig>({
    instanceName,
    googleCalendarConnected: false,
    agentName: '',
    agentPurpose: '',
    agentBehavior: '',
    businessContext: '',
    faqs: [],
    workingHours: {
      enabled: true,
      start: '09:00',
      end: '18:00',
      timezone: 'America/Bogota'
    }
  });

  const [googleAuthLoading, setGoogleAuthLoading] = useState(false);
  const [connectedGoogleEmail, setConnectedGoogleEmail] = useState<string>('');

  const [newFAQ, setNewFAQ] = useState({ question: '', answer: '' });

  // Verificar si Google Calendar está conectado al cargar
  useEffect(() => {
    const calendarSuccess = searchParams.get('calendar_success');
    const userEmail = searchParams.get('user_email');
    const userName = searchParams.get('user_name');
    const error = searchParams.get('error');
    const errorMessage = searchParams.get('message');

    if (calendarSuccess === 'true' && userEmail) {
      setConfig(prev => ({ ...prev, googleCalendarConnected: true }));
      setConnectedGoogleEmail(decodeURIComponent(userEmail));
      alert(`🎉 Google Calendar conectado exitosamente!\n\nUsuario: ${userName || 'Usuario'}\nEmail: ${userEmail}`);
      // No cambiar de paso automáticamente, dejar que el usuario continue manualmente
    } else if (error) {
      const errorText = errorMessage || error;
      alert(`❌ Error conectando Google Calendar: ${errorText}`);
    }
  }, [searchParams]);

  const connectGoogleCalendar = async () => {
    if (!instanceName) {
      alert('Instancia no encontrada');
      return;
    }

    setGoogleAuthLoading(true);
    
    try {
      console.log('🔗 Iniciando OAuth con Google Calendar...');
      
      const response = await fetch(`/api/auth/google?instance=${instanceName}`);
      const data = await response.json();

      if (data.success && data.authUrl) {
        console.log('✅ Redirigiendo a Google OAuth...');
        // Redireccionar a Google OAuth
        window.location.href = data.authUrl;
      } else {
        throw new Error(data.error || 'Failed to get authorization URL');
      }
    } catch (error) {
      console.error('❌ Error starting Google OAuth:', error);
      alert('Error al conectar con Google Calendar: ' + (error instanceof Error ? error.message : 'Unknown error'));
      setGoogleAuthLoading(false);
    }
  };

  const skipGoogleCalendar = () => {
    setConfig(prev => ({
      ...prev,
      googleCalendarConnected: true // Marcar como "conectado" para continuar
    }));
    alert('⏭️ Google Calendar omitido. Puedes configurarlo después en producción.');
  };

  const steps = [
    { id: 1, title: 'Google Calendar', icon: '📅' },
    { id: 2, title: 'Contexto del Agente', icon: '🤖' },
    { id: 3, title: 'Configuración Final', icon: '✅' }
  ];

  const addFAQ = () => {
    if (newFAQ.question && newFAQ.answer) {
      const faq: FAQ = {
        id: Date.now().toString(),
        question: newFAQ.question,
        answer: newFAQ.answer
      };
      setConfig(prev => ({
        ...prev,
        faqs: [...prev.faqs, faq]
      }));
      setNewFAQ({ question: '', answer: '' });
    }
  };

  const removeFAQ = (id: string) => {
    setConfig(prev => ({
      ...prev,
      faqs: prev.faqs.filter(faq => faq.id !== id)
    }));
  };

  const saveConfiguration = async () => {
    try {
      // Transform frontend config to backend format
      const backendConfig = {
        business_name: config.agentName || 'Mi Negocio',
        business_description: config.businessContext || config.agentPurpose || 'Servicios profesionales',
        available_hours: {
          monday: { start: config.workingHours.start, end: config.workingHours.end },
          tuesday: { start: config.workingHours.start, end: config.workingHours.end },
          wednesday: { start: config.workingHours.start, end: config.workingHours.end },
          thursday: { start: config.workingHours.start, end: config.workingHours.end },
          friday: { start: config.workingHours.start, end: config.workingHours.end }
        },
        appointment_duration: 60, // Default 1 hour
        buffer_time: 15, // Default 15 minutes buffer
        custom_instructions: config.agentBehavior || 'Sé profesional y útil al agendar citas.',
        greeting_message: `Hola! Soy el asistente de ${config.agentName || 'nuestro negocio'}. ¿En qué puedo ayudarte hoy?`
      };

      console.log('Sending config to backend:', backendConfig);

      // Save configuration to Python backend
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/v1/agent/config`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backendConfig),
      });

      const result = await response.json();

      if (response.ok) {
        console.log('Configuration saved successfully:', result);
        alert('¡Configuración guardada exitosamente! 🎉\n\nTu agente conversacional está activo y listo para recibir mensajes por WhatsApp.');
      } else {
        throw new Error(result.error || 'Failed to save configuration');
      }
    } catch (error) {
      console.error('Error saving configuration:', error);
      alert('Error al guardar la configuración: ' + (error instanceof Error ? error.message : 'Error desconocido'));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation */}
      <nav className="px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-gray-900 dark:text-white">
            Agendo
          </Link>
          <div className="flex gap-4">
            <Link 
              href="/connect"
              className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors"
            >
              Conectar WhatsApp
            </Link>
            <Link 
              href="/dashboard"
              className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors"
            >
              Dashboard
            </Link>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Configurar tu Agente Conversacional
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Instancia: <span className="font-semibold text-blue-600">{instanceName}</span>
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex justify-center mb-8">
          <div className="flex space-x-4 overflow-x-auto pb-2">
            {steps.map((step) => (
              <div
                key={step.id}
                className={`flex items-center space-x-2 px-4 py-2 rounded-full whitespace-nowrap cursor-pointer transition-colors ${
                  step.id === currentStep
                    ? 'bg-blue-600 text-white'
                    : step.id < currentStep
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                }`}
                onClick={() => setCurrentStep(step.id)}
              >
                <span className="text-lg">{step.icon}</span>
                <span className="font-medium">{step.title}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          
          {/* Step 1: Google Calendar */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                📅 Integración con Google Calendar
              </h2>
              
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📅</div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  Conectar Google Calendar
                </h3>
                <p className="text-gray-600 dark:text-gray-300 mb-6">
                  Tu agente necesita acceso a tu calendario para poder agendar citas automáticamente cuando los clientes escriban por WhatsApp.
                </p>
                
                {config.googleCalendarConnected ? (
                  <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-6">
                    <div className="text-green-600 dark:text-green-400 text-4xl mb-2">✅</div>
                    <p className="text-green-800 dark:text-green-200 font-semibold mb-2">
                      Google Calendar conectado exitosamente
                    </p>
                    <p className="text-green-700 dark:text-green-300 text-sm">
                      Cuenta: <strong>{connectedGoogleEmail}</strong>
                    </p>
                    <p className="text-green-700 dark:text-green-300 text-sm mt-2">
                      ✨ Tu agente ahora puede agendar citas automáticamente
                    </p>
                  </div>
                ) : (
                  <div>
                    <button
                      onClick={connectGoogleCalendar}
                      disabled={googleAuthLoading}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-4 px-8 rounded-lg transition-colors inline-flex items-center gap-3 text-lg"
                    >
                      {googleAuthLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                          <span>Conectando...</span>
                        </>
                      ) : (
                        <>
                          <span>🔗</span>
                          <span>Conectar con Google Calendar</span>
                        </>
                      )}
                    </button>
                    
                    <div className="mt-6 text-sm text-gray-600 dark:text-gray-400 max-w-md mx-auto">
                      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                        <p className="mb-2 font-semibold text-blue-800 dark:text-blue-200">🔒 Proceso seguro:</p>
                        <ul className="text-xs space-y-1 text-left text-blue-700 dark:text-blue-300">
                          <li>• Te redirecciona a Google para autorizar</li>
                          <li>• Solo acceso de lectura/escritura a tu calendario</li>
                          <li>• Puedes revocar acceso en cualquier momento</li>
                          <li>• Los datos nunca se almacenan en nuestros servidores</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 2: Agent Configuration */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                🤖 Configuración del Agente
              </h2>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nombre de tu agente/asistente
                </label>
                <input
                  type="text"
                  value={config.agentName}
                  onChange={(e) => setConfig(prev => ({ ...prev, agentName: e.target.value }))}
                  placeholder="Ej: Sofia, María, Dr. López Assistant"
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  ¿Qué tipo de negocio/servicio ofreces?
                </label>
                <textarea
                  value={config.agentPurpose}
                  onChange={(e) => setConfig(prev => ({ ...prev, agentPurpose: e.target.value }))}
                  placeholder="Ej: Consultorio dental especializado en ortodoncia y blanqueamiento. Ofrecemos tratamientos de calidad con tecnología de punta en el centro de Bogotá."
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  ¿Cómo quieres que se comporte tu agente?
                </label>
                <textarea
                  value={config.agentBehavior}
                  onChange={(e) => setConfig(prev => ({ ...prev, agentBehavior: e.target.value }))}
                  placeholder="Ej: Ser amable, profesional y empático. Saludar cordialmente, preguntar el nombre del cliente, y ayudar a agendar citas. No dar diagnósticos médicos, solo información general."
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>

              {/* Working Hours */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                  🕒 Horario de Atención
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                      Hora de inicio
                    </label>
                    <input
                      type="time"
                      value={config.workingHours.start}
                      onChange={(e) => setConfig(prev => ({
                        ...prev,
                        workingHours: { ...prev.workingHours, start: e.target.value }
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-800 dark:text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">
                      Hora de fin
                    </label>
                    <input
                      type="time"
                      value={config.workingHours.end}
                      onChange={(e) => setConfig(prev => ({
                        ...prev,
                        workingHours: { ...prev.workingHours, end: e.target.value }
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-800 dark:text-white"
                    />
                  </div>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  El agente solo responderá durante este horario. Fuera de horario enviará un mensaje automático.
                </p>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h3 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">
                  💡 Tu agente podrá:
                </h3>
                <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                  <li>✅ Responder preguntas sobre tu negocio</li>
                  <li>✅ Agendar citas automáticamente en tu Google Calendar</li>
                  <li>✅ Verificar disponibilidad en tiempo real</li>
                  <li>✅ Enviar confirmaciones de citas</li>
                  <li>✅ Manejar cancelaciones y reagendamientos</li>
                </ul>
              </div>
            </div>
          )}

          {/* Step 3: Final Configuration */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                ✅ ¡Tu Agente está Listo!
              </h2>
              
              <div className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg p-8">
                <div className="text-center mb-6">
                  <div className="text-6xl mb-4">🎉</div>
                  <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                    ¡Configuración Completa!
                  </h3>
                  <p className="text-gray-600 dark:text-gray-300">
                    Tu agente conversacional está configurado y listo para recibir mensajes
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-green-600 dark:text-green-400">✅</span>
                      <span className="font-semibold text-gray-900 dark:text-white">WhatsApp</span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      Instancia: {instanceName}
                    </p>
                  </div>
                  
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={config.googleCalendarConnected ? "text-green-600 dark:text-green-400" : "text-yellow-600 dark:text-yellow-400"}>
                        {config.googleCalendarConnected ? "✅" : "⏳"}
                      </span>
                      <span className="font-semibold text-gray-900 dark:text-white">Google Calendar</span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {config.googleCalendarConnected ? `Conectado: ${connectedGoogleEmail}` : "Pendiente de conexión"}
                    </p>
                  </div>
                  
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-green-600 dark:text-green-400">✅</span>
                      <span className="font-semibold text-gray-900 dark:text-white">Agente</span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {config.agentName || "Agente sin nombre"}
                    </p>
                  </div>
                  
                  <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-green-600 dark:text-green-400">✅</span>
                      <span className="font-semibold text-gray-900 dark:text-white">Horario</span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      {config.workingHours.start} - {config.workingHours.end}
                    </p>
                  </div>
                </div>

                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6">
                  <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-3">
                    🚀 ¿Cómo funciona tu agente?
                  </h4>
                  <div className="space-y-2 text-sm text-blue-700 dark:text-blue-300">
                    <p>• Los clientes escriben a tu WhatsApp conectado</p>
                    <p>• El agente responde automáticamente según tu configuración</p>
                    <p>• Puede agendar citas directamente en tu Google Calendar</p>
                    <p>• Verifica disponibilidad en tiempo real</p>
                    <p>• Respeta tu horario de atención configurado</p>
                  </div>
                </div>

                <div className="text-center">
                  <button
                    onClick={saveConfiguration}
                    className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white font-bold py-4 px-8 rounded-lg transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl text-lg"
                  >
                    🎯 Activar Mi Agente
                  </button>
                </div>
              </div>
            </div>
          )}


          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-200 dark:border-gray-600">
            <button
              onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
              disabled={currentStep === 1}
              className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
            >
              ← Anterior
            </button>
            
            <button
              onClick={() => setCurrentStep(Math.min(3, currentStep + 1))}
              disabled={currentStep === 3}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
            >
              Siguiente →
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
