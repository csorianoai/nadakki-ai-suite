// NADAKKI - Integracion del Sidebar v6.6
// Agrega estos items a tu navItems en page.tsx:

export const marketingNavItems = [
  { id: 'campaigns', icon: '📢', label: 'Campañas', color: '#EAB308', href: '/campaigns' },
  { id: 'social', icon: '🔗', label: 'Social', color: '#06B6D4', href: '/social' },
  { id: 'ai-studio', icon: '🤖', label: 'AI Studio', color: '#8B5CF6', href: '/ai-studio' },
  { id: 'analytics', icon: '📊', label: 'Analytics', color: '#22C55E', href: '/analytics' },
  { id: 'export', icon: '📥', label: 'Exportar', color: '#06B6D4', href: '/export' },
  { id: 'notifications', icon: '🔔', label: 'Notificaciones', color: '#EF4444', href: '/notifications' },
  { id: 'scheduler', icon: '⏰', label: 'Scheduler', color: '#F97316', href: '/scheduler' },
  { id: 'tenants', icon: '🏢', label: 'Tenants', color: '#6366F1', href: '/tenants' },
];

// Uso con Next.js Link:
// import Link from 'next/link';
// {marketingNavItems.map(item => (
//   <Link key={item.id} href={item.href}>
//     <button style={{color: item.color}}>{item.icon} {item.label}</button>
//   </Link>
// ))}
