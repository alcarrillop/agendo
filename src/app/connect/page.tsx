'use client';

import Link from "next/link";
import { useState, useEffect } from "react";

interface ConnectionState {
  status: 'idle' | 'creating' | 'qr-ready' | 'connecting' | 'connected' | 'error';
  instanceName: string;
  qrCode?: string;
  error?: string;
}

export default function ConnectPage() {
  const [connectionState, setConnectionState] = useState<ConnectionState>({
    status: 'idle',
    instanceName: ''
  });
  const [testMessage, setTestMessage] = useState('');
  const [testNumber, setTestNumber] = useState('');

  const generateInstanceName = () => {
    const tenantId = Math.random().toString(36).substring(2, 15);
    return `TENANT_${tenantId}`;
  };

  const createInstance = async () => {
    const instanceName = generateInstanceName();
    const webhookUrl = `${window.location.origin}/api/webhooks/evolution`;

    setConnectionState({
      status: 'creating',
      instanceName
    });

    try {
      const response = await fetch('/api/evo/instances', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: instanceName,
          webhookUrl
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to create instance');
      }

      // Wait a moment then get QR code
      setTimeout(() => {
        getQRCode(instanceName);
      }, 2000);

    } catch (error) {
      console.error('Error creating instance:', error);
      setConnectionState({
        status: 'error',
        instanceName,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  };

  const getQRCode = async (instanceName: string) => {
    try {
      const response = await fetch(`/api/evo/instances/${instanceName}/qr`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to get QR code');
      }

      setConnectionState(prev => ({
        ...prev,
        status: 'qr-ready',
        qrCode: data.data.qr
      }));

      // Start polling connection state
      pollConnectionState(instanceName);

    } catch (error) {
      console.error('Error getting QR code:', error);
      setConnectionState(prev => ({
        ...prev,
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error'
      }));
    }
  };

  const pollConnectionState = async (instanceName: string) => {
    const checkState = async () => {
      try {
        const response = await fetch(`/api/evo/instances/${instanceName}/state`);
        const data = await response.json();

        if (data.state === 'open') {
          setConnectionState(prev => ({
            ...prev,
            status: 'connected'
          }));
          return true; // Stop polling
        }
        return false; // Continue polling
      } catch (error) {
        console.error('Error checking state:', error);
        return false;
      }
    };

    // Poll every 2 seconds for up to 2 minutes
    const maxPolls = 60;
    let pollCount = 0;

    const pollInterval = setInterval(async () => {
      pollCount++;
      const shouldStop = await checkState();

      if (shouldStop || pollCount >= maxPolls) {
        clearInterval(pollInterval);
      }
    }, 2000);
  };

  const sendTestMessage = async () => {
    if (!testNumber || !testMessage || connectionState.status !== 'connected') {
      return;
    }

    try {
      const response = await fetch(`/api/evo/instances/${connectionState.instanceName}/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to: testNumber,
          text: testMessage
        }),
      });

      const data = await response.json();

      if (response.ok) {
        alert('¡Mensaje enviado exitosamente! ✅');
        setTestMessage('');
        setTestNumber('');
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      alert('Error enviando mensaje');
    }
  };

  const resetConnection = () => {
    setConnectionState({
      status: 'idle',
      instanceName: ''
    });
    setTestMessage('');
    setTestNumber('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation */}
      <nav className="px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-gray-900 dark:text-white">
            Agendo
          </Link>
          <Link 
            href="/dashboard"
            className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors"
          >
            Dashboard
          </Link>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-6">
            Conectar WhatsApp con Evolution API
          </h1>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 max-w-2xl mx-auto">
            
            {/* Idle State */}
            {connectionState.status === 'idle' && (
              <div>
                <div className="mb-8">
                  <div className="text-6xl mb-4">📱</div>
                  <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                    ¡Conecta tu WhatsApp!
                  </h2>
                  <p className="text-gray-600 dark:text-gray-300 mb-6">
                    Usa Evolution API para conectar tu número de WhatsApp sin depender de Meta.
                  </p>
                </div>

                <button
                  onClick={createInstance}
                  className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-8 rounded-full transition-colors"
                >
                  Conectar WhatsApp
                </button>
              </div>
            )}

            {/* Creating Instance */}
            {connectionState.status === 'creating' && (
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Creando instancia...
                </h2>
                <p className="text-gray-600 dark:text-gray-300">
                  Configurando tu conexión con Evolution API
                </p>
              </div>
            )}

            {/* QR Code Ready */}
            {connectionState.status === 'qr-ready' && connectionState.qrCode && (
              <div className="text-center">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                  Escanea el código QR
                </h2>
                <div className="bg-white p-4 rounded-lg inline-block mb-4">
                  <img 
                    src={connectionState.qrCode} 
                    alt="QR Code" 
                    className="w-64 h-64 mx-auto"
                  />
                </div>
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  1. Abre WhatsApp en tu teléfono<br/>
                  2. Ve a Configuración → Dispositivos vinculados<br/>
                  3. Escanea este código QR
                </p>
                <div className="animate-pulse text-yellow-600 dark:text-yellow-400">
                  Esperando conexión...
                </div>
              </div>
            )}

            {/* Connected */}
            {connectionState.status === 'connected' && (
              <div>
                <div className="text-center mb-8">
                  <div className="text-6xl mb-4">✅</div>
                  <h2 className="text-2xl font-semibold text-green-600 dark:text-green-400 mb-2">
                    ¡WhatsApp Conectado!
                  </h2>
                  <p className="text-gray-600 dark:text-gray-300">
                    Ahora configura tu agente conversacional
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                    Instancia: {connectionState.instanceName}
                  </p>
                </div>

                {/* Next Steps */}
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-6 mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    🚀 Siguientes pasos para tu agente
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                      <div className="text-2xl mb-2">📅</div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Google Calendar</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-300">Conecta tu calendario para gestión de citas</p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                      <div className="text-2xl mb-2">🤖</div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Comportamiento</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-300">Define cómo debe responder tu agente</p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                      <div className="text-2xl mb-2">❓</div>
                      <h4 className="font-medium text-gray-900 dark:text-white">FAQs</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-300">Preguntas frecuentes y respuestas</p>
                    </div>
                    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                      <div className="text-2xl mb-2">📝</div>
                      <h4 className="font-medium text-gray-900 dark:text-white">Contexto</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-300">Define el propósito y funcionamiento</p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-4 justify-center">
                  <Link
                    href={`/setup?instance=${connectionState.instanceName}`}
                    className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-full transition-colors flex items-center gap-2"
                  >
                    <span>🛠️</span>
                    Configurar Agente
                  </Link>
                  <Link
                    href="/dashboard"
                    className="bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-full transition-colors"
                  >
                    Ver Dashboard
                  </Link>
                </div>
              </div>
            )}

            {/* Error State */}
            {connectionState.status === 'error' && (
              <div className="text-center">
                <div className="text-6xl mb-4">❌</div>
                <h2 className="text-2xl font-semibold text-red-600 dark:text-red-400 mb-4">
                  Error de conexión
                </h2>
                <p className="text-gray-600 dark:text-gray-300 mb-6">
                  {connectionState.error}
                </p>
                <button
                  onClick={resetConnection}
                  className="bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-6 rounded-full transition-colors"
                >
                  Intentar de nuevo
                </button>
              </div>
            )}

          </div>
        </div>
      </main>
    </div>
  );
}