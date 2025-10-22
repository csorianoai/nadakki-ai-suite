# patch_analisis_financiero.ps1
# 🚀 Parche seguro para agents/contabilidad/analisis_financiero.py
# 1) Backup
Copy-Item .\agents\contabilidad\analisis_financiero.py .\agents\contabilidad\analisis_financiero.bak

# 2) Cargar contenido
$content = Get-Content .\agents\contabilidad\analisis_financiero.py -Raw

# 3) Reemplazar RepositoryStub
$content = $content -replace 'class RepositoryStub:[\s\S]*?self\.repository = RepositoryStub\(\)', @'
class RepositoryStub:
            async def get_saldos_cuentas(self, tenant_id, fecha):
                # Claves compatibles con el mapeo actual y valores genéricos no-cero
                return {
                    "1110001": 9500000,   # cartera_creditos
                    "1120001": 1200000,   # inversiones
                    "1100001": 800000,    # disponible
                    "2110001": 7000000,   # depositos_publico
                    "2120001": 500000,    # obligaciones_financieras
                    "3110001": 2500000,   # capital_social
                    "3120001": 300000,    # reservas
                    "3130001": 450000,    # utilidades_retenidas
                    "4110001": 1500000,   # ingresos_operativos
                    "5110001": 900000,    # gastos_operativos
                    "5120001": 60000      # provision_cartera
                }
            async def get_transacciones_periodo(self, tenant_id, fecha_inicio, fecha_fin):
                return [{"monto": 1000, "tipo": "ingreso"}, {"monto": 500, "tipo": "egreso"}]
            async def get_flujo_caja_historico(self, tenant_id, meses):
                return [{"mes": i, "flujo": 100000 + i*5000} for i in range(meses)]

        self.repository = RepositoryStub()
'@

# 4) Endurecer _generar_predicciones_ml
$content = [regex]::Replace($content,
'async\s+def\s+_generar_predicciones_ml\([^\)]*\):[\s\S]*?return\s+\{[\s\S]*?\}\s*$',
@'
async def _generar_predicciones_ml(self, datos_financieros: Dict[str, Any]) -> Dict[str, Any]:
        """Genera predicciones usando machine learning (siempre retorna llaves esperadas)"""
        if not self.config.ml_predictions:
            return {"ml_habilitado": False, "predicciones_flujo_caja": [], "prediccion_roa": None}

        try:
            features = np.array([
                float(datos_financieros.get("ingresos_operativos", 0.0)),
                float(datos_financieros.get("gastos_operativos", 0.0)),
                float(datos_financieros.get("provision_cartera", 0.0)),
                float(datos_financieros.get("activos_totales", 0.0)),
                float(datos_financieros.get("patrimonio_total", 0.0)),
                float(datos_financieros.get("depositos_publico", 0.0))
            ])

            predicciones_flujo = self.ml_engine.predecir_flujo_caja(features, 12) if self.ml_engine.modelos_entrenados else []

            prediccion_roa = None
            if self.ml_engine.modelos_entrenados:
                features_roa = np.array([
                    float(datos_financieros.get("utilidad_neta", 0.0)),
                    float(datos_financieros.get("activos_totales", 0.0)),
                    float(datos_financieros.get("ingresos_operativos", 0.0)),
                    float(datos_financieros.get("gastos_operativos", 0.0)),
                    float(datos_financieros.get("cartera_creditos", 0.0))
                ]).reshape(1, -1)
                features_roa_scaled = self.ml_engine.scalers["roa"].transform(features_roa)
                roa_pred = self.ml_engine.modelos["prediccion_roa"].predict(features_roa_scaled)[0]
                prediccion_roa = {"roa_predicho_12_meses": float(roa_pred), "variacion_esperada": None, "confianza": 0.82}

            return {
                "ml_habilitado": True,
                "predicciones_flujo_caja": [
                    {
                        "periodo": p.periodo,
                        "flujo_predicho": float(p.flujo_predicho),
                        "intervalo_confianza": [float(p.intervalo_confianza_inferior), float(p.intervalo_confianza_superior)],
                        "probabilidad_exactitud": float(p.probabilidad_exactitud)
                    } for p in predicciones_flujo
                ],
                "prediccion_roa": prediccion_roa,
                "modelo_version": "2.0.0",
                "fecha_entrenamiento": datetime.now().isoformat(),
                "precision_historica": 0.85
            }

        except Exception as e:
            self.logger.error(f"Error en predicciones ML: {e}")
            return {"ml_habilitado": True, "predicciones_flujo_caja": [], "prediccion_roa": None, "error": str(e)}
'@, 'Multiline')

# 5) Endurecer _detectar_anomalias_financieras
$content = [regex]::Replace($content,
'def\s+_detectar_anomalias_financieras\([^\)]*\):[\s\S]*?return\s+\{[^\}]*\}\s*$',
@'
def _detectar_anomalias_financieras(self, ratios: List[RatioFinanciero]) -> Dict[str, Any]:
        """Detecta anomalías con ML y reglas; tolerante a vacío"""
        try:
            if not ratios:
                return {"anomalias_detectadas": False, "deteccion_ml": {"anomalias_detectadas": False, "score_anomalia": 0, "nivel_riesgo": "BAJO", "recomendaciones": []}, "anomalias_reglas_negocio": [], "total_anomalias": 0, "nivel_riesgo_general": "BAJO", "recomendaciones_inmediatas": []}

            valores_ratios = np.array([r.valor_actual for r in ratios], dtype=float)
            if valores_ratios.size == 0:
                return {"anomalias_detectadas": False, "deteccion_ml": {"anomalias_detectadas": False, "score_anomalia": 0, "nivel_riesgo": "BAJO", "recomendaciones": []}, "anomalias_reglas_negocio": [], "total_anomalias": 0, "nivel_riesgo_general": "BAJO", "recomendaciones_inmediatas": []}

            resultado_ml = self.ml_engine.detectar_anomalias(valores_ratios)
            anomalias_reglas = []
            for ratio in ratios:
                if ratio.categoria == "Liquidez" and ratio.valor_actual < self.config.umbrales_alerta.get("liquidez_minima", 1.2):
                    anomalias_reglas.append({"tipo": "liquidez_critica", "ratio": ratio.nombre, "valor_actual": ratio.valor_actual, "umbral": self.config.umbrales_alerta["liquidez_minima"], "severidad": "CRITICA"})

            if resultado_ml.get("anomalias_detectadas") or anomalias_reglas:
                self.metrics["anomalias_detectadas"] += 1

            return {
                "anomalias_detectadas": bool(resultado_ml.get("anomalias_detectadas")) or len(anomalias_reglas) > 0,
                "deteccion_ml": resultado_ml,
                "anomalias_reglas_negocio": anomalias_reglas,
                "total_anomalias": len(anomalias_reglas),
                "nivel_riesgo_general": resultado_ml.get("nivel_riesgo", "BAJO"),
                "recomendaciones_inmediatas": resultado_ml.get("recomendaciones", [])
            }
        except Exception as e:
            self.logger.error(f"Error detectando anomalías: {e}")
            return {"anomalias_detectadas": False, "deteccion_ml": {"anomalias_detectadas": False}, "anomalias_reglas_negocio": [], "total_anomalias": 0, "nivel_riesgo_general": "BAJO", "recomendaciones_inmediatas": [], "error": str(e)}
'@, 'Multiline')

# 6) Guardar cambios
Set-Content .\agents\contabilidad\analisis_financiero.py -Value $content -Encoding UTF8

Write-Host "✅ Parche aplicado a analisis_financiero.py"
