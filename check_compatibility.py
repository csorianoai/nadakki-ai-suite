"""
VERIFICADOR DE COMPATIBILIDAD RENDER.COM
Ejecutar localmente antes de deploy
"""
import sys
import subprocess

REQUIRED_PACKAGES = {
    'numpy': '1.24.3',
    'pandas': '2.0.3',
    'fastapi': '0.104.1',
    'pydantic': '2.5.0',
    'uvicorn': '0.24.0'
}

def check_python_version():
    version = sys.version_info
    if version.major == 3 and version.minor == 11:
        print("✅ Python 3.11 (compatible con Render)")
        return True
    else:
        print(f"⚠️  Python {version.major}.{version.minor}.{version.micro}")
        print("   Recomendado: Python 3.11.9")
        return False

def check_packages():
    all_ok = True
    for package, required_version in REQUIRED_PACKAGES.items():
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        installed = line.split(': ')[1]
                        if installed == required_version:
                            print(f"✅ {package}=={installed}")
                        else:
                            print(f"❌ {package}=={installed} (requerido: {required_version})")
                            all_ok = False
                        break
            else:
                print(f"❌ {package} no instalado")
                all_ok = False
        except Exception as e:
            print(f"⚠️  Error verificando {package}: {e}")
            all_ok = False
    return all_ok

if __name__ == "__main__":
    print("=== VERIFICACIÓN DE COMPATIBILIDAD RENDER.COM ===\n")
    
    py_ok = check_python_version()
    print()
    pkgs_ok = check_packages()
    print()
    
    if py_ok and pkgs_ok:
        print("✅ SISTEMA LISTO PARA DEPLOY EN RENDER.COM")
    else:
        print("⚠️  AJUSTAR VERSIONES ANTES DE DEPLOY")
        print("\nEjecutar:")
        print("pip install -r requirements.txt -c constraints.txt")