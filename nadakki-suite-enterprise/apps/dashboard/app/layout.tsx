import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Nadakki Dashboard',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex h-screen bg-slate-950 text-white">
          <nav className="w-64 border-r border-slate-800 p-6 bg-slate-900">
            <h1 className="text-2xl font-bold mb-8">⚡ Nadakki</h1>
            <ul className="space-y-4">
              <li><a href="/dashboard" className="hover:text-blue-400">📊 Dashboard</a></li>
              <li><a href="/agents" className="hover:text-blue-400">🤖 Agentes</a></li>
              <li><a href="/billing" className="hover:text-blue-400">💰 Facturación</a></li>
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
