# ============================================================
# NADAKKI AI SUITE – DEPLOYMENT MAESTRO (FASE 5)
# ============================================================
$base = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite"
$venv = "$base\venv\Scripts\activate"
Start-Process powershell -ArgumentList "-NoExit", "-Command `"cd $base; & $venv; python -m uvicorn main:app --reload --port 8000`""
Start-Sleep -Seconds 5
Start-Process powershell -ArgumentList "-NoExit", "-Command `"cd $base; & $venv; streamlit run streamlit_dashboard_cloud.py`""
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList "-NoExit", "-Command `"cd $base; & $venv; powershell -ExecutionPolicy Bypass -File .\phase5_audit.ps1`""
