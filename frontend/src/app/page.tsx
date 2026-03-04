export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-6">
          Welcome to AI CMS
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          A modern website engine with user registration, simple landing pages, and switchable themes.
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/login"
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Login
          </a>
          <a
            href="/register"
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Register
          </a>
        </div>
        <div className="mt-12 text-sm text-gray-500">
          <p>MVP Phase 1 - Foundation Setup</p>
        </div>
      </div>
    </div>
  );
}
