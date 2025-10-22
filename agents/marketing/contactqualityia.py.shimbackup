# agents/contact_quality.py - ContactQualityIA Agent
import time
from typing import Dict, List
from datetime import datetime, timedelta
import sys
sys.path.append('..')
from schemas.canonical import ContactQualityInput, ContactQualityOutput

class ContactQualityIA:
    def __init__(self, tenant_id: str, config: Dict = None):
        self.tenant_id = tenant_id
        self.agent_id = 'contact_quality_ia'
        self.config = config or self._default_config()
        
        # Ventanas horarias por región
        self.time_windows = {
            'DO': ['09:00-11:00', '14:00-16:00', '18:00-20:00'],
            'US': ['10:00-12:00', '15:00-17:00', '19:00-21:00'],
            'latam': ['09:00-11:00', '14:00-16:00', '18:00-20:00']
        }
        
        # Scoring por canal basado en histórico
        self.channel_weights = {
            'phone': 1.0,
            'whatsapp': 0.9,
            'email': 0.7
        }
    
    def _default_config(self) -> Dict:
        return {
            'timezone': 'America/Santo_Domingo',
            'min_contactability': 0.3,
            'script_variants': {
                'A': 'professional',
                'B': 'friendly', 
                'C': 'urgent'
            }
        }
    
    def _analyze_contact_history(self, history: List) -> Dict:
        """Analiza histórico de contacto por canal"""
        if not history:
            return {'phone': 0.5, 'email': 0.5, 'whatsapp': 0.5}
        
        channel_stats = {}
        for h in history:
            channel = h.channel
            if channel not in channel_stats:
                channel_stats[channel] = {'total': 0, 'success': 0}
            
            channel_stats[channel]['total'] += 1
            if h.outcome in ['answered', 'opened', 'clicked']:
                channel_stats[channel]['success'] += 1
        
        # Calcular tasa de éxito por canal
        scores = {}
        for channel, stats in channel_stats.items():
            scores[channel] = stats['success'] / stats['total'] if stats['total'] > 0 else 0.5
        
        # Defaults para canales sin histórico
        for channel in ['phone', 'email', 'whatsapp']:
            if channel not in scores:
                scores[channel] = 0.5
        
        return scores
    
    def _select_best_channel(self, channel_scores: Dict) -> str:
        """Selecciona mejor canal basado en scores"""
        return max(channel_scores.items(), key=lambda x: x[1])[0]
    
    def _get_time_window(self, region: str) -> str:
        """Obtiene ventana horaria según región"""
        current_hour = datetime.now().hour
        
        windows = self.time_windows.get(region, self.time_windows['latam'])
        
        # Seleccionar ventana según hora actual
        if 9 <= current_hour < 12:
            return windows[0]
        elif 14 <= current_hour < 17:
            return windows[1]
        else:
            return windows[2]
    
    def _select_script_variant(self, lead_age: int, industry: str) -> str:
        """Selecciona variante de script según perfil"""
        if lead_age and lead_age > 50:
            return 'A'  # Profesional para mayores
        elif industry and industry.lower() in ['tech', 'startup']:
            return 'B'  # Amigable para tech
        else:
            return 'C'  # Urgente para general
    
    def _calculate_contactability(self, channel_scores: Dict, lead) -> float:
        """Calcula score de contactabilidad general"""
        # Promedio ponderado de canales
        base_score = sum(
            channel_scores[ch] * self.channel_weights.get(ch, 0.5) 
            for ch in channel_scores
        ) / len(channel_scores)
        
        # Ajustar por eventos recientes
        if lead.lead.events:
            recent_events = [e for e in lead.lead.events 
                           if (datetime.utcnow() - e.ts).days < 7]
            if recent_events:
                base_score += 0.1  # Boost por engagement reciente
        
        return min(1.0, base_score)
    
    def _recommend_action(self, contactability: float, best_channel: str) -> str:
        """Recomienda acción basada en contactabilidad"""
        if contactability >= 0.7:
            return 'call_now' if best_channel == 'phone' else 'send_email'
        elif contactability >= 0.4:
            return 'schedule'
        else:
            return 'send_email'
    
    async def execute(self, input_data: ContactQualityInput) -> ContactQualityOutput:
        start = time.perf_counter()
        
        if input_data.lead.tenant_id != self.tenant_id:
            raise ValueError(f"Tenant mismatch: {input_data.lead.tenant_id} != {self.tenant_id}")
        
        # Analizar histórico
        channel_scores = self._analyze_contact_history(input_data.contact_history)
        
        # Seleccionar mejor canal
        best_channel = self._select_best_channel(channel_scores)
        
        # Obtener ventana horaria
        region = input_data.lead.persona.get('region', 'latam')
        time_window = self._get_time_window(region)
        
        # Seleccionar script
        script = self._select_script_variant(
            input_data.lead.attributes.age,
            input_data.lead.attributes.industry
        )
        
        # Calcular contactabilidad
        contactability = self._calculate_contactability(channel_scores, input_data)
        
        # Recomendar acción
        action = self._recommend_action(contactability, best_channel)
        
        latency_ms = max(1, int((time.perf_counter() - start) * 1000))
        
        return ContactQualityOutput(
            lead_id=input_data.lead.lead_id,
            contactability_score=round(contactability, 3),
            best_channel=best_channel,
            best_time_window=time_window,
            script_variant=script,
            next_action=action,
            latency_ms=latency_ms,
            tenant_id=self.tenant_id
        )

def create_agent_instance(tenant_id: str, config: Dict = None):
    return ContactQualityIA(tenant_id, config)