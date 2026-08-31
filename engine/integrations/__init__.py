"""
Cerberus Memory Intelligence - External Integration Adapters
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)

Phase P2: Lifecycle bridges between Cerberus and orchestrator clients
(Gemini Maestro / Maestri canvas, AI Orchestrator event stream).
"""

from engine.integrations.orchestrator import OrchestratorAdapter
from engine.integrations.maestri import (
    detect_project_from_path,
    format_agent_session_pack,
)

__all__ = [
    "OrchestratorAdapter",
    "detect_project_from_path",
    "format_agent_session_pack",
]
