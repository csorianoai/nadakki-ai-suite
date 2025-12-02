import pytest
from agents.marketing import contentperformanceia

def test_performance_metrics():
    metrics = contentperformanceia.evaluate("campaña test")
    assert isinstance(metrics, dict)
    assert "engagement" in metrics
