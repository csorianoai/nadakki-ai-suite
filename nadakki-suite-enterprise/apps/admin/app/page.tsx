export default function AdminDashboard() {
  return (
    <div className="p-8">
      <h1 className="text-4xl font-bold mb-8">Panel Administrativo</h1>
      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-700 p-6 rounded-lg">
          <p className="text-gray-400">Usuarios</p>
          <p className="text-3xl font-bold">142</p>
        </div>
        <div className="bg-slate-900 border border-slate-700 p-6 rounded-lg">
          <p className="text-gray-400">Tenants</p>
          <p className="text-3xl font-bold">23</p>
        </div>
        <div className="bg-slate-900 border border-slate-700 p-6 rounded-lg">
          <p className="text-gray-400">Revenue</p>
          <p className="text-3xl font-bold">\.5K</p>
        </div>
      </div>
    </div>
  );
}
