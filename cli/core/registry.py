"""Agent registry for BrainStormer."""

import re
from pathlib import Path
from typing import Optional


def get_agents_dir() -> Path:
    """Get the Claude Code agents directory."""
    home = Path.home()
    agents_dir = home / ".claude" / "agents"
    return agents_dir


def list_agents(filter_stack: Optional[str] = None, show_all: bool = False) -> list[dict]:
    """List available agents, optionally filtered by stack relevance.

    Returns list of agent dicts with name, description, category, filename.
    """
    agents_dir = get_agents_dir()
    if not agents_dir.exists():
        return []

    agents = []
    for f in sorted(agents_dir.glob("*.md")):
        agent = parse_agent_frontmatter(f)
        if agent:
            agents.append(agent)

    if not show_all and filter_stack:
        agents = [a for a in agents if _matches_stack(a, filter_stack)]

    return agents


def parse_agent_frontmatter(path: Path) -> Optional[dict]:
    """Parse YAML frontmatter from an agent .md file."""
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    if not content.startswith("---"):
        return None

    # Find closing ---
    end = content.find("---", 3)
    if end == -1:
        return None

    frontmatter = content[3:end].strip()
    agent = {"filename": path.name, "path": str(path)}

    # Simple YAML parsing (avoid full yaml dependency for agent listing)
    for line in frontmatter.split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key in ("name", "description", "color", "emoji", "vibe", "source"):
                agent[key] = value

    # Derive category from filename prefix
    name_parts = path.stem.split("-")
    if len(name_parts) > 1:
        agent["category"] = name_parts[0]
    else:
        agent["category"] = "general"

    return agent


# Stack → relevant agent categories
STACK_CATEGORY_MAP = {
    "node": ["engineering", "design", "testing", "product"],
    "python": ["engineering", "testing", "product"],
    "rust": ["engineering", "testing"],
    "go": ["engineering", "testing"],
    "react": ["engineering", "design", "testing", "product"],
    "nextjs": ["engineering", "design", "testing", "product"],
    "vite": ["engineering", "design", "testing"],
    "game": ["game", "godot", "unity", "unreal", "roblox", "level", "narrative", "technical"],
}


def _matches_stack(agent: dict, stack: str) -> bool:
    """Check if an agent is relevant for a given stack."""
    relevant_categories = STACK_CATEGORY_MAP.get(stack, [])
    # Always include general-purpose categories
    relevant_categories.extend(["engineering", "testing", "product", "project"])

    category = agent.get("category", "")
    return any(cat in category for cat in relevant_categories)


def count_agents() -> int:
    """Count total agents in the agents directory."""
    agents_dir = get_agents_dir()
    if not agents_dir.exists():
        return 0
    return len(list(agents_dir.glob("*.md")))


# Priority agents per stack — hand-curated "top 10" for progressive disclosure
STACK_TOP_AGENTS = {
    "nextjs": [
        "Frontend Developer", "typescript-pro", "react-state-management",
        "nextjs-app-router-patterns", "tailwind-expert", "css-expert",
        "test-automator", "Code Reviewer", "accessibility-expert",
        "performance-engineer",
    ],
    "node": [
        "nodejs-expert", "typescript-pro", "express-expert",
        "jest-expert", "test-automator", "Code Reviewer",
        "docker-expert", "database-admin", "api-design-principles",
        "performance-engineer",
    ],
    "python": [
        "python-pro", "fastapi-templates", "test-automator",
        "Code Reviewer", "docker-expert", "database-admin",
        "data-scientist", "debugger", "performance-engineer",
        "api-design-principles",
    ],
    "rust": [
        "rust-engineer", "rust-async-patterns", "memory-safety-patterns",
        "test-automator", "Code Reviewer", "debugger",
        "docker-expert", "performance-engineer", "cli-developer",
        "error-handling-patterns",
    ],
    "go": [
        "go-concurrency-patterns", "gin-expert", "test-automator",
        "Code Reviewer", "docker-expert", "debugger",
        "api-design-principles", "performance-engineer",
        "grpc-expert", "database-admin",
    ],
    "react": [
        "Frontend Developer", "react-state-management", "typescript-pro",
        "css-expert", "tailwind-expert", "test-automator",
        "Code Reviewer", "accessibility-expert", "performance-engineer",
        "web-component-design",
    ],
    "django": [
        "django-developer", "python-pro", "test-automator",
        "Code Reviewer", "database-admin", "docker-expert",
        "api-design-principles", "performance-engineer",
        "debugger", "deployment-engineer",
    ],
    "vite": [
        "Frontend Developer", "typescript-pro", "vue-expert",
        "svelte-expert", "css-expert", "tailwind-expert",
        "test-automator", "Code Reviewer", "performance-engineer",
        "web-component-design",
    ],
    "general": [
        "Code Reviewer", "test-automator", "debugger",
        "performance-engineer", "docker-expert", "deployment-engineer",
        "api-design-principles", "error-handling-patterns",
        "git-advanced-workflows", "docs-architect",
    ],
}


def get_top_agents(stack: str, limit: int = 10) -> list[dict]:
    """Get the top recommended agents for a given stack.

    Returns actual agent dicts matched against the curated priority list.
    """
    priority_names = STACK_TOP_AGENTS.get(stack, STACK_TOP_AGENTS["general"])
    all_agents = list_agents(show_all=True)

    # Build a lookup by name (case-insensitive) and filename stem
    by_name = {}
    for a in all_agents:
        name = a.get("name", "").lower()
        stem = Path(a["filename"]).stem.lower()
        by_name[name] = a
        by_name[stem] = a

    matched = []
    for pname in priority_names[:limit]:
        key = pname.lower()
        agent = by_name.get(key)
        if agent and agent not in matched:
            matched.append(agent)

    return matched
