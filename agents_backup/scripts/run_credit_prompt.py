# run_credit_prompt.py

with open("C:/Nadakki/Prompts/credit-module-status-check.md", "r", encoding="utf-8") as f:
    prompt = f.read()

# Replace this with your actual GPT agent instance
# Example:
# from your_project.agent_module import gpt_agent
# response = gpt_agent.run(prompt)

response = f"Simulated response to prompt: {prompt[:100]}..."  # TEMP placeholder
print(response)
