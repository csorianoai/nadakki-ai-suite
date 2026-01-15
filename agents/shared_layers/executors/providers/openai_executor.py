import time
from openai import OpenAI
from ..base_executor import BaseExecutor, GenerationRequest, GenerationResponse

class OpenAIExecutor(BaseExecutor):
    def _initialize_client(self):
        self.client = OpenAI(api_key=self.api_key)
    
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        start = time.time()
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        response = self.client.chat.completions.create(model=request.model, messages=messages, max_tokens=request.max_tokens, temperature=request.temperature)
        latency = (time.time() - start) * 1000
        usage = response.usage
        pricing = {"gpt-4o": {"input": 2.50, "output": 10.00}, "gpt-4o-mini": {"input": 0.15, "output": 0.60}}
        p = pricing.get(request.model, pricing["gpt-4o-mini"])
        cost = round((usage.prompt_tokens/1e6)*p["input"] + (usage.completion_tokens/1e6)*p["output"], 6)
        return GenerationResponse(content=response.choices[0].message.content, model_used=request.model, input_tokens=usage.prompt_tokens, output_tokens=usage.completion_tokens, total_tokens=usage.total_tokens, latency_ms=latency, cost_usd=cost, finish_reason=response.choices[0].finish_reason, metadata={"id": response.id})
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        pricing = {"gpt-4o": {"input": 2.50, "output": 10.00}, "gpt-4o-mini": {"input": 0.15, "output": 0.60}}
        p = pricing.get(model, pricing["gpt-4o-mini"])
        return round((input_tokens/1e6)*p["input"] + (output_tokens/1e6)*p["output"], 6)
