import pytest
from agents.contabilidad import reportes_fiscales

def test_generate_report():
    report = reportes_fiscales.generate("Q3")
    assert isinstance(report, dict)
    assert "total_impuestos" in report
