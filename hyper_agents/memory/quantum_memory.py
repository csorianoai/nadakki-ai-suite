"""
NADAKKI AI SUITE - QUANTUM MEMORY
Sistema de memoria vectorial semántica independiente.
Soporta múltiples backends: en-memoria, SQLite, Redis, etc.
"""

import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import math

# Importar tipos locales
from enum import Enum


class MemoryType(Enum):
    """Tipos de memoria para el sistema"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


# ============================================================================
# MEMORY ENTRY
# ============================================================================

@dataclass
class MemoryEntry:
    """Entrada individual de memoria"""
    key: str
    content: Dict[str, Any]
    memory_type: MemoryType
    importance: float
    embedding: Optional[List[float]] = None
    tags: List[str] = field(default_factory=list)
    access_count: int = 0
    last_accessed: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "importance": self.importance,
            "tags": self.tags,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MemoryEntry":
        return cls(
            key=data["key"],
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            importance=data["importance"],
            tags=data.get("tags", []),
            access_count=data.get("access_count", 0),
            last_accessed=data.get("last_accessed", datetime.utcnow().isoformat()),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            expires_at=data.get("expires_at"),
            metadata=data.get("metadata", {})
        )


# ============================================================================
# SIMPLE EMBEDDER (Sin dependencias externas)
# ============================================================================

class SimpleEmbedder:
    """
    Generador de embeddings simple basado en TF-IDF.
    No requiere dependencias externas como sentence-transformers.
    """
    
    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_count = 0
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenización simple"""
        import re
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def _hash_token(self, token: str, dim: int) -> int:
        """Hash de token a dimensión específica"""
        return int(hashlib.md5(token.encode()).hexdigest(), 16) % dim
    
    def embed(self, text: str) -> List[float]:
        """
        Genera embedding para texto.
        Usa hashing trick para mantener dimensión fija.
        """
        tokens = self._tokenize(text)
        
        if not tokens:
            return [0.0] * self.dimension
        
        # Crear vector usando hashing trick
        vector = [0.0] * self.dimension
        
        # Contar frecuencias
        freq = defaultdict(int)
        for token in tokens:
            freq[token] += 1
        
        # TF-IDF aproximado con hashing
        for token, count in freq.items():
            idx = self._hash_token(token, self.dimension)
            tf = count / len(tokens)
            # IDF aproximado (usando log del hash)
            idf = 1.0 + math.log(1 + self._hash_token(token, 1000) / 100)
            vector[idx] += tf * idf
        
        # Normalizar
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    def similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcula similitud coseno entre dos vectores"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot / (norm1 * norm2)


# ============================================================================
# QUANTUM MEMORY
# ============================================================================

class QuantumMemory:
    """
    Sistema de memoria vectorial semántica.
    
    Características:
    - Búsqueda semántica por similitud
    - Múltiples tipos de memoria
    - Decay temporal (olvido gradual)
    - Consolidación de memoria
    - Multi-tenant
    """
    
    def __init__(
        self, 
        tenant_id: str = "default", 
        agent_id: str = "default",
        embedding_dim: int = 128,
        max_memories: int = 1000
    ):
        self.tenant_id = tenant_id
        self.agent_id = agent_id
        self.embedding_dim = embedding_dim
        self.max_memories = max_memories
        
        # Almacenamiento por tipo de memoria
        self.memories: Dict[MemoryType, Dict[str, MemoryEntry]] = {
            mt: {} for mt in MemoryType
        }
        
        # Índice de embeddings para búsqueda rápida
        self.embedding_index: Dict[str, List[float]] = {}
        
        # Embedder
        self.embedder = SimpleEmbedder(embedding_dim)
        
        # Estadísticas
        self.stats = {
            "total_stores": 0,
            "total_retrieves": 0,
            "cache_hits": 0,
            "consolidations": 0
        }
    
    async def store(
        self,
        key: str,
        content: Dict[str, Any],
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        importance: float = 0.5,
        tags: List[str] = None,
        ttl_hours: Optional[int] = None
    ) -> MemoryEntry:
        """
        Almacena información en memoria.
        
        Args:
            key: Identificador único
            content: Contenido a almacenar
            memory_type: Tipo de memoria
            importance: Importancia (0.0-1.0)
            tags: Etiquetas para búsqueda
            ttl_hours: Tiempo de vida en horas (None = sin expiración)
        
        Returns:
            MemoryEntry creada
        """
        # Generar embedding del contenido
        text_content = json.dumps(content, ensure_ascii=False)
        embedding = self.embedder.embed(text_content)
        
        # Calcular expiración
        expires_at = None
        if ttl_hours:
            expires_at = (datetime.utcnow() + timedelta(hours=ttl_hours)).isoformat()
        elif memory_type == MemoryType.SHORT_TERM:
            expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        
        # Crear entrada
        entry = MemoryEntry(
            key=f"{self.agent_id}_{key}",
            content=content,
            memory_type=memory_type,
            importance=max(0.0, min(1.0, importance)),
            embedding=embedding,
            tags=tags or [],
            expires_at=expires_at,
            metadata={
                "tenant_id": self.tenant_id,
                "agent_id": self.agent_id
            }
        )
        
        # Almacenar
        self.memories[memory_type][entry.key] = entry
        self.embedding_index[entry.key] = embedding
        
        # Verificar límite
        await self._enforce_limits()
        
        self.stats["total_stores"] += 1
        
        return entry
    
    async def get_context(
        self,
        query: str,
        limit: int = 5,
        memory_types: List[MemoryType] = None,
        min_similarity: float = 0.3,
        tags: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recupera contexto relevante basado en similitud semántica.
        
        Args:
            query: Consulta de búsqueda
            limit: Máximo de resultados
            memory_types: Tipos de memoria a buscar (None = todos)
            min_similarity: Similitud mínima requerida
            tags: Filtrar por tags
        
        Returns:
            Lista de memorias relevantes con scores
        """
        self.stats["total_retrieves"] += 1
        
        # Generar embedding de la consulta
        query_embedding = self.embedder.embed(query)
        
        # Tipos a buscar
        search_types = memory_types or list(MemoryType)
        
        # Buscar en todas las memorias
        candidates = []
        
        for mem_type in search_types:
            for key, entry in self.memories[mem_type].items():
                # Verificar expiración
                if entry.expires_at:
                    if datetime.fromisoformat(entry.expires_at) < datetime.utcnow():
                        continue
                
                # Filtrar por tags
                if tags and not any(t in entry.tags for t in tags):
                    continue
                
                # Calcular similitud
                if key in self.embedding_index:
                    similarity = self.embedder.similarity(
                        query_embedding, 
                        self.embedding_index[key]
                    )
                    
                    if similarity >= min_similarity:
                        # Ajustar por importancia y recencia
                        recency_factor = self._calculate_recency(entry.last_accessed)
                        adjusted_score = (
                            similarity * 0.6 + 
                            entry.importance * 0.3 + 
                            recency_factor * 0.1
                        )
                        
                        candidates.append({
                            "entry": entry,
                            "similarity": similarity,
                            "adjusted_score": adjusted_score
                        })
        
        # Ordenar por score ajustado
        candidates.sort(key=lambda x: x["adjusted_score"], reverse=True)
        
        # Actualizar accesos y retornar
        results = []
        for c in candidates[:limit]:
            entry = c["entry"]
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow().isoformat()
            
            results.append({
                "key": entry.key,
                "content": entry.content,
                "memory_type": entry.memory_type.value,
                "similarity": round(c["similarity"], 3),
                "score": round(c["adjusted_score"], 3),
                "tags": entry.tags
            })
        
        return results
    
    async def retrieve(
        self,
        key: str,
        memory_type: MemoryType = None
    ) -> Optional[MemoryEntry]:
        """Recupera memoria específica por key"""
        full_key = f"{self.agent_id}_{key}"
        
        if memory_type:
            return self.memories[memory_type].get(full_key)
        
        # Buscar en todos los tipos
        for mem_type in MemoryType:
            if full_key in self.memories[mem_type]:
                entry = self.memories[mem_type][full_key]
                entry.access_count += 1
                entry.last_accessed = datetime.utcnow().isoformat()
                return entry
        
        return None
    
    async def consolidate(self):
        """
        Consolida memorias de corto a largo plazo.
        Memorias importantes y frecuentemente accedidas se promueven.
        """
        promoted = 0
        
        for key, entry in list(self.memories[MemoryType.SHORT_TERM].items()):
            # Criterios de promoción
            should_promote = (
                entry.importance >= 0.7 and 
                entry.access_count >= 3
            ) or (
                entry.access_count >= 5
            )
            
            if should_promote:
                # Mover a largo plazo
                entry.memory_type = MemoryType.LONG_TERM
                entry.expires_at = None  # Sin expiración
                
                self.memories[MemoryType.LONG_TERM][key] = entry
                del self.memories[MemoryType.SHORT_TERM][key]
                promoted += 1
        
        self.stats["consolidations"] += 1
        
        return {"promoted": promoted, "timestamp": datetime.utcnow().isoformat()}
    
    async def forget(
        self,
        key: str = None,
        memory_type: MemoryType = None,
        older_than_hours: int = None
    ) -> int:
        """
        Elimina memorias.
        
        Args:
            key: Key específica a eliminar
            memory_type: Tipo específico a limpiar
            older_than_hours: Eliminar más antiguas que X horas
        
        Returns:
            Número de memorias eliminadas
        """
        deleted = 0
        
        types_to_clean = [memory_type] if memory_type else list(MemoryType)
        
        for mem_type in types_to_clean:
            keys_to_delete = []
            
            for k, entry in self.memories[mem_type].items():
                should_delete = False
                
                if key and k == f"{self.agent_id}_{key}":
                    should_delete = True
                elif older_than_hours:
                    created = datetime.fromisoformat(entry.created_at)
                    if datetime.utcnow() - created > timedelta(hours=older_than_hours):
                        should_delete = True
                
                if should_delete:
                    keys_to_delete.append(k)
            
            for k in keys_to_delete:
                del self.memories[mem_type][k]
                if k in self.embedding_index:
                    del self.embedding_index[k]
                deleted += 1
        
        return deleted
    
    def _calculate_recency(self, last_accessed: str) -> float:
        """Calcula factor de recencia (más reciente = mayor valor)"""
        try:
            accessed = datetime.fromisoformat(last_accessed)
            hours_ago = (datetime.utcnow() - accessed).total_seconds() / 3600
            # Decay exponencial
            return math.exp(-hours_ago / 24)  # 24h half-life
        except:
            return 0.5
    
    async def _enforce_limits(self):
        """Aplica límites de memoria, eliminando las menos importantes"""
        total = sum(len(m) for m in self.memories.values())
        
        if total <= self.max_memories:
            return
        
        # Recopilar todas las memorias con scores
        all_memories = []
        for mem_type, memories in self.memories.items():
            for key, entry in memories.items():
                recency = self._calculate_recency(entry.last_accessed)
                score = entry.importance * 0.5 + recency * 0.5
                all_memories.append((mem_type, key, score))
        
        # Ordenar por score (menor primero)
        all_memories.sort(key=lambda x: x[2])
        
        # Eliminar exceso
        to_remove = total - self.max_memories
        for mem_type, key, _ in all_memories[:to_remove]:
            del self.memories[mem_type][key]
            if key in self.embedding_index:
                del self.embedding_index[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de memoria"""
        memory_counts = {
            mt.value: len(self.memories[mt]) 
            for mt in MemoryType
        }
        
        return {
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "total_memories": sum(memory_counts.values()),
            "by_type": memory_counts,
            "embedding_dim": self.embedding_dim,
            "stats": self.stats
        }
    
    def export_memories(self) -> Dict[str, Any]:
        """Exporta todas las memorias para persistencia"""
        export = {
            "tenant_id": self.tenant_id,
            "agent_id": self.agent_id,
            "exported_at": datetime.utcnow().isoformat(),
            "memories": {}
        }
        
        for mem_type in MemoryType:
            export["memories"][mem_type.value] = [
                entry.to_dict() 
                for entry in self.memories[mem_type].values()
            ]
        
        return export
    
    def import_memories(self, data: Dict[str, Any]):
        """Importa memorias desde export"""
        for mem_type_str, entries in data.get("memories", {}).items():
            mem_type = MemoryType(mem_type_str)
            for entry_data in entries:
                entry = MemoryEntry.from_dict(entry_data)
                self.memories[mem_type][entry.key] = entry
                
                # Regenerar embedding
                text_content = json.dumps(entry.content, ensure_ascii=False)
                self.embedding_index[entry.key] = self.embedder.embed(text_content)
