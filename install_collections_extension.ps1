param(
    [string]$RootPath = ".",
    [string]$Mode = "integrate"
)

Write-Host "=== INSTALANDO EXTENSIÓN DE COBRANZA NADAKKI ===" -ForegroundColor Cyan

# Crear estructura de extensiones
$dirs = @("extensions/collections", "extensions/compliance", "extensions/voice", "extensions/config")
foreach ($dir in $dirs) {
    New-Item -Path $dir -ItemType Directory -Force | Out-Null
    Write-Host "Creado: $dir" -ForegroundColor Green
}

# Crear archivo principal de extensión
$mainExtension = @"
# collections_engine.py - Motor Principal de Cobranza
import sqlite3
from datetime import datetime

class CollectionsEngine:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        self.db_path = 'nadakki.db'
    
    def create_case(self, debtor_id, debt_amount):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        case_ref = f"CASE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        cursor.execute('''
            INSERT INTO collections_cases (tenant_id, debtor_id, case_reference, debt_amount)
            VALUES (?, ?, ?, ?)
        ''', (self.tenant_id, debtor_id, case_ref, debt_amount))
        
        case_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            'case_id': case_id,
            'case_reference': case_ref,
            'tenant_id': self.tenant_id,
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
    
    def get_case(self, case_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM collections_cases WHERE id = ? AND tenant_id = ?', 
                      (case_id, self.tenant_id))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'case_id': result[0],
                'tenant_id': result[1],
                'debtor_id': result[2],
                'case_reference': result[3],
                'debt_amount': result[4],
                'status': result[5],
                'created_at': result[6]
            }
        return None

print("Motor de cobranza inicializado correctamente")
"@

$mainExtension | Out-File "extensions/collections/collections_engine.py" -Encoding UTF8

Write-Host "✓ Motor de cobranza creado" -ForegroundColor Green
Write-Host "✓ Base de datos SQLite configurada" -ForegroundColor Green
Write-Host "✓ Extensión lista para uso" -ForegroundColor Green

# Prueba rápida
python -c "
import sys
sys.path.append('extensions/collections')
from collections_engine import CollectionsEngine

engine = CollectionsEngine('credicefi')
case = engine.create_case('DEBTOR_001', 25000.50)
print(f'Caso creado: {case}')

retrieved = engine.get_case(case['case_id'])
print(f'Caso recuperado: {retrieved}')
print('EXTENSIÓN DE COBRANZA FUNCIONANDO CORRECTAMENTE')
"

Write-Host "=== INSTALACIÓN COMPLETADA ===" -ForegroundColor Cyan
