import pytest
from datetime import datetime
from agents.contabilidad.analisis_financiero import AnalisisFinanciero

@pytest.mark.asyncio
async def test_output_structure():
    analizador = AnalisisFinanciero(tenant_id="test_tenant")
    resultado = await analizador.realizar_analisis_completo(datetime.now())
    assert "ratios_financieros" in resultado
    assert isinstance(resultado["ratios_financieros"], list)
    assert len(resultado["ratios_financieros"]) > 0
    assert "predicciones_ml" in resultado
    assert "deteccion_anomalias" in resultado
    assert "score_salud_financiera" in resultado
