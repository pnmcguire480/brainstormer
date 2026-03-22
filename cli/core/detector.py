"""Stack and project detection for BrainStormer."""

import json
from pathlib import Path
from typing import Optional


STACK_MARKERS = {
    "package.json": "node",
    "Cargo.toml": "rust",
    "pyproject.toml": "python",
    "setup.py": "python",
    "requirements.txt": "python",
    "go.mod": "go",
    "Gemfile": "ruby",
    "composer.json": "php",
    "pom.xml": "java",
    "build.gradle": "java",
    "CMakeLists.txt": "cpp",
    "Makefile": "make",
}

FRAMEWORK_MARKERS = {
    "next.config.js": "nextjs",
    "next.config.ts": "nextjs",
    "next.config.mjs": "nextjs",
    "vite.config.ts": "vite",
    "vite.config.js": "vite",
    "angular.json": "angular",
    "svelte.config.js": "svelte",
    "nuxt.config.ts": "nuxt",
    "astro.config.mjs": "astro",
    "remix.config.js": "remix",
    "django-admin.py": "django",
    "manage.py": "django",
    "app.py": "flask",
    "Fastfile": "fastlane",
}

TOOL_MARKERS = {
    "supabase": [".supabase", "supabase"],
    "docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
    "terraform": ["main.tf"],
    "prisma": ["prisma/schema.prisma"],
    "drizzle": ["drizzle.config.ts"],
    "tailwind": ["tailwind.config.js", "tailwind.config.ts"],
    "typescript": ["tsconfig.json"],
}


class ProjectInfo:
    """Detected project information."""

    def __init__(self, root: Path):
        self.root = root
        self.name = root.name
        self.stack: Optional[str] = None
        self.framework: Optional[str] = None
        self.tools: list[str] = []
        self.has_brainstormer = False
        self.existing_files: list[str] = []

    @property
    def summary(self) -> str:
        parts = []
        if self.framework:
            parts.append(self.framework.title())
        if self.stack and self.stack not in (self.framework or ""):
            parts.append(self.stack.title())
        if self.tools:
            parts.extend(t.title() for t in self.tools[:3])
        return " + ".join(parts) if parts else "Unknown stack"

    def to_dict(self) -> dict:
        return {
            "root": str(self.root),
            "name": self.name,
            "stack": self.stack,
            "framework": self.framework,
            "tools": self.tools,
            "has_brainstormer": self.has_brainstormer,
            "existing_files": self.existing_files,
            "summary": self.summary,
        }


BRAINSTORMER_FILES = [
    "CLAUDE.md", "SPEC.md", "SCENARIOS.md", "ARCHITECTURE.md",
    "AGENTS.md", "CODEGUIDE.md", "ART.md", "CONTEXT.md",
    "SNIFFTEST.md", "README.md",
]


def detect_project(root: Path) -> ProjectInfo:
    """Detect project type, stack, and existing BrainStormer files."""
    info = ProjectInfo(root)

    # Detect stack
    for marker, stack in STACK_MARKERS.items():
        if (root / marker).exists():
            info.stack = stack
            break

    # Detect framework
    for marker, framework in FRAMEWORK_MARKERS.items():
        if (root / marker).exists():
            info.framework = framework
            break

    # Detect tools
    for tool, markers in TOOL_MARKERS.items():
        for marker in markers:
            if (root / marker).exists():
                info.tools.append(tool)
                break

    # Try to get project name from package.json etc.
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
            if data.get("name"):
                info.name = data["name"]
        except (json.JSONDecodeError, OSError):
            pass

    cargo = root / "Cargo.toml"
    if cargo.exists():
        try:
            for line in cargo.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("name"):
                    info.name = line.split("=")[1].strip().strip('"')
                    break
        except OSError:
            pass

    # Check for existing BrainStormer files
    for fname in BRAINSTORMER_FILES:
        if (root / fname).exists():
            info.existing_files.append(fname)

    # Check for .brainstormer marker
    info.has_brainstormer = (root / ".brainstormer-version").exists()

    return info
