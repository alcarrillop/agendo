import Link from "next/link";

export default function ConnectPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
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
            Conectar tu número de WhatsApp
          </h1>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-8 max-w-2xl mx-auto">
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-lg p-6 mb-8">
              <h2 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200 mb-2">
                🚧 Próximamente
              </h2>
              <p className="text-yellow-700 dark:text-yellow-300">
                Esta funcionalidad estará disponible pronto. Por ahora, puedes probar Agendo usando nuestro sandbox de WhatsApp.
              </p>
            </div>

            <div className="text-left space-y-4 text-gray-600 dark:text-gray-300">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                ¿Qué podrás hacer cuando esté listo?
              </h3>
              <ul className="space-y-3">
                <li className="flex items-start gap-3">
                  <span className="text-green-500 font-bold">✓</span>
                  <span>Conectar tu número de WhatsApp Business</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-500 font-bold">✓</span>
                  <span>Configurar webhooks automáticamente</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-500 font-bold">✓</span>
                  <span>Gestionar citas desde tu propio número</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-500 font-bold">✓</span>
                  <span>Acceso completo a todas las funcionalidades</span>
                </li>
              </ul>
            </div>

            <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/"
                className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-full transition-colors"
              >
                Volver al inicio
              </Link>
              <Link
                href="/dashboard"
                className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-full transition-colors"
              >
                Ver Dashboard
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
