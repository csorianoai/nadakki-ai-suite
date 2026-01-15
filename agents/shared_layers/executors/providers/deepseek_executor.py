import time
from openai import OpenAI
from ..base_executor import BaseExecutor, GenerationRequest, GenerationResponse

class DeepSeekExecutor(BaseExecutor):
    def _initialize_client(self):
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com/v1")
    
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        start = time.time()
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        response = self.client.chat.completions.create(model="deepseek-chat", messages=messages, max_tokens=request.max_tokens, temperature=request.temperature)
        latency = (time.time() - start) * 1000
        usage = response.usage
        cost = round((usage.prompt_tokens/1e6)*0.14 + (usage.completion_tokens/1e6)*0.28, 6)
        return GenerationResponse(content=response.choices[0].message.content, model_used="deepseek-chat", input_tokens=usage.prompt_tokens, output_tokens=usage.completion_tokens, total_tokens=usage.total_tokens, latency_ms=latency, cost_usd=cost, finish_reason=response.choices[0].finish_reason, metadata={"id": response.id})
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        return round((input_tokens/1e6)*0.14 + (output_tokens/1e6)*0.28, 6)
