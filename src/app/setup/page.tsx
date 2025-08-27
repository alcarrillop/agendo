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
  
  const [currentStep, setCurrentStep] = useState(1);
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
    const googleSuccess = searchParams.get('google_success');
    const googleEmail = searchParams.get('email');
    const googleError = searchParams.get('google_error');

    if (googleSuccess === 'true' && googleEmail) {
      setConfig(prev => ({ ...prev, googleCalendarConnected: true }));
      setConnectedGoogleEmail(decodeURIComponent(googleEmail));
      setCurrentStep(5); // Ir al paso final
    } else if (googleError) {
      alert(`Error conectando Google Calendar: ${googleError}`);
    }
  }, [searchParams]);

  const connectGoogleCalendar = async () => {
    if (!instanceName) {
      alert('Instancia no encontrada');
      return;
    }

    setGoogleAuthLoading(true);
    
    try {
      const response = await fetch(`/api/auth/google?instance=${instanceName}`);
      const data = await response.json();

      if (data.success && data.authUrl) {
        // Redireccionar a Google OAuth
        window.location.href = data.authUrl;
      } else {
        throw new Error(data.error || 'Failed to get authorization URL');
      }
    } catch (error) {
      console.error('Error starting Google OAuth:', error);
      alert('Error al conectar con Google Calendar');
      setGoogleAuthLoading(false);
    }
  };

  const steps = [
    { id: 1, title: 'Contexto del Negocio', icon: '🏢' },
    { id: 2, title: 'Comportamiento del Agente', icon: '🤖' },
    { id: 3, title: 'Preguntas Frecuentes', icon: '❓' },
    { id: 4, title: 'Google Calendar', icon: '📅' },
    { id: 5, title: 'Configuración Final', icon: '✅' }
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
      // TODO: Save to backend/database
      console.log('Saving configuration:', config);
      alert('¡Configuración guardada exitosamente! 🎉');
    } catch (error) {
      console.error('Error saving configuration:', error);
      alert('Error al guardar la configuración');
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
          
          {/* Step 1: Business Context */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                🏢 Contexto del Negocio
              </h2>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nombre de tu agente/asistente
                </label>
                <input
                  type="text"
                  value={config.agentName}
                  onChange={(e) => setConfig(prev => ({ ...prev, agentName: e.target.value }))}
                  placeholder="Ej: Sofia, Asistente Virtual de Consultorio Dental"
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  ¿Para qué sirve tu negocio/servicio?
                </label>
                <textarea
                  value={config.agentPurpose}
                  onChange={(e) => setConfig(prev => ({ ...prev, agentPurpose: e.target.value }))}
                  placeholder="Ej: Somos un consultorio dental especializado en ortodoncia y blanqueamiento dental. Ofrecemos tratamientos de calidad con tecnología de punta..."
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Contexto adicional del negocio
                </label>
                <textarea
                  value={config.businessContext}
                  onChange={(e) => setConfig(prev => ({ ...prev, businessContext: e.target.value }))}
                  placeholder="Ej: Ubicados en el centro de Bogotá, atendemos de lunes a viernes. Tenemos 15 años de experiencia. Aceptamos seguros médicos..."
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>
          )}

          {/* Step 2: Agent Behavior */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                🤖 Comportamiento del Agente
              </h2>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  ¿Cómo quieres que se comporte tu agente?
                </label>
                <textarea
                  value={config.agentBehavior}
                  onChange={(e) => setConfig(prev => ({ ...prev, agentBehavior: e.target.value }))}
                  placeholder="Ej: Debe ser amable, profesional y empático. Siempre saludar cordialmente, preguntar el nombre del paciente, y ofrecer ayuda para agendar citas. No debe dar diagnósticos médicos, solo información general..."
                  rows={6}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                />
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                <h3 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">
                  💡 Sugerencias para el comportamiento:
                </h3>
                <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                  <li>• Personalidad: amable, profesional, empático</li>
                  <li>• Tono: formal/informal según tu negocio</li>
                  <li>• Acciones principales: agendar citas, responder FAQs</li>
                  <li>• Limitaciones: qué NO debe hacer o responder</li>
                </ul>
              </div>

              {/* Working Hours */}
              <div>
                <label className="flex items-center space-x-2 mb-4">
                  <input
                    type="checkbox"
                    checked={config.workingHours.enabled}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      workingHours: { ...prev.workingHours, enabled: e.target.checked }
                    }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Configurar horario de atención
                  </span>
                </label>

                {config.workingHours.enabled && (
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
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
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
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 3: FAQs */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                ❓ Preguntas Frecuentes (FAQs)
              </h2>
              
              {/* Add FAQ Form */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Agregar nueva pregunta frecuente
                </h3>
                <div className="space-y-4">
                  <input
                    type="text"
                    value={newFAQ.question}
                    onChange={(e) => setNewFAQ(prev => ({ ...prev, question: e.target.value }))}
                    placeholder="Pregunta (ej: ¿Cuáles son los precios de la consulta?)"
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white"
                  />
                  <textarea
                    value={newFAQ.answer}
                    onChange={(e) => setNewFAQ(prev => ({ ...prev, answer: e.target.value }))}
                    placeholder="Respuesta detallada..."
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-white"
                  />
                  <button
                    onClick={addFAQ}
                    disabled={!newFAQ.question || !newFAQ.answer}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                  >
                    Agregar FAQ
                  </button>
                </div>
              </div>

              {/* FAQ List */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  FAQs configuradas ({config.faqs.length})
                </h3>
                {config.faqs.length === 0 ? (
                  <p className="text-gray-500 dark:text-gray-400 italic">
                    No hay FAQs configuradas aún. Agrega algunas preguntas frecuentes arriba.
                  </p>
                ) : (
                  config.faqs.map((faq) => (
                    <div key={faq.id} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                            {faq.question}
                          </h4>
                          <p className="text-gray-600 dark:text-gray-300 text-sm">
                            {faq.answer}
                          </p>
                        </div>
                        <button
                          onClick={() => removeFAQ(faq.id)}
                          className="ml-4 text-red-600 hover:text-red-800 transition-colors"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Step 4: Google Calendar */}
          {currentStep === 4 && (
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
                  Permite que tu agente gestione citas automáticamente
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
                      Tu agente ahora puede agendar citas automáticamente
                    </p>
                  </div>
                ) : (
                  <div>
                    <button
                      onClick={connectGoogleCalendar}
                      disabled={googleAuthLoading}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-8 rounded-lg transition-colors inline-flex items-center gap-2"
                    >
                      {googleAuthLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Conectando...</span>
                        </>
                      ) : (
                        <>
                          <span>🔗</span>
                          <span>Conectar con Google Calendar</span>
                        </>
                      )}
                    </button>
                    <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                      <p className="mb-2">🔒 <strong>Proceso seguro:</strong></p>
                      <ul className="text-xs space-y-1 ml-4">
                        <li>• Te redirecciona a Google para autorizar</li>
                        <li>• Solo acceso de lectura/escritura a tu calendario</li>
                        <li>• Puedes revocar acceso en cualquier momento</li>
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 5: Final Configuration */}
          {currentStep === 5 && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                ✅ Configuración Final
              </h2>
              
              <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-green-800 dark:text-green-200 mb-4">
                  🎉 ¡Tu agente está casi listo!
                </h3>
                
                <div className="space-y-3 text-sm text-green-700 dark:text-green-300">
                  <div className="flex items-center gap-2">
                    <span>✅</span>
                    <span>WhatsApp conectado: <strong>{instanceName}</strong></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>✅</span>
                    <span>Agente: <strong>{config.agentName || 'Sin nombre'}</strong></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>✅</span>
                    <span>FAQs configuradas: <strong>{config.faqs.length}</strong></span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>{config.googleCalendarConnected ? '✅' : '⏳'}</span>
                    <span>Google Calendar: <strong>{config.googleCalendarConnected ? 'Conectado' : 'Pendiente'}</strong></span>
                  </div>
                </div>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6">
                <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">
                  📱 ¿Cómo funciona ahora?
                </h4>
                <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                  <li>• Los clientes pueden escribir a tu WhatsApp</li>
                  <li>• El agente responderá automáticamente según la configuración</li>
                  <li>• Podrá responder FAQs y agendar citas (si Google Calendar está conectado)</li>
                  <li>• Respetará el horario de atención configurado</li>
                </ul>
              </div>

              <div className="text-center">
                <button
                  onClick={saveConfiguration}
                  className="bg-green-600 hover:bg-green-700 text-white font-bold py-4 px-8 rounded-lg transition-colors text-lg"
                >
                  🚀 Activar mi Agente
                </button>
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
              onClick={() => setCurrentStep(Math.min(5, currentStep + 1))}
              disabled={currentStep === 5}
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
