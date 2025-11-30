$prompt = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\prompts\Plan4_ExecPrompt.json"
$app = "C:\Users\cesar\Projects\nadakki-ai-suite\nadakki-ai-suite\app.py"

if (!(Test-Path $prompt)) {
  Write-Error "Prompt no encontrado: $prompt"
  exit 1
}
if (!(Test-Path $app)) {
  Write-Error "Script app.py no encontrado: $app"
  exit 1
}

Write-Host "✅ Ejecutando Plan 4..."
python $app $prompt
