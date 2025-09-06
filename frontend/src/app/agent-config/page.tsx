"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface AgentConfig {
  id?: string;
  instance_name: string;
  agent_name: string;
  agent_purpose: string;
  agent_behavior: string;
  working_hours_start: string;
  working_hours_end: string;
  timezone: string;
  language: string;
  greeting_message?: string;
  fallback_message?: string;
  booking_instructions?: string;
  custom_prompts?: Record<string, any>;
  is_active: boolean;
}

interface Instance {
  instance_name: string;
  status: string;
  phone_number?: string;
}

export default function AgentConfigPage() {
  const [instances, setInstances] = useState<Instance[]>([]);
  const [selectedInstance, setSelectedInstance] = useState<string>("");
  const [config, setConfig] = useState<AgentConfig>({
    instance_name: "",
    agent_name: "Sofia",
    agent_purpose: "Soy un asistente virtual que ayuda a agendar citas para nuestro consultorio dental.",
    agent_behavior: "Soy amable, profesional y empática. Ayudo a los clientes a agendar citas y respondo preguntas sobre nuestros servicios.",
    working_hours_start: "09:00",
    working_hours_end: "18:00",
    timezone: "America/Bogota",
    language: "es",
    greeting_message: "¡Hola! Soy Sofia, tu asistente virtual. ¿En qué puedo ayudarte hoy?",
    fallback_message: "Lo siento, no entendí tu mensaje. ¿Podrías ser más específico?",
    booking_instructions: "Para agendar una cita, necesito saber: tu nombre, el tipo de servicio que necesitas, y tu disponibilidad preferida.",
    is_active: true
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  // Load instances on component mount
  useEffect(() => {
    loadInstances();
  }, []);

  const loadInstances = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/instances');
      if (response.ok) {
        const data = await response.json();
        setInstances(data);
      }
    } catch (error) {
      console.error('Error loading instances:', error);
    }
  };

  const loadExistingConfig = async (instanceName: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/agent-configs/instance/${instanceName}`);
      if (response.ok) {
        const existingConfig = await response.json();
        setConfig(existingConfig);
      } else if (response.status === 404) {
        // No existing config, use defaults
        setConfig(prev => ({ ...prev, instance_name: instanceName }));
      }
    } catch (error) {
      console.error('Error loading existing config:', error);
    }
  };

  const handleInstanceChange = (instanceName: string) => {
    setSelectedInstance(instanceName);
    loadExistingConfig(instanceName);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const configData = { ...config, instance_name: selectedInstance };
      
      const url = config.id 
        ? `http://localhost:8000/api/v1/agent-configs/${config.id}`
        : 'http://localhost:8000/api/v1/agent-configs/';
      
      const method = config.id ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(configData),
      });

      if (response.ok) {
        const result = await response.json();
        setConfig(result);
        setMessage({ type: 'success', text: 'Configuración guardada exitosamente!' });
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Error al guardar la configuración' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error de conexión' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation */}
      <nav className="px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-gray-900 dark:text-white">
            Awendo
          </Link>
          <div className="flex gap-4">
            <Link 
              href="/dashboard"
              className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors"
            >
              Dashboard
            </Link>
            <Link 
              href="/connect"
              className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors"
            >
              Conectar
            </Link>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            🤖 Configurar Agente
          </h1>

          {/* Instance Selection */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Seleccionar Instancia de WhatsApp
            </label>
            <select
              value={selectedInstance}
              onChange={(e) => handleInstanceChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="">Selecciona una instancia...</option>
              {instances.map((instance) => (
                <option key={instance.instance_name} value={instance.instance_name}>
                  {instance.instance_name} ({instance.status})
                </option>
              ))}
            </select>
          </div>

          {selectedInstance && (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Nombre del Agente
                  </label>
                  <input
                    type="text"
                    value={config.agent_name}
                    onChange={(e) => setConfig(prev => ({ ...prev, agent_name: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    placeholder="Ej: Sofia, Ana, Carlos..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Idioma
                  </label>
                  <select
                    value={config.language}
                    onChange={(e) => setConfig(prev => ({ ...prev, language: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="es">Español</option>
                    <option value="en">English</option>
                    <option value="pt">Português</option>
                  </select>
                </div>
              </div>

              {/* Purpose */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Propósito del Agente
                </label>
                <textarea
                  value={config.agent_purpose}
                  onChange={(e) => setConfig(prev => ({ ...prev, agent_purpose: e.target.value }))}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  placeholder="Describe qué hace tu agente y para qué negocio..."
                />
              </div>

              {/* Behavior */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Comportamiento y Personalidad
                </label>
                <textarea
                  value={config.agent_behavior}
                  onChange={(e) => setConfig(prev => ({ ...prev, agent_behavior: e.target.value }))}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  placeholder="Describe cómo debe comportarse el agente: tono, estilo, personalidad..."
                />
              </div>

              {/* Working Hours */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Horario de Inicio
                  </label>
                  <input
                    type="time"
                    value={config.working_hours_start}
                    onChange={(e) => setConfig(prev => ({ ...prev, working_hours_start: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Horario de Fin
                  </label>
                  <input
                    type="time"
                    value={config.working_hours_end}
                    onChange={(e) => setConfig(prev => ({ ...prev, working_hours_end: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Zona Horaria
                  </label>
                  <select
                    value={config.timezone}
                    onChange={(e) => setConfig(prev => ({ ...prev, timezone: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="America/Bogota">Bogotá (GMT-5)</option>
                    <option value="America/Mexico_City">México (GMT-6)</option>
                    <option value="America/Argentina/Buenos_Aires">Buenos Aires (GMT-3)</option>
                    <option value="America/Sao_Paulo">São Paulo (GMT-3)</option>
                    <option value="America/New_York">Nueva York (GMT-5)</option>
                  </select>
                </div>
              </div>

              {/* Messages */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Mensaje de Saludo
                  </label>
                  <textarea
                    value={config.greeting_message || ""}
                    onChange={(e) => setConfig(prev => ({ ...prev, greeting_message: e.target.value }))}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    placeholder="Mensaje que enviará cuando alguien inicie una conversación..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Mensaje de Fallback
                  </label>
                  <textarea
                    value={config.fallback_message || ""}
                    onChange={(e) => setConfig(prev => ({ ...prev, fallback_message: e.target.value }))}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    placeholder="Mensaje cuando no entienda lo que dice el usuario..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Instrucciones de Agendamiento
                  </label>
                  <textarea
                    value={config.booking_instructions || ""}
                    onChange={(e) => setConfig(prev => ({ ...prev, booking_instructions: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                    placeholder="Instrucciones específicas sobre cómo agendar citas..."
                  />
                </div>
              </div>

              {/* Status */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={config.is_active}
                  onChange={(e) => setConfig(prev => ({ ...prev, is_active: e.target.checked }))}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                  Agente activo
                </label>
              </div>

              {/* Message */}
              {message && (
                <div className={`p-4 rounded-md ${
                  message.type === 'success' 
                    ? 'bg-green-50 text-green-800 border border-green-200' 
                    : 'bg-red-50 text-red-800 border border-red-200'
                }`}>
                  {message.text}
                </div>
              )}

              {/* Submit Button */}
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200"
                >
                  {loading ? 'Guardando...' : 'Guardar Configuración'}
                </button>
              </div>
            </form>
          )}

          {!selectedInstance && (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">
                Primero selecciona una instancia de WhatsApp para configurar su agente.
              </p>
              <Link 
                href="/connect"
                className="mt-4 inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors duration-200"
              >
                Crear Nueva Instancia
              </Link>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
