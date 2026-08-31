"""
Cerberus Memory Intelligence - Data Models & Schema Contracts
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
import datetime
import json


class CandidateStatus(str, Enum):
    CAPTURED = "CAPTURED"
    CANDIDATE = "CANDIDATE"
    VERIFIED = "VERIFIED"
    CANONICAL = "CANONICAL"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"
    ARCHIVED = "ARCHIVED"
    CONFLICT = "CONFLICT"
    QUARANTINED = "QUARANTINED"


@dataclass
class Candidate:
    candidate_id: str
    project_id: str
    type: str
    title: str
    content: str
    source: str
    source_path: Optional[str]
    task_id: str
    agent: str
    created_at: str
    confidence: float
    authority_hint: str
    fingerprint: str
    status: CandidateStatus = CandidateStatus.CANDIDATE
    secret_findings: List[str] = field(default_factory=list)
    canonical_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = dict(self.__dict__)
        result["status"] = self.status.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Candidate":
        values = dict(data)
        values["status"] = CandidateStatus(values["status"])
        return cls(**values)


class SourceType(str, Enum):
    GOVERNANCE = "governance"
    CANONICAL_ADR = "canonical_adr"
    ARCHITECTURE = "architecture"
    BUSINESS_RULE = "business_rule"
    PROJECT_STATE = "project_state"
    HANDOVER = "handover"
    LEARNING = "learning"
    WIKI = "wiki"
    TEMPLATE = "template"
    SPEC = "spec"
    RAW_OBSERVATION = "raw_observation"
    UNKNOWN = "unknown"


class AuthorityLevel(int, Enum):
    PO_DECISION = 100
    CANONICAL_ADR = 90
    GOVERNANCE = 85
    APPROVED_QA = 80
    ARCHITECTURE = 75
    LEARNING = 70
    BUSINESS_RULE = 70
    PROJECT_STATE = 65
    HANDOVER = 60
    WIKI = 50
    RAW_OBSERVATION = 30
    UNKNOWN = 10


class MemoryStatus(str, Enum):
    ACTIVE = "ativo"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"
    DRAFT = "draft"
    PROPOSAL = "proposta"


@dataclass
class MemoryItem:
    memory_id: str
    project_id: str  # e.g., 'canteirohub', 'biolar', 'helpdev', 'dm-erp', '_global'
    source_path: str
    source_type: SourceType
    title: str
    authority_level: int = AuthorityLevel.WIKI.value
    tags: List[str] = field(default_factory=list)
    snippet: str = ""
    full_text: str = ""
    updated_at: str = ""
    status: MemoryStatus = MemoryStatus.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "project_id": self.project_id,
            "source_path": self.source_path,
            "source_type": self.source_type.value if isinstance(self.source_type, SourceType) else str(self.source_type),
            "title": self.title,
            "authority_level": self.authority_level,
            "tags": self.tags,
            "snippet": self.snippet,
            "updated_at": self.updated_at,
            "status": self.status.value if isinstance(self.status, MemoryStatus) else str(self.status),
            "metadata": self.metadata,
        }


@dataclass
class SearchResult:
    item: MemoryItem
    lexical_score: float
    authority_boost: float
    final_score: float
    matched_snippets: List[str] = field(default_factory=list)
    semantic_score: float = 0.0
    rrf_score: float = 0.0
    lexical_rank: Optional[int] = None
    semantic_rank: Optional[int] = None
    search_mode: str = "lexical"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.item.memory_id,
            "project_id": self.item.project_id,
            "source_path": self.item.source_path,
            "source_type": self.item.source_type.value if isinstance(self.item.source_type, SourceType) else str(self.item.source_type),
            "title": self.item.title,
            "authority_level": self.item.authority_level,
            "final_score": round(self.final_score, 4),
            "lexical_score": round(self.lexical_score, 4),
            "semantic_score": round(self.semantic_score, 4),
            "rrf_score": round(self.rrf_score, 6),
            "lexical_rank": self.lexical_rank,
            "semantic_rank": self.semantic_rank,
            "search_mode": self.search_mode,
            "authority_boost": round(self.authority_boost, 4),
            "tags": self.item.tags,
            "snippet": self.matched_snippets[0] if self.matched_snippets else self.item.snippet,
            "updated_at": self.item.updated_at,
        }


@dataclass
class ContextPack:
    project_id: str
    task_summary: str
    role: str
    mandatory_rules: List[MemoryItem] = field(default_factory=list)
    relevant_decisions: List[MemoryItem] = field(default_factory=list)
    relevant_architecture: List[MemoryItem] = field(default_factory=list)
    relevant_learnings: List[MemoryItem] = field(default_factory=list)
    recent_handoff: List[MemoryItem] = field(default_factory=list)
    token_estimate: int = 0

    def to_markdown(self) -> str:
        lines = []
        lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"🧠 CERBERUS CONTEXT PACK — PROJECT: {self.project_id.upper()} | ROLE: {self.role.upper()}")
        lines.append(f"TASK: {self.task_summary}")
        lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

        if self.mandatory_rules:
            lines.append("### 🔒 1. REGRAS MANDATÓRIAS & GOVERNANÇA")
            for item in self.mandatory_rules:
                lines.append(f"- **{item.title}** (`{item.source_path}`)")
                if item.snippet:
                    lines.append(f"  > {item.snippet.strip()}")
            lines.append("")

        if self.relevant_decisions:
            lines.append("### 🏛️ 2. DECISÕES ARQUITETURAIS RELEVANTES (ADRs)")
            for item in self.relevant_decisions:
                lines.append(f"- **{item.title}** (`{item.source_path}` · Auth: {item.authority_level})")
                if item.snippet:
                    lines.append(f"  > {item.snippet.strip()}")
            lines.append("")

        if self.relevant_architecture:
            lines.append("### 📐 3. ARQUITETURA & PADRÕES TÉCNICOS")
            for item in self.relevant_architecture:
                lines.append(f"- **{item.title}** (`{item.source_path}`)")
                if item.snippet:
                    lines.append(f"  > {item.snippet.strip()}")
            lines.append("")

        if self.relevant_learnings:
            lines.append("### 💡 4. LIÇÕES APRENDIDAS & GOTCHAS")
            for item in self.relevant_learnings:
                lines.append(f"- **{item.title}** (`{item.source_path}`)")
                if item.snippet:
                    lines.append(f"  > {item.snippet.strip()}")
            lines.append("")

        if self.recent_handoff:
            lines.append("### 🤝 5. CONTINUIDADE & ÚLTIMO HANDOVER")
            for item in self.recent_handoff:
                lines.append(f"- **{item.title}** (`{item.source_path}`)")
                if item.snippet:
                    lines.append(f"  > {item.snippet.strip()}")
            lines.append("")

        lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        return "\n".join(lines)
