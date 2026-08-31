"""
Cerberus Memory Intelligence - High-Level Retrieval & Context Pack Service
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from engine.models import MemoryItem, SearchResult, ContextPack, SourceType, AuthorityLevel
from engine.index import SQLiteMemoryIndex


class CerberusMemoryService:
    def __init__(self, index: Optional[SQLiteMemoryIndex] = None):
        self.index = index or SQLiteMemoryIndex()

    def search(
        self,
        query: str,
        project_id: Optional[str] = None,
        source_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[SearchResult]:
        return self.index.search(
            query=query,
            project_id=project_id,
            source_types=source_types,
            limit=limit,
            include_global=True
        )

    def get_decisions(self, project_id: Optional[str] = None, limit: int = 10) -> List[SearchResult]:
        return self.index.search(
            query="ADR decisao arquitetura",
            project_id=project_id,
            source_types=[SourceType.CANONICAL_ADR.value],
            limit=limit,
            include_global=True,
            min_authority=AuthorityLevel.CANONICAL_ADR.value
        )

    def get_learnings(self, topic: Optional[str] = None, project_id: Optional[str] = None, limit: int = 10) -> List[SearchResult]:
        q = f"aprendizado licao gotcha {topic}" if topic else "aprendizado licao diretrizes"
        return self.index.search(
            query=q,
            project_id=project_id,
            source_types=[SourceType.LEARNING.value],
            limit=limit,
            include_global=True
        )

    def get_project_context(self, project_id: str) -> Dict[str, Any]:
        """
        Retrieves top-level index and state for a specific project.
        """
        project_items = self.index.search(
            query=f"{project_id} visao geral status arquitetura",
            project_id=project_id,
            limit=5,
            include_global=False
        )
        return {
            "project_id": project_id,
            "items": [item.to_dict() for item in project_items]
        }

    def get_recent_handoff(self, project_id: Optional[str] = None) -> List[SearchResult]:
        return self.index.search(
            query="handover continuidade estado atual",
            project_id=project_id,
            source_types=[SourceType.HANDOVER.value],
            limit=3,
            include_global=True
        )

    def build_context_pack(
        self,
        project_id: str,
        task_summary: str,
        role: str = "DEVELOPER",
        max_tokens: int = 1500
    ) -> ContextPack:
        """
        Constructs a compact, budget-aware Context Pack tailored to a specific task and role.
        """
        # 1. Mandatory Rules (Global Governance & Security)
        gov_results = self.index.search(
            query="governance modelo routing autoridade",
            project_id="_global",
            source_types=[SourceType.GOVERNANCE.value],
            limit=2
        )
        mandatory_rules = [r.item for r in gov_results]

        # 2. Relevant Decisions (ADRs matching task summary)
        adr_results = self.index.search(
            query=f"{task_summary} ADR decisao",
            project_id=project_id,
            source_types=[SourceType.CANONICAL_ADR.value],
            limit=3,
            min_authority=AuthorityLevel.CANONICAL_ADR.value
        )
        relevant_decisions = [r.item for r in adr_results]

        # 3. Relevant Architecture
        arch_results = self.index.search(
            query=f"{task_summary} arquitetura stack banco",
            project_id=project_id,
            source_types=[SourceType.ARCHITECTURE.value, SourceType.WIKI.value],
            limit=2
        )
        relevant_architecture = [r.item for r in arch_results]

        # 4. Relevant Learnings & Gotchas
        learning_results = self.index.search(
            query=f"{task_summary} gotchas gotcha erro licao",
            project_id=project_id,
            source_types=[SourceType.LEARNING.value],
            limit=2
        )
        relevant_learnings = [r.item for r in learning_results]

        # 5. Recent Handoff
        handoff_results = self.get_recent_handoff(project_id=project_id)
        recent_handoff = [r.item for r in handoff_results[:1]]

        # Estimate tokens (~4 chars per token)
        total_chars = sum(len(item.snippet) + len(item.title) for item in (
            mandatory_rules + relevant_decisions + relevant_architecture + relevant_learnings + recent_handoff
        ))
        token_estimate = total_chars // 4

        return ContextPack(
            project_id=project_id,
            task_summary=task_summary,
            role=role,
            mandatory_rules=mandatory_rules,
            relevant_decisions=relevant_decisions,
            relevant_architecture=relevant_architecture,
            relevant_learnings=relevant_learnings,
            recent_handoff=recent_handoff,
            token_estimate=token_estimate
        )
