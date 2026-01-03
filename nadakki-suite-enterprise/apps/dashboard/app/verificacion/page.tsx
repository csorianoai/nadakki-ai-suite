'use client';
import React, { useState, useEffect } from 'react';

const colors = {
  bg: { primary: '#0a0f1c', card: 'rgba(26, 31, 46, 0.9)' },
  text: { primary: '#f8fafc', muted: '#64748b' },
  accent: '#ff6b9d',
};

export default function VerificacionPage() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => setIsLoading(false), 800);
  }, []);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: colors.bg.primary, color: colors.text.primary, padding: 32, fontFamily: 'system-ui' }}>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={{ fontSize: 40 }}>🔐</span>
          Verificación Biométrica
        </h1>
        <p style={{ fontSize: 14, color: colors.text.muted, marginTop: 8 }}>15 agentes especializados - Nadakki AI Enterprise</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 20, marginBottom: 32 }}>
        {[
          { label: 'Agentes Activos', value: '15', icon: '🤖' },
          { label: 'Tareas Hoy', value: '0', icon: '📋' },
          { label: 'Precisión', value: '97%', icon: '🎯' },
          { label: 'Uptime', value: '99.9%', icon: '⚡' },
        ].map((stat, i) => (
          <div key={i} style={{ background: 'linear-gradient(135deg, #1a1f2e, #252b3f)', borderRadius: 16, border: '1px solid rgba(51, 65, 85, 0.5)', padding: 20 }}>
            <div style={{ fontSize: 24, marginBottom: 8 }}>{stat.icon}</div>
            <div style={{ fontSize: 28, fontWeight: 700, color: colors.accent }}>{isLoading ? '...' : stat.value}</div>
            <div style={{ fontSize: 12, color: colors.text.muted, marginTop: 4 }}>{stat.label}</div>
          </div>
        ))}
      </div>

      <div style={{ backgroundColor: colors.bg.card, borderRadius: 16, border: '1px solid rgba(51, 65, 85, 0.5)', padding: 24 }}>
        <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
          🔐 Panel de Control
        </h3>
        <div style={{ textAlign: 'center', padding: 48, color: colors.text.muted }}>
          <div style={{ fontSize: 64, marginBottom: 16, opacity: 0.5 }}>🔐</div>
          <p>Módulo Verificación Biométrica integrado</p>
          <p style={{ fontSize: 12, marginTop: 8 }}>Conectando con 15 agentes...</p>
        </div>
      </div>
    </div>
  );
}
