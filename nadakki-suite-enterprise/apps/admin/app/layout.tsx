import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Nadakki Admin Panel',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex h-screen bg-slate-950 text-white">
          <nav className="w-64 border-r border-slate-800 p-6 bg-slate-900">
            <h1 className="text-2xl font-bold mb-8">⚡ Nadakki Admin</h1>
            <ul className="space-y-4">
              <li><a href="/admin" className="hover:text-blue-400">📊 Dashboard</a></li>
              <li><a href="/users" className="hover:text-blue-400">👥 Usuarios</a></li>
              <li><a href="/tenants" className="hover:text-blue-400">🏢 Clientes</a></li>
              <li><a href="/settings" className="hover:text-blue-400">⚙️ Configuración</a></li>
            </ul>
          </nav>
          <main className="flex-1 overflow-auto">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
