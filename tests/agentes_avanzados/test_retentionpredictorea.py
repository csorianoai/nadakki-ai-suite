import pytest
from agents.marketing import retentionpredictorea

def test_predict_retention():
    score = retentionpredictorea.predict(user_id=123)
    assert isinstance(score, float)
    assert 0 <= score <= 1
