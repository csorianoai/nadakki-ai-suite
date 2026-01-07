"""
AI Generation Router - Template and content generation using LLM
NADAKKI AI Suite v2.0
"""
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import asyncio
import os

router = APIRouter(prefix="/ai", tags=["AI Generation"])

# ═══════════════════════════════════════════════════════════════
# MODELOS
# ═══════════════════════════════════════════════════════════════

class TemplateGenerationRequest(BaseModel):
    objective: str = Field(..., description="Goal: convert, recover, reactivate, retain, upsell, onboard")
    channel: str = Field(..., description="Channel: email, sms, push, whatsapp, in-app")
    industry: str = Field(..., description="Industry: fintech, ecommerce, saas, healthcare")
    tone: str = Field(..., description="Tone: professional, friendly, urgent, casual")
    key_message: str = Field(..., description="Main message to convey")
    product_description: Optional[str] = ""
    cta: Optional[str] = "Learn More"
    additional_context: Optional[str] = ""
    tenant_id: str = "default"

class GeneratedTemplate(BaseModel):
    id: str
    subject: str
    preheader: str
    headline: str
    body: str
    cta_text: str
    cta_url: str
    footer: str
    metadata: Dict[str, Any]
    generated_at: datetime

class CopyRewriteRequest(BaseModel):
    original_text: str
    target_tone: str
    channel: str
    max_length: Optional[int] = None

class ABVariantRequest(BaseModel):
    original_content: Dict[str, Any]
    variation_type: str = "subject"  # subject, body, cta
    num_variants: int = 3

# ═══════════════════════════════════════════════════════════════
# AI GENERATION ENGINE
# ═══════════════════════════════════════════════════════════════

class AIGenerationEngine:
    """
    AI Content Generation Engine
    In production, this connects to Claude/GPT APIs
    For now, uses intelligent template-based generation
    """
    
    TEMPLATES = {
        "convert": {
            "email": {
                "subject_patterns": [
                    "{emoji} {key_message} - Limited Time Offer",
                    "Exclusive for you: {key_message}",
                    "Don't miss out on {key_message}"
                ],
                "body_patterns": [
                    "Hi {{name}},\n\nWe have something special for you. {key_message}\n\n{product_description}\n\nThis offer won't last long - take action today!\n\nBest regards,\n{{company_name}}",
                ]
            },
            "sms": {
                "body_patterns": [
                    "{{name}}, {key_message}! Act now: {{link}}",
                    "{emoji} {key_message} - Tap here: {{link}}"
                ]
            }
        },
        "recover": {
            "email": {
                "subject_patterns": [
                    "🛒 You left something behind!",
                    "Your cart is waiting for you",
                    "Complete your purchase - {key_message}"
                ],
                "body_patterns": [
                    "Hi {{name}},\n\nWe noticed you left some items in your cart. {key_message}\n\nYour items are still available, but they won't wait forever!\n\n{{cart_items}}\n\nComplete your purchase now and enjoy free shipping.\n\nSee you soon!"
                ]
            }
        },
        "reactivate": {
            "email": {
                "subject_patterns": [
                    "We miss you, {{name}}! 💔",
                    "It's been a while - {key_message}",
                    "Come back and see what's new"
                ],
                "body_patterns": [
                    "Hi {{name}},\n\nIt's been a while since we've seen you, and we wanted to reach out.\n\n{key_message}\n\nAs a special welcome back offer: {product_description}\n\nWe'd love to have you back!\n\nWarmly,\n{{company_name}}"
                ]
            }
        },
        "onboard": {
            "email": {
                "subject_patterns": [
                    "Welcome to {{company_name}}! 🎉",
                    "You're in! Here's what's next",
                    "Getting started with {{company_name}}"
                ],
                "body_patterns": [
                    "Hi {{name}},\n\nWelcome aboard! We're thrilled to have you join us.\n\n{key_message}\n\nHere's how to get started:\n1. Complete your profile\n2. Explore our features\n3. {product_description}\n\nNeed help? Our team is here for you 24/7.\n\nLet's do great things together!\n\n{{company_name}} Team"
                ]
            }
        }
    }
    
    EMOJIS = {
        "convert": ["🎯", "💰", "🚀", "✨"],
        "recover": ["🛒", "⏰", "💫", "🎁"],
        "reactivate": ["💝", "👋", "🌟", "💫"],
        "onboard": ["🎉", "👋", "🚀", "✨"],
        "retain": ["❤️", "🙏", "⭐", "🎊"],
        "upsell": ["📈", "💎", "⬆️", "🏆"]
    }
    
    TONE_MODIFIERS = {
        "professional": {"greeting": "Dear", "closing": "Best regards", "style": "formal"},
        "friendly": {"greeting": "Hey", "closing": "Cheers", "style": "casual"},
        "urgent": {"greeting": "Hi", "closing": "Act now", "style": "direct"},
        "casual": {"greeting": "Hi there", "closing": "Talk soon", "style": "relaxed"}
    }
    
    async def generate_template(self, request: TemplateGenerationRequest) -> GeneratedTemplate:
        """Generate a complete template based on parameters"""
        import random
        
        objective = request.objective
        channel = request.channel
        
        # Get templates for objective/channel
        templates = self.TEMPLATES.get(objective, self.TEMPLATES["convert"])
        channel_templates = templates.get(channel, templates.get("email", {}))
        
        # Select patterns
        subject_patterns = channel_templates.get("subject_patterns", ["{key_message}"])
        body_patterns = channel_templates.get("body_patterns", ["{key_message}"])
        
        # Get emoji
        emoji = random.choice(self.EMOJIS.get(objective, ["✨"]))
        
        # Get tone modifiers
        tone = self.TONE_MODIFIERS.get(request.tone, self.TONE_MODIFIERS["friendly"])
        
        # Generate subject
        subject = random.choice(subject_patterns).format(
            emoji=emoji,
            key_message=request.key_message
        )
        
        # Generate body
        body = random.choice(body_patterns).format(
            key_message=request.key_message,
            product_description=request.product_description or "Check out our latest offerings.",
            additional_context=request.additional_context or ""
        )
        
        # Apply tone
        if tone["style"] == "formal":
            body = body.replace("Hi {{name}}", "Dear {{name}}")
        
        # Generate preheader
        preheader = f"{request.key_message[:50]}..." if len(request.key_message) > 50 else request.key_message
        
        # Calculate predicted performance
        base_ctr = {"email": 15, "sms": 25, "push": 8, "whatsapp": 35, "in-app": 20}
        base_conversion = {"email": 5, "sms": 8, "push": 3, "whatsapp": 12, "in-app": 7}
        
        variance = random.uniform(0.8, 1.3)
        predicted_ctr = round(base_ctr.get(channel, 15) * variance, 1)
        predicted_conversion = round(base_conversion.get(channel, 5) * variance, 1)
        
        return GeneratedTemplate(
            id=f"gen_{uuid.uuid4().hex[:8]}",
            subject=subject,
            preheader=preheader,
            headline=request.key_message,
            body=body,
            cta_text=request.cta or "Learn More",
            cta_url="{{cta_url}}",
            footer="© {{year}} {{company_name}}. All rights reserved.",
            metadata={
                "objective": objective,
                "channel": channel,
                "industry": request.industry,
                "tone": request.tone,
                "predicted_ctr": predicted_ctr,
                "predicted_conversion": predicted_conversion,
                "word_count": len(body.split()),
                "reading_time": f"{max(1, len(body.split()) // 200)} min",
                "ai_model": "nadakki-gen-v2",
                "confidence_score": round(random.uniform(0.85, 0.98), 2)
            },
            generated_at=datetime.now()
        )
    
    async def rewrite_copy(self, request: CopyRewriteRequest) -> Dict[str, Any]:
        """Rewrite copy with different tone"""
        tone = self.TONE_MODIFIERS.get(request.target_tone, self.TONE_MODIFIERS["friendly"])
        
        # Simple tone transformation (in production, use LLM)
        rewritten = request.original_text
        
        if tone["style"] == "formal":
            rewritten = rewritten.replace("Hey", "Dear").replace("!", ".")
        elif tone["style"] == "urgent":
            rewritten = rewritten.upper() if len(rewritten) < 50 else rewritten + " ACT NOW!"
        
        if request.max_length and len(rewritten) > request.max_length:
            rewritten = rewritten[:request.max_length-3] + "..."
        
        return {
            "original": request.original_text,
            "rewritten": rewritten,
            "tone": request.target_tone,
            "channel": request.channel,
            "character_count": len(rewritten)
        }
    
    async def generate_ab_variants(self, request: ABVariantRequest) -> List[Dict[str, Any]]:
        """Generate A/B test variants"""
        variants = []
        original = request.original_content
        
        for i in range(request.num_variants):
            variant = original.copy()
            
            if request.variation_type == "subject" and "subject" in variant:
                prefixes = ["🔥 ", "⚡ ", "✨ ", "🎯 ", ""]
                suffixes = [" - Don't Miss Out!", " - Limited Time", " - Exclusive Offer", ""]
                variant["subject"] = f"{prefixes[i % len(prefixes)]}{original['subject']}{suffixes[i % len(suffixes)]}"
            
            elif request.variation_type == "cta" and "cta" in variant:
                ctas = ["Get Started", "Learn More", "Claim Now", "Unlock Access", "Start Free"]
                variant["cta"] = ctas[i % len(ctas)]
            
            variants.append({
                "variant_id": f"var_{chr(65+i)}",
                "content": variant,
                "predicted_lift": round((i + 1) * 3.5 + 5, 1)
            })
        
        return variants

# Engine instance
ai_engine = AIGenerationEngine()

# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@router.post("/generate-template", response_model=GeneratedTemplate)
async def generate_template(request: TemplateGenerationRequest):
    """Generate AI-powered template based on parameters"""
    try:
        template = await ai_engine.generate_template(request)
        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.post("/rewrite-copy")
async def rewrite_copy(request: CopyRewriteRequest):
    """Rewrite copy with different tone/style"""
    return await ai_engine.rewrite_copy(request)

@router.post("/ab-variants")
async def generate_ab_variants(request: ABVariantRequest):
    """Generate A/B test variants"""
    return await ai_engine.generate_ab_variants(request)

@router.post("/optimize-subject")
async def optimize_subject(
    subject: str = Body(...),
    channel: str = Body(default="email"),
    objective: str = Body(default="convert")
):
    """Optimize email/push subject line"""
    suggestions = [
        {"text": f"🔥 {subject}", "predicted_open_rate": 28.5},
        {"text": f"{subject} - Limited Time", "predicted_open_rate": 26.2},
        {"text": f"Don't miss: {subject}", "predicted_open_rate": 24.8},
        {"text": subject.upper() if len(subject) < 30 else subject, "predicted_open_rate": 22.1},
    ]
    return {
        "original": subject,
        "suggestions": suggestions,
        "best_recommendation": suggestions[0]
    }

@router.post("/personalize")
async def personalize_content(
    content: str = Body(...),
    user_data: Dict[str, Any] = Body(default={})
):
    """Personalize content with user data"""
    personalized = content
    
    for key, value in user_data.items():
        personalized = personalized.replace(f"{{{{{key}}}}}", str(value))
    
    return {
        "original": content,
        "personalized": personalized,
        "fields_replaced": list(user_data.keys())
    }
