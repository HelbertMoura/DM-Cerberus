"""
Cerberus Memory Intelligence - Markdown & Frontmatter Parser
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from engine.models import MemoryItem, SourceType, AuthorityLevel, MemoryStatus


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Extracts YAML frontmatter from markdown content without external dependencies.
    """
    frontmatter = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()

            for line in fm_text.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip().lower()
                    val = val.strip()

                    # Handle list format [a, b, c]
                    if val.startswith("[") and val.endswith("]"):
                        items = [item.strip().strip("'\"") for item in val[1:-1].split(",") if item.strip()]
                        frontmatter[key] = items
                    else:
                        frontmatter[key] = val.strip("'\"")

    return frontmatter, body


def resolve_project_and_type(file_path: Path, root_path: Path) -> Tuple[str, SourceType, int]:
    """
    Determines project_id, source_type, and default authority_level based on path.
    """
    rel_path = file_path.relative_to(root_path).as_posix().lower()
    origin_path = file_path.resolve().as_posix().lower()
    file_name = file_path.name.lower()

    # Project ID detection
    project_id = "_global"
    is_explicit_global = rel_path.startswith("global/") or "global/" in rel_path
    is_governance_file = "ai-governance" in file_name or "model-routing" in file_name
    if is_explicit_global or is_governance_file:
        project_id = "_global"
    elif "projects/" in rel_path:
        parts = rel_path.split("projects/")[1].split("/")
        if parts:
            project_id = parts[0]
    elif "dm-erp" in origin_path or "canteirohub" in origin_path:
        project_id = "canteirohub"
    elif "biolar" in origin_path:
        project_id = "biolar"
    elif "helpdev" in origin_path:
        project_id = "helpdev"
    elif "dmpdv" in origin_path:
        project_id = "dmpdv"
    elif "apae" in origin_path:
        project_id = "apae-juatuba"

    # Source Type & Authority Level detection
    if "global/" in rel_path or "ai-governance" in file_name or "model-routing" in file_name:
        source_type = SourceType.GOVERNANCE
        authority = AuthorityLevel.GOVERNANCE.value
    elif file_name == "decisions.md" or "adr" in file_name:
        source_type = SourceType.CANONICAL_ADR
        authority = AuthorityLevel.CANONICAL_ADR.value
    elif file_name == "learnings.md":
        source_type = SourceType.LEARNING
        authority = AuthorityLevel.LEARNING.value
    elif file_name == "handover.md":
        source_type = SourceType.HANDOVER
        authority = AuthorityLevel.HANDOVER.value
    elif file_name == "project_state.md" or file_name == "status.md":
        source_type = SourceType.PROJECT_STATE
        authority = AuthorityLevel.PROJECT_STATE.value
    elif file_name == "architecture.md" or file_name == "arquitetura.md":
        source_type = SourceType.ARCHITECTURE
        authority = AuthorityLevel.ARCHITECTURE.value
    elif file_name == "business_rules.md":
        source_type = SourceType.BUSINESS_RULE
        authority = AuthorityLevel.BUSINESS_RULE.value
    elif "wiki/" in rel_path:
        source_type = SourceType.WIKI
        authority = AuthorityLevel.WIKI.value
    elif "templates/" in rel_path:
        source_type = SourceType.TEMPLATE
        authority = AuthorityLevel.WIKI.value
    else:
        source_type = SourceType.WIKI
        authority = AuthorityLevel.WIKI.value

    return project_id, source_type, authority


def parse_markdown_file(file_path: Path, root_path: Path) -> List[MemoryItem]:
    """
    Parses a markdown file into one or more MemoryItem chunks.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return []

    frontmatter, body = parse_frontmatter(content)
    project_id, source_type, default_authority = resolve_project_and_type(file_path, root_path)

    # Title resolution
    title = frontmatter.get("titulo") or frontmatter.get("title")
    if not title:
        # Look for first H1
        h1_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()
        else:
            title = file_path.stem.replace("-", " ").replace("_", " ").title()

    tags = frontmatter.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    status_str = frontmatter.get("status", "ativo").lower()
    try:
        status = MemoryStatus(status_str)
    except ValueError:
        status = MemoryStatus.ACTIVE

    updated_at = frontmatter.get("atualizado") or frontmatter.get("updated") or ""

    # Snippet generation (first non-empty 300 characters of prose)
    lines = [l.strip() for l in body.splitlines() if l.strip() and not l.strip().startswith("#")]
    snippet = " ".join(lines)[:350] if lines else title

    rel_source_path = file_path.relative_to(root_path).as_posix()
    memory_id = f"{project_id}::{rel_source_path}"

    items = []

    # Main document item
    main_item = MemoryItem(
        memory_id=memory_id,
        project_id=project_id,
        source_path=rel_source_path,
        source_type=source_type,
        title=title,
        authority_level=default_authority,
        tags=tags,
        snippet=snippet,
        full_text=content,
        updated_at=updated_at,
        status=status,
        metadata={"frontmatter": frontmatter}
    )
    items.append(main_item)

    # Section-level chunking for ADRs and long topic files
    if source_type in (SourceType.CANONICAL_ADR, SourceType.LEARNING, SourceType.WIKI, SourceType.GOVERNANCE):
        sections = re.split(r"\n(?=##\s+)", body)
        if len(sections) > 1:
            for idx, sec in enumerate(sections[1:], start=1):
                sec_lines = sec.strip().splitlines()
                if not sec_lines:
                    continue
                sec_heading = sec_lines[0].replace("##", "").strip()
                sec_body = "\n".join(sec_lines[1:]).strip()
                if len(sec_body) < 40:
                    continue

                sec_snippet = " ".join([l.strip() for l in sec_lines[1:] if l.strip() and not l.strip().startswith("#")])[:350]
                sec_id = f"{memory_id}#sec-{idx}"

                # Section authority inherit or elevate for specific rules
                sec_authority = default_authority
                if "tcu" in sec_heading.lower() or "sefaz" in sec_heading.lower() or "segurança" in sec_heading.lower():
                    sec_authority = min(100, default_authority + 5)

                chunk_item = MemoryItem(
                    memory_id=sec_id,
                    project_id=project_id,
                    source_path=f"{rel_source_path}#{sec_heading}",
                    source_type=source_type,
                    title=f"{title} ➔ {sec_heading}",
                    authority_level=sec_authority,
                    tags=tags + [sec_heading.lower()],
                    snippet=sec_snippet,
                    full_text=sec,
                    updated_at=updated_at,
                    status=status,
                    metadata={"parent_id": memory_id, "section": sec_heading}
                )
                items.append(chunk_item)

    return items
