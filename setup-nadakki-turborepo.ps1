param(
    [string]$ProjectName = "nadakki-suite-enterprise",
    [string]$RenderUrl = "https://nadakki-ai-suite.onrender.com",
    [string]$TenantId = "credicefi",
    [string]$ApiKey = "sk_live_credicefi_12345678abcdefgh"
)

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   NADAKKI SUITE v4.0 - TURBOREPO ENTERPRISE GENERATOR      ║" -ForegroundColor Cyan
Write-Host "║   Monorepo Profesional + Enterprise-Grade                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ PASO 1: Verificando requisitos..." -ForegroundColor Yellow
Write-Host ""

$requirements = @{
    "Node.js" = { node -v }
    "npm" = { npm -v }
    "git" = { git --version }
}

foreach ($req in $requirements.GetEnumerator()) {
    try {
        $version = & $req.Value 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ $($req.Key): $version" -ForegroundColor Green
        } else {
            Write-Host "   ❌ $($req.Key) no encontrado" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "   ❌ $($req.Key) no encontrado" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

Write-Host "📦 PASO 2: Creando estructura TurboRepo..." -ForegroundColor Yellow

if (!(Test-Path $ProjectName)) {
    New-Item -ItemType Directory -Path $ProjectName | Out-Null
    Write-Host "   ✅ Carpeta creada: $ProjectName" -ForegroundColor Green
}

Set-Location $ProjectName

$dirs = @(
    "apps/dashboard",
    "apps/dashboard/src/app",
    "apps/dashboard/src/components",
    "apps/dashboard/src/lib",
    "apps/admin",
    "apps/admin/src/app",
    "apps/admin/src/components",
    "apps/admin/src/lib",
    "apps/landing",
    "apps/landing/src/app",
    "apps/landing/src/components",
    "apps/landing/src/lib",
    "packages/ui/src",
    "packages/api/src",
    "packages/utils/src",
    "packages/types/src"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

Write-Host "   ✅ Estructura de carpetas creada" -ForegroundColor Green
Write-Host ""

Write-Host "📝 PASO 3: Configurando TurboRepo..." -ForegroundColor Yellow

$rootPackageJson = @{
    "name" = "nadakki-suite-enterprise"
    "version" = "4.0.0"
    "private" = $true
    "scripts" = @{
        "build" = "turbo run build"
        "dev" = "turbo run dev --parallel"
        "lint" = "turbo run lint"
        "format" = "turbo run format"
        "test" = "turbo run test"
    }
    "devDependencies" = @{
        "turbo" = "latest"
        "typescript" = "^5.0.0"
    }
    "workspaces" = @(
        "apps/*",
        "packages/*"
    )
} | ConvertTo-Json -Depth 10

$rootPackageJson | Out-File "package.json" -Encoding UTF8

Write-Host "   ✅ package.json raíz creado" -ForegroundColor Green

Write-Host "⚙️  PASO 4: Configurando turbo.json..." -ForegroundColor Yellow

$turboJson = @{
    "`$schema" = "https://turborepo.org/schema.json"
    "globalDependencies" = @("**/.env.local")
    "pipeline" = @{
        "build" = @{
            "outputs" = @(".next/**")
            "cache" = $false
        }
        "lint" = @{
            "outputs" = @()
        }
        "dev" = @{
            "cache" = $false
            "persistent" = $true
        }
        "test" = @{
            "outputs" = @("coverage/**")
            "cache" = $false
        }
    }
} | ConvertTo-Json -Depth 10

$turboJson | Out-File "turbo.json" -Encoding UTF8

Write-Host "   ✅ turbo.json creado" -ForegroundColor Green
Write-Host ""

Write-Host "🔐 PASO 5: Creando .gitignore..." -ForegroundColor Yellow

$gitignore = @"
node_modules/
.pnp
.pnp.js
coverage/
.next/
out/
dist/
build/
.DS_Store
*.pem
.idea/
.vscode/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
.turbo/
Thumbs.db
"@

$gitignore | Out-File ".gitignore" -Encoding UTF8

Write-Host "   ✅ .gitignore creado" -ForegroundColor Green
Write-Host ""

Write-Host "🔌 PASO 6: Generando packages/api..." -ForegroundColor Yellow

$apiPackageJson = @{
    "name" = "@nadakki/api"
    "version" = "1.0.0"
    "main" = "./src/index.ts"
    "types" = "./src/index.ts"
    "dependencies" = @{
        "axios" = "^1.6.0"
    }
} | ConvertTo-Json -Depth 10

$apiPackageJson | Out-File "packages/api/package.json" -Encoding UTF8

$apiIndex = @"
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_RENDER_API_URL || '$RenderUrl';
const TENANT_ID = process.env.NEXT_PUBLIC_TENANT_ID || '$TenantId';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '$ApiKey';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-Tenant-ID': TENANT_ID,
    'X-API-Key': API_KEY,
  }
});

apiClient.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
    if (token) {
      config.headers.Authorization = \`Bearer \${token}\`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const api = {
  getCores: () => apiClient.get('/cores'),
  getCore: (id: string) => apiClient.get(\`/cores/\${id}\`),
  getAgents: () => apiClient.get('/agents'),
  executeAgent: (id: string, payload: any) => apiClient.post(\`/agents/\${id}/execute\`, payload),
  getMetrics: () => apiClient.get('/dashboard/metrics'),
  getHealth: () => apiClient.get('/health'),
  getTenants: () => apiClient.get('/tenants'),
  createTenant: (data: any) => apiClient.post('/tenants', data),
  getInvoices: () => apiClient.get('/billing/invoices'),
};

export default apiClient;
"@

$apiIndex | Out-File "packages/api/src/index.ts" -Encoding UTF8

Write-Host "   ✅ packages/api creado" -ForegroundColor Green

Write-Host "🎨 PASO 7: Generando packages/ui..." -ForegroundColor Yellow

$uiPackageJson = @{
    "name" = "@nadakki/ui"
    "version" = "1.0.0"
    "main" = "./src/index.ts"
    "types" = "./src/index.ts"
    "dependencies" = @{
        "react" = "^18.0.0"
        "lucide-react" = "latest"
        "clsx" = "^2.0.0"
    }
} | ConvertTo-Json -Depth 10

$uiPackageJson | Out-File "packages/ui/package.json" -Encoding UTF8

$uiIndex = @"
export const Button = ({ children, className, ...props }: any) => (
  <button className={`px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition \${className}`} {...props}>
    {children}
  </button>
);

export const Card = ({ children, className, ...props }: any) => (
  <div className={`bg-white rounded-lg shadow p-6 \${className}`} {...props}>
    {children}
  </div>
);

export const Badge = ({ children, variant = 'default', className, ...props }: any) => {
  const colors: any = {
    default: 'bg-gray-200 text-gray-800',
    success: 'bg-green-100 text-green-800',
    error: 'bg-red-100 text-red-800',
  };
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium \${colors[variant]} \${className}`} {...props}>
      {children}
    </span>
  );
};

export const Input = ({ className, ...props }: any) => (
  <input className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 \${className}`} {...props} />
);

export const Container = ({ children, className, ...props }: any) => (
  <div className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 \${className}`} {...props}>
    {children}
  </div>
);
"@

$uiIndex | Out-File "packages/ui/src/index.ts" -Encoding UTF8

Write-Host "   ✅ packages/ui creado" -ForegroundColor Green

Write-Host "📝 PASO 8: Generando packages/types..." -ForegroundColor Yellow

$typesPackageJson = @{
    "name" = "@nadakki/types"
    "version" = "1.0.0"
    "main" = "./src/index.ts"
    "types" = "./src/index.ts"
} | ConvertTo-Json -Depth 10

$typesPackageJson | Out-File "packages/types/package.json" -Encoding UTF8

$typesIndex = @"
export interface Agent {
  id: string;
  name: string;
  description: string;
  status: 'healthy' | 'error' | 'unknown';
  category: string;
  lastRun?: string;
}

export interface Core {
  id: string;
  name: string;
  description: string;
  agents: Agent[];
  icon: string;
  color: string;
}

export interface Tenant {
  id: string;
  name: string;
  email: string;
  plan: 'starter' | 'professional' | 'enterprise';
  status: 'active' | 'inactive';
}

export interface DashboardMetrics {
  total_evaluations: number;
  agents_active: number;
  revenue_today: number;
  uptime_percentage: number;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'viewer';
}

export interface Invoice {
  id: string;
  invoice_number: string;
  tenant_id: string;
  amount: number;
  status: 'draft' | 'sent' | 'paid' | 'overdue';
  due_date: string;
  created_at: string;
}
"@

$typesIndex | Out-File "packages/types/src/index.ts" -Encoding UTF8

Write-Host "   ✅ packages/types creado" -ForegroundColor Green
Write-Host ""

Write-Host "📊 PASO 9: Generando apps/dashboard..." -ForegroundColor Yellow

npx create-next-app@latest dashboard --typescript --tailwind --app --no-git --no-src-dir --import-alias "@/*" -y 2>$null
Move-Item -Path "dashboard/*" -Destination "apps/dashboard/" -Force
Remove-Item "dashboard" -Recurse -Force

$dashboardEnv = @"
NEXT_PUBLIC_RENDER_API_URL=$RenderUrl
NEXT_PUBLIC_TENANT_ID=$TenantId
NEXT_PUBLIC_API_KEY=$ApiKey
NEXT_PUBLIC_APP_NAME=Nadakki Dashboard
NODE_ENV=development
"@

$dashboardEnv | Out-File "apps/dashboard/.env.local" -Encoding UTF8

$dashboardLayout = @"
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
"@

$dashboardLayout | Out-File "apps/dashboard/app/layout.tsx" -Encoding UTF8

$dashboardPage = @"
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
          <p className="text-3xl font-bold">\$12.5K</p>
        </div>
      </div>
    </div>
  );
}
"@

$dashboardPage | Out-File "apps/dashboard/app/page.tsx" -Encoding UTF8

Write-Host "   ✅ apps/dashboard creado" -ForegroundColor Green

Write-Host "👥 PASO 10: Generando apps/admin..." -ForegroundColor Yellow

npx create-next-app@latest admin --typescript --tailwind --app --no-git --no-src-dir --import-alias "@/*" -y 2>$null
Move-Item -Path "admin/*" -Destination "apps/admin/" -Force
Remove-Item "admin" -Recurse -Force

$adminEnv = @"
NEXT_PUBLIC_RENDER_API_URL=$RenderUrl
NEXT_PUBLIC_TENANT_ID=$TenantId
NEXT_PUBLIC_API_KEY=$ApiKey
NEXT_PUBLIC_APP_NAME=Nadakki Admin
NODE_ENV=development
"@

$adminEnv | Out-File "apps/admin/.env.local" -Encoding UTF8

$adminLayout = @"
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
"@

$adminLayout | Out-File "apps/admin/app/layout.tsx" -Encoding UTF8

$adminPage = @"
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
          <p className="text-3xl font-bold">\$128.5K</p>
        </div>
      </div>
    </div>
  );
}
"@

$adminPage | Out-File "apps/admin/app/page.tsx" -Encoding UTF8

Write-Host "   ✅ apps/admin creado" -ForegroundColor Green

Write-Host "🌐 PASO 11: Generando apps/landing..." -ForegroundColor Yellow

npx create-next-app@latest landing --typescript --tailwind --app --no-git --no-src-dir --import-alias "@/*" -y 2>$null
Move-Item -Path "landing/*" -Destination "apps/landing/" -Force
Remove-Item "landing" -Recurse -Force

$landingEnv = @"
NEXT_PUBLIC_APP_NAME=Nadakki AI Suite
NODE_ENV=development
"@

$landingEnv | Out-File "apps/landing/.env.local" -Encoding UTF8

$landingLayout = @"
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Nadakki AI Suite - Enterprise Platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-white">{children}</body>
    </html>
  );
}
"@

$landingLayout | Out-File "apps/landing/app/layout.tsx" -Encoding UTF8

$landingPage = @"
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
"@

$landingPage | Out-File "apps/landing/app/page.tsx" -Encoding UTF8

Write-Host "   ✅ apps/landing creado" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 PASO 12: Configurando Vercel..." -ForegroundColor Yellow

$vercelJson = @{
    "version" = 2
    "builds" = @(
        @{
            "src" = "apps/dashboard/package.json"
            "use" = "@vercel/next"
        },
        @{
            "src" = "apps/admin/package.json"
            "use" = "@vercel/next"
        },
        @{
            "src" = "apps/landing/package.json"
            "use" = "@vercel/next"
        }
    )
} | ConvertTo-Json -Depth 10

$vercelJson | Out-File "vercel.json" -Encoding UTF8

Write-Host "   ✅ vercel.json creado" -ForegroundColor Green

Write-Host "📖 PASO 13: Generando documentación..." -ForegroundColor Yellow

$readme = @"
# Nadakki AI Suite v4.0 - TurboRepo Enterprise

Monorepo profesional con dashboard, admin panel, landing page y más.

## 📁 Estructura

\`\`\`
nadakki-suite-enterprise/
├── apps/
│   ├── dashboard/
│   ├── admin/
│   └── landing/
├── packages/
│   ├── api/
│   ├── ui/
│   ├── types/
│   └── utils/
├── turbo.json
├── package.json
└── vercel.json
\`\`\`

## 🚀 Inicio rápido

\`\`\`bash
npm install
npm run dev
\`\`\`

## 📊 Apps

- **Dashboard**: http://localhost:3000
- **Admin**: http://localhost:3001
- **Landing**: http://localhost:3002

## 🚢 Deployment

\`\`\`bash
npm install -g vercel
vercel
\`\`\`
"@

$readme | Out-File "README.md" -Encoding UTF8

Write-Host "   ✅ README.md creado" -ForegroundColor Green
Write-Host ""

Write-Host "📦 PASO 14: Instalando TurboRepo..." -ForegroundColor Yellow

npm install turbo 2>$null

Write-Host "   ✅ TurboRepo instalado" -ForegroundColor Green
Write-Host ""

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║        ✅ NADAKKI SUITE v4.0 GENERADA CON ÉXITO            ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📁 Proyecto: $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

Write-Host "🚀 PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   1. npm install" -ForegroundColor Cyan
Write-Host "   2. npm run dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Dashboard: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Admin:     http://localhost:3001" -ForegroundColor Cyan
Write-Host "   Landing:   http://localhost:3002" -ForegroundColor Cyan
Write-Host ""

Write-Host "✨ ¡Nadakki Suite v4.0 está lista para desarrollo!" -ForegroundColor Green
Write-Host ""

