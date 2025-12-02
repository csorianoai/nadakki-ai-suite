import pytest
from agents.marketing import content_generator_v3

def test_generate_content():
    content = content_generator_v3.generate("nuevo producto")
    assert isinstance(content, str)
    assert len(content) > 10
