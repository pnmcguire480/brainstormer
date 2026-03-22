# Changelog

All notable changes to BrainStormer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Version scheme: `YYYY.WW.patch` (year.week.patch).

## [Unreleased]

## [2026.12.0] - 2026-03-22

### Added
- Initial release of BrainStormer CLI
- `brainstormer init` — 6-phase project scaffolding with stack detection
- `brainstormer status` — show configured skills and missing components
- `brainstormer doctor` — validate setup and diagnose issues
- `brainstormer sync` — one-way sync to Obsidian vault with user note preservation
- `brainstormer update` — check for template updates
- `brainstormer migrate` — import .cursorrules, .windsurfrules, Copilot, Aider configs
- `brainstormer agent list` — progressive disclosure showing top 10 agents per stack
- 4 integrated sub-skills: Kernel, Comprehension, Ideation, Quality
- 735 curated agents with source tagging
- Stack detection for Node, Python, Rust, Go, Ruby, PHP, Java, C++
- Framework detection for Next.js, Vite, Angular, Svelte, Nuxt, Astro, Remix, Django, Flask
- Tool detection for Supabase, Docker, Terraform, Prisma, Tailwind, TypeScript
- Obsidian vault sync with project dashboards
- Cross-platform support (Windows, macOS, Linux)
- User-friendly error handling with categorized messages
- Idempotent init (safe to run multiple times)
- pip-installable package with pyproject.toml
