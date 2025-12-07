export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-black text-white">
      <header className="border-b border-slate-800">
        <nav className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-2xl font-bold">⚡ Nadakki AI Suite</h1>
          <div className="space-x-4">
            <a href="/dashboard" className="hover:text-blue-400">Dashboard</a>
            <a href="/admin" className="hover:text-blue-400">Admin</a>
          </div>
        </nav>
      </header>

      <section className="max-w-7xl mx-auto px-4 py-32 text-center">
        <h1 className="text-5xl font-bold mb-6">Enterprise AI Agents Platform</h1>
        <p className="text-xl text-gray-400 mb-8">15 cores de IA especializados para instituciones financieras</p>
        <div className="space-x-4">
          <a href="/dashboard" className="bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded-lg inline-block">
            Dashboard
          </a>
          <a href="/admin" className="bg-slate-800 hover:bg-slate-700 px-8 py-3 rounded-lg inline-block">
            Admin Panel
          </a>
        </div>
      </section>

      <section className="max-w-7xl mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">15 AI Cores Especializados</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { icon: "💳", name: "Crédito", agents: 4 },
            { icon: "📊", name: "Marketing", agents: 3 },
            { icon: "⚖️", name: "Legal", agents: 3 },
          ].map((core) => (
            <div key={core.name} className="bg-slate-900 border border-slate-800 p-6 rounded-lg">
              <div className="text-4xl mb-4">{core.icon}</div>
              <h3 className="text-xl font-bold mb-2">{core.name}</h3>
              <p className="text-gray-400">{core.agents} agentes especializados</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
