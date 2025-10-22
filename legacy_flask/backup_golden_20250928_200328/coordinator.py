import glob
import importlib
import os

def file_to_module(file_path):
    normalized_path = file_path.replace(os.sep, ".")
    if normalized_path.startswith("agents."):
        return normalized_path.replace(".py", "")
    return "agents." + normalized_path.split("agents.", 1)[-1].replace(".py", "")

def load_all_agents():
    print("\n🧠 Iniciando importación dinámica de agentes...\n")

    for file in glob.glob("agents/**/*.py", recursive=True):
        if "__init__" in file or "base" in file:
            continue
        try:
            module_path = file_to_module(file)
            importlib.import_module(module_path)
            print(f"[IMPORT OK] {module_path}")
        except Exception as e:
            print(f"[IMPORT FAIL] {module_path} - Error: {str(e)}")

# Ejecutar al importar este módulo
load_all_agents()
