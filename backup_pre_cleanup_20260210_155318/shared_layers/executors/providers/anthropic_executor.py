import time
import anthropic
from ..base_executor import BaseExecutor, GenerationRequest, GenerationResponse

class AnthropicExecutor(BaseExecutor):
    def _initialize_client(self):
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        start = time.time()
        response = self.client.messages.create(model=request.model, max_tokens=request.max_tokens, system=request.system_prompt or "You are a helpful assistant.", messages=[{"role": "user", "content": request.prompt}], temperature=request.temperature)
        latency = (time.time() - start) * 1000
        usage = response.usage
        pricing = {"claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00}, "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25}}
        p = pricing.get(request.model, pricing["claude-3-haiku-20240307"])
        cost = round((usage.input_tokens/1e6)*p["input"] + (usage.output_tokens/1e6)*p["output"], 6)
        return GenerationResponse(content=response.content[0].text, model_used=request.model, input_tokens=usage.input_tokens, output_tokens=usage.output_tokens, total_tokens=usage.input_tokens + usage.output_tokens, latency_ms=latency, cost_usd=cost, finish_reason=response.stop_reason, metadata={"id": response.id})
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        pricing = {"claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00}, "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25}}
        p = pricing.get(model, pricing["claude-3-haiku-20240307"])
        return round((input_tokens/1e6)*p["input"] + (output_tokens/1e6)*p["output"], 6)
