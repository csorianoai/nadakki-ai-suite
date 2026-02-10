from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class GenerationRequest:
    prompt: str
    model: str
    max_tokens: int = 2000
    temperature: float = 0.7
    system_prompt: Optional[str] = None

@dataclass
class GenerationResponse:
    content: str
    model_used: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    cost_usd: float
    finish_reason: str = "stop"
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseExecutor(ABC):
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self): pass
    
    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResponse: pass
    
    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float: pass
