import Link from "next/link";

export default function Home() {
  const sandboxNumber = process.env.TWILIO_SANDBOX_NUMBER || "1XXXXXXXXXX";
  const sandboxCode = process.env.TWILIO_SANDBOX_CODE || "xxxxxx";
  const sandboxLink = `https://wa.me/${sandboxNumber}?text=${encodeURIComponent(`join ${sandboxCode}`)}`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Navigation */}
      <nav className="px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
                  <div className="text-2xl font-bold text-gray-900 dark:text-white">
          Awendo
        </div>
          <Link 
            href="/dashboard"
            className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white transition-colors"
          >
            Dashboard
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 py-16 sm:py-24">
        <div className="text-center">
          {/* Hero Title */}
          <h1 className="text-4xl sm:text-6xl font-bold text-gray-900 dark:text-white mb-6">
            <span className="block">Awendo</span>
            <span className="block text-3xl sm:text-5xl text-blue-600 dark:text-blue-400 mt-2">
              De chat a cita en segundos
            </span>
          </h1>

          {/* Hero Description */}
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto">
            Convierte conversaciones de WhatsApp en citas automáticamente. 
            Sin formularios complicados, sin apps que descargar.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            {/* CTA 1: Probar ya (Sandbox) */}
            <a
              href={sandboxLink}
              target="_blank"
              rel="noopener noreferrer"
              className="bg-green-600 hover:bg-green-700 text-white font-semibold py-4 px-8 rounded-full text-lg transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center gap-3"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.893 3.097"/>
              </svg>
              Probar ya
            </a>

            {/* CTA 2: Conectar tu número */}
            <Link
              href="/connect"
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-8 rounded-full text-lg transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
            >
              Conectar tu número
            </Link>
          </div>

          {/* Sandbox Instructions */}
          <div className="mt-12 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
              💡 Para probar en 30 segundos:
            </h3>
            <ol className="text-left text-gray-600 dark:text-gray-300 space-y-2">
              <li>1. Haz clic en <strong>&quot;Probar ya&quot;</strong></li>
              <li>2. Se abrirá WhatsApp con el mensaje pre-escrito</li>
              <li>3. Envía el mensaje para unirte al sandbox</li>
              <li>4. ¡Recibe una respuesta automática!</li>
            </ol>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-8 text-gray-500 dark:text-gray-400">
        <p>© 2025 Awendo. Construido para simplificar la gestión de citas.</p>
      </footer>
    </div>
  );
}
