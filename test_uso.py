# filepath: test_uso.py
import asyncio
from agents.marketing.content_generator_v3 import create_agent_instance, ContentGenerationInput

async def main():
    # Crear agente
    agent = create_agent_instance("tn_mi_banco")
    
    # Crear input
    input_data = ContentGenerationInput(
        tenant_id="tn_mi_banco",
        content_type="ad_copy",
        audience_segment="high_value",
        brand_tone="professional",
        key_message="Refinancia tu hipoteca con mejores tasas",
        language="es",
        jurisdiction="MX",
        variant_count=3
    )
    
    # Ejecutar
    output = await agent.execute(input_data)
    
    # Mostrar resultados
    print(f"\nGeneration ID: {output.generation_id}")
    print(f"Recommended: {output.recommended_variant}\n")
    
    for variant in output.variants:
        print(f"{variant.variant_id}: {variant.content}")
        print(f"  CTR: {variant.scores.estimated_ctr:.2%}")
        print(f"  Compliance: {variant.scores.compliance:.2f}\n")

if __name__ == "__main__":
    asyncio.run(main())