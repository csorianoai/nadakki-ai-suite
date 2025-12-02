"""
Migración de tenants existentes a la nueva estructura de base de datos
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

def migrate_existing_tenants():
    """Migra tenants del sistema anterior a la nueva estructura"""
    
    conn = sqlite3.connect("tenants.db")
    cursor = conn.cursor()
    
    print("🔄 MIGRANDO TENANTS EXISTENTES...")
    
    # Leer archivos JSON de tenants existentes
    config_dir = Path("config/tenants")
    tenant_files = list(config_dir.glob("*.json"))
    
    migrated_count = 0
    
    for tenant_file in tenant_files:
        try:
            with open(tenant_file, 'r', encoding='utf-8') as f:
                tenant_data = json.load(f)
            
            tenant_id = tenant_data.get('tenant_id')
            institution_name = tenant_data.get('institution_name')
            plan = tenant_data.get('plan', 'enterprise')
            
            if not tenant_id or not institution_name:
                continue
            
            print(f"  📋 Procesando: {institution_name} ({tenant_id})")
            
            # Verificar si ya existe en la base de datos
            cursor.execute("SELECT tenant_id FROM tenants WHERE tenant_id = ?", (tenant_id,))
            existing = cursor.fetchone()
            
            if not existing:
                # Insertar en tabla tenants
                cursor.execute("""
                    INSERT INTO tenants (
                        tenant_id, institution_name, institution_type, plan,
                        api_key, status, created_at, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tenant_id,
                    institution_name,
                    tenant_data.get('institution_type', 'bank'),
                    plan,
                    f"migrated_{tenant_id}",
                    'active',
                    tenant_data.get('created_at', datetime.now().isoformat()),
                    datetime.now().isoformat()
                ))
                
                # Insertar en tenant_branding
                cursor.execute("""
                    INSERT INTO tenant_branding (
                        tenant_id, primary_color, secondary_color, logo_url
                    ) VALUES (?, ?, ?, ?)
                """, (
                    tenant_id,
                    tenant_data.get('primary_color', '#1e40af'),
                    tenant_data.get('secondary_color', '#3b82f6'),
                    tenant_data.get('logo_url', f'https://ui-avatars.com/api/?name={institution_name.replace(" ", "+")}')
                ))
                
                # Insertar en tenant_limits
                max_requests = {
                    'starter': 5000,
                    'professional': 20000, 
                    'enterprise': 999999
                }.get(plan, 999999)
                
                cursor.execute("""
                    INSERT INTO tenant_limits (
                        tenant_id, max_monthly_requests, current_monthly_requests, last_reset
                    ) VALUES (?, ?, ?, ?)
                """, (
                    tenant_id,
                    max_requests,
                    0,  # current_requests
                    datetime.now().isoformat()
                ))
                
                migrated_count += 1
                print(f"    ✅ Migrado: {institution_name}")
            
        except Exception as e:
            print(f"    ❌ Error migrando {tenant_file}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ MIGRACIÓN COMPLETADA: {migrated_count} tenants migrados")
    return migrated_count

# Ejecutar migración
if __name__ == "__main__":
    migrate_existing_tenants()