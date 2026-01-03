'use client';
import React, { useState, useEffect, ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavModule { id: string; icon: string; label: string; href: string; badge?: number | string; }
interface NavCore { id: string; title: string; icon: string; color: string; gradient: string; modules: NavModule[]; }

const navigationStructure: NavCore[] = [
  { id: 'system', title: 'SISTEMA', icon: '🚀', color: '#00d4ff', gradient: 'linear-gradient(135deg, #00d4ff, #0099cc)', modules: [
    { id: 'dashboard', icon: '🏠', label: 'Dashboard Principal', href: '/', badge: '∞' },
    { id: 'tenants', icon: '🏢', label: 'Multi-Tenant', href: '/tenants', badge: 'NEW' },
    { id: 'pricing', icon: '💎', label: 'Planes & Pricing', href: '/pricing' },
  ]},
  { id: 'workflows', title: 'WORKFLOWS', icon: '🔄', color: '#8B5CF6', gradient: 'linear-gradient(135deg, #8B5CF6, #6366F1)', modules: [
    { id: 'wf-campaign', icon: '📢', label: 'Campaign Optimization', href: '/workflows/campaign-optimization', badge: '5' },
    { id: 'wf-acquisition', icon: '🎯', label: 'Customer Acquisition', href: '/workflows/customer-acquisition-intelligence', badge: '7' },
    { id: 'wf-lifecycle', icon: '♻️', label: 'Customer Lifecycle', href: '/workflows/customer-lifecycle-revenue', badge: '6' },
    { id: 'wf-content', icon: '📝', label: 'Content Performance', href: '/workflows/content-performance-engine', badge: '5' },
    { id: 'wf-social', icon: '📱', label: 'Social Intelligence', href: '/workflows/social-media-intelligence', badge: '4' },
    { id: 'wf-email', icon: '✉️', label: 'Email Automation', href: '/workflows/email-automation-master', badge: '4' },
    { id: 'wf-attribution', icon: '📊', label: 'Multi-Channel Attribution', href: '/workflows/multi-channel-attribution', badge: '4' },
    { id: 'wf-competitive', icon: '🔍', label: 'Competitive Intel', href: '/workflows/competitive-intelligence-hub', badge: '3' },
    { id: 'wf-abtesting', icon: '🧪', label: 'A/B Testing', href: '/workflows/ab-testing-experimentation', badge: '3' },
    { id: 'wf-influencer', icon: '⭐', label: 'Influencer Engine', href: '/workflows/influencer-partnership-engine', badge: '2' },
  ]},
  { id: 'marketing', title: 'MARKETING', icon: '🎯', color: '#F97316', gradient: 'linear-gradient(135deg, #F97316, #EA580C)', modules: [
    { id: 'mkt-leads', icon: '📊', label: 'Lead Management', href: '/marketing/leads', badge: '3' },
    { id: 'mkt-content', icon: '✍️', label: 'Content Generation', href: '/marketing/content', badge: '4' },
    { id: 'mkt-social', icon: '📱', label: 'Social Media', href: '/marketing/social', badge: '3' },
    { id: 'mkt-all', icon: '🎯', label: 'Ver 35 Agentes', href: '/marketing', badge: '35' },
  ]},
  { id: 'legal', title: 'LEGAL', icon: '⚖️', color: '#A855F7', gradient: 'linear-gradient(135deg, #A855F7, #9333EA)', modules: [
    { id: 'legal-laboral', icon: '👷', label: 'Derecho Laboral', href: '/legal/laboral', badge: '2' },
    { id: 'legal-tributario', icon: '💰', label: 'Derecho Tributario', href: '/legal/tributario', badge: '2' },
    { id: 'legal-all', icon: '⚖️', label: 'Ver 32 Agentes', href: '/legal', badge: '32' },
  ]},
  { id: 'finanzas', title: 'FINANZAS', icon: '🏦', color: '#EC4899', gradient: 'linear-gradient(135deg, #EC4899, #DB2777)', modules: [
    { id: 'originacion', icon: '📝', label: 'Originación', href: '/originacion', badge: '10' },
    { id: 'decision', icon: '⚖️', label: 'Decisión', href: '/decision', badge: '5' },
    { id: 'contabilidad', icon: '📊', label: 'Contabilidad', href: '/contabilidad', badge: '22' },
    { id: 'presupuesto', icon: '💰', label: 'Presupuesto', href: '/presupuesto', badge: '13' },
  ]},
  { id: 'compliance', title: 'COMPLIANCE', icon: '🛡️', color: '#EF4444', gradient: 'linear-gradient(135deg, #EF4444, #DC2626)', modules: [
    { id: 'regtech', icon: '📋', label: 'RegTech', href: '/regtech', badge: '8' },
    { id: 'compliance', icon: '✅', label: 'Compliance', href: '/compliance', badge: '5' },
  ]},
  { id: 'operaciones', title: 'OPERACIONES', icon: '⚙️', color: '#14B8A6', gradient: 'linear-gradient(135deg, #14B8A6, #0D9488)', modules: [
    { id: 'rrhh', icon: '👥', label: 'RRHH', href: '/rrhh', badge: '10' },
    { id: 'logistica', icon: '🚚', label: 'Logística', href: '/logistica', badge: '23' },
  ]},
  { id: 'otros', title: 'ESPECIALIDADES', icon: '🎓', color: '#64748B', gradient: 'linear-gradient(135deg, #64748B, #475569)', modules: [
    { id: 'ventascrm', icon: '🤝', label: 'Ventas CRM', href: '/ventascrm', badge: '9' },
    { id: 'educacion', icon: '🎓', label: 'Educación', href: '/educacion', badge: '9' },
  ]},
];

const colors = { bg: { primary: '#0a0f1c', sidebar: 'rgba(26, 31, 46, 0.98)', tertiary: '#252b3f' }, border: { subtle: 'rgba(51, 65, 85, 0.5)' }, text: { primary: '#f8fafc', secondary: '#94a3b8', muted: '#64748b' }, neon: { blue: '#00d4ff', purple: '#a55eea', green: '#26de81' } };

function NavItem({ module, coreColor, isActive, isCollapsed }: { module: NavModule; coreColor: string; isActive: boolean; isCollapsed: boolean }) {
  const [isHovered, setIsHovered] = useState(false);
  return (<Link href={module.href} style={{ textDecoration: 'none' }}><div onMouseEnter={() => setIsHovered(true)} onMouseLeave={() => setIsHovered(false)} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 12px 8px 20px', margin: '1px 6px', borderRadius: '8px', cursor: 'pointer', backgroundColor: isActive ? `${coreColor}25` : isHovered ? 'rgba(51, 65, 85, 0.4)' : 'transparent', borderLeft: isActive ? `3px solid ${coreColor}` : '3px solid transparent' }}><span style={{ fontSize: '14px' }}>{module.icon}</span><span style={{ fontSize: '12px', fontWeight: isActive ? 600 : 400, color: isActive ? coreColor : colors.text.secondary, flex: 1 }}>{module.label}</span>{module.badge && (<span style={{ fontSize: '9px', fontWeight: 700, padding: '2px 5px', borderRadius: '8px', backgroundColor: 'rgba(255,255,255,0.08)', color: colors.text.muted }}>{module.badge}</span>)}</div></Link>);
}

function CoreSection({ core, currentPath, isExpanded, onToggle }: { core: NavCore; currentPath: string; isExpanded: boolean; onToggle: () => void }) {
  const [isHovered, setIsHovered] = useState(false);
  const hasActiveModule = core.modules.some(m => currentPath === m.href || (m.href !== '/' && currentPath.startsWith(m.href)));
  return (<div style={{ margin: '3px 6px', borderRadius: '10px', backgroundColor: isExpanded ? `${core.color}08` : 'transparent', border: `1px solid ${isExpanded ? `${core.color}25` : 'transparent'}` }}><div onClick={onToggle} onMouseEnter={() => setIsHovered(true)} onMouseLeave={() => setIsHovered(false)} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 12px', cursor: 'pointer', backgroundColor: isHovered ? `${core.color}15` : 'transparent', borderRadius: '8px' }}><div style={{ width: '28px', height: '28px', borderRadius: '8px', background: isExpanded || hasActiveModule ? core.gradient : 'rgba(51, 65, 85, 0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px' }}>{core.icon}</div><div style={{ flex: 1 }}><div style={{ fontSize: '10px', fontWeight: 700, color: isExpanded ? core.color : colors.text.secondary, textTransform: 'uppercase' }}>{core.title}</div></div><span style={{ fontSize: '9px', color: colors.text.muted, transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s ease' }}>▼</span></div><div style={{ maxHeight: isExpanded ? '600px' : '0px', overflow: 'hidden', transition: 'max-height 0.3s ease' }}>{core.modules.map((module) => (<NavItem key={module.id} module={module} coreColor={core.color} isActive={currentPath === module.href} isCollapsed={false} />))}</div></div>);
}

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [expandedCores, setExpandedCores] = useState<string[]>(['system', 'workflows']);
  const toggleCore = (coreId: string) => setExpandedCores(prev => prev.includes(coreId) ? prev.filter(id => id !== coreId) : [...prev, coreId]);
  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: colors.bg.primary }}>
      <aside style={{ width: 280, backgroundColor: colors.bg.sidebar, borderRight: `1px solid ${colors.border.subtle}`, position: 'fixed', left: 0, top: 0, height: '100vh', overflowY: 'auto', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '16px 14px', borderBottom: `1px solid ${colors.border.subtle}`, display: 'flex', alignItems: 'center', gap: '10px' }}><div style={{ width: '38px', height: '38px', borderRadius: '10px', background: 'linear-gradient(135deg, #667eea, #764ba2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px' }}>🚀</div><div><div style={{ fontSize: '15px', fontWeight: 800, background: 'linear-gradient(135deg, #667eea, #764ba2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>NADAKKI AI</div><div style={{ fontSize: '8px', color: colors.text.muted }}>Enterprise Suite</div></div></div>
        <div style={{ padding: '8px 10px', margin: '10px', borderRadius: '8px', background: 'rgba(139, 92, 246, 0.1)', display: 'flex', justifyContent: 'space-around' }}><div style={{ textAlign: 'center' }}><div style={{ fontSize: '14px', fontWeight: 800, color: colors.neon.purple }}>225</div><div style={{ fontSize: '7px', color: colors.text.muted }}>AGENTES</div></div><div style={{ textAlign: 'center' }}><div style={{ fontSize: '14px', fontWeight: 800, color: colors.neon.green }}>20</div><div style={{ fontSize: '7px', color: colors.text.muted }}>CORES</div></div><div style={{ textAlign: 'center' }}><div style={{ fontSize: '14px', fontWeight: 800, color: colors.neon.blue }}>10</div><div style={{ fontSize: '7px', color: colors.text.muted }}>WORKFLOWS</div></div></div>
        <nav style={{ flex: 1, padding: '2px 0' }}>{navigationStructure.map((core) => (<CoreSection key={core.id} core={core} currentPath={pathname} isExpanded={expandedCores.includes(core.id)} onToggle={() => toggleCore(core.id)} />))}</nav>
        <div style={{ padding: '10px', borderTop: `1px solid ${colors.border.subtle}` }}><div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 10px', borderRadius: '8px', background: 'rgba(51, 65, 85, 0.3)' }}><div style={{ width: '30px', height: '30px', borderRadius: '8px', background: 'linear-gradient(135deg, #667eea, #764ba2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '14px' }}>🏦</div><div style={{ flex: 1 }}><div style={{ fontSize: '11px', fontWeight: 600, color: colors.text.primary }}>Credicefi</div><div style={{ fontSize: '8px', color: colors.text.muted }}>Enterprise</div></div><div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#26de81' }} /></div></div>
      </aside>
      <main style={{ flex: 1, marginLeft: 280, minHeight: '100vh' }}>{children}</main>
    </div>
  );
}
