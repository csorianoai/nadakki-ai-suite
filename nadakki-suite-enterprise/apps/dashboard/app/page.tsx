export default function Dashboard() {
  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold mb-8">Dashboard</h1>
      <div className="grid md:grid-cols-4 gap-6">
        <div className="bg-slate-900 border border-slate-700 p-6 rounded-lg">
          <p className="text-gray-400">Evaluaciones</p>
          <p className="text-3xl font-bold">1,247</p>
        </div>
        <div className="bg-slate-900 border border-slate-700 p-6 rounded-lg">
          <p className="text-gray-400">Agentes Activos</p>
          <p className="text-3xl font-bold">35</p>
        </div>
        <div className="bg-slate-900 border border-slate-700 p-6 rounded-lg">
          <p className="text-gray-400">Clientes</p>
          <p className="text-3xl font-bold">4</p>
        </div>
        <div className="bg-slate-900 border border-slate-700 p-6 rounded-lg">
          <p className="text-gray-400">Revenue</p>
          <p className="text-3xl font-bold">\.5K</p>
        </div>
      </div>
    </div>
  );
}
