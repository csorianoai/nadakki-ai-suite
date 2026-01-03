'use client';
import React, { createContext, useContext, useState, ReactNode } from 'react';

interface Tenant { id: string; name: string; slug: string; }
interface TenantContextValue {
  currentTenant: Tenant | null;
  tenants: Tenant[];
  isLoading: boolean;
  switchTenant: (id: string) => void;
}

const TenantContext = createContext<TenantContextValue | null>(null);

export function TenantProvider({ children }: { children: ReactNode }) {
  const [currentTenant, setCurrentTenant] = useState<Tenant | null>(null);
  const [tenants] = useState<Tenant[]>([]);
  const [isLoading] = useState(false);
  const switchTenant = (id: string) => { /* TODO */ };
  return (
    <TenantContext.Provider value={{ currentTenant, tenants, isLoading, switchTenant }}>
      {children}
    </TenantContext.Provider>
  );
}

export function useTenant() {
  const ctx = useContext(TenantContext);
  if (!ctx) throw new Error('useTenant must be used within TenantProvider');
  return ctx;
}
