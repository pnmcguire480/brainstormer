# BrainStormer Agent Audit Plan

## Current State
- **735 agents** across 4 sources
- Sources: wshobson/agents (398), community (156), 0xfurai (110), VoltAgent (71)
- All are community IP (free, open-source repos) — none are Anthropic proprietary
- Quality varies: community agents are deep (personality, sections, 500+ words), others are thin

## Goal
Consolidate 735 agents into a curated, comprehensive catalog of **BrainStormer-original agents**.
- Every agent rewritten in BrainStormer's voice (our IP)
- Overlapping agents merged into one authoritative version
- No domain gaps — cover every facet of software development + business
- Anthropic-specific tooling (agent-installer) stays as-is

## Agents to Leave Untouched
- `meta-orchestration-agent-installer.md` — references BrainStormer's own agent install flow

## Target Catalog Structure

Agents are organized into **domains**. Each domain has a clear set of agents.
Where multiple current agents cover the same thing, they merge into ONE.

---

### DOMAIN 1: Frontend & Web (18 agents)
| Target Agent | Merges From | Notes |
|---|---|---|
| react | react-expert, web-component-design (react parts) | Core React patterns |
| react-state-management | react-state-management | Zustand, Redux, Jotai, React Query |
| nextjs | nextjs-app-router-patterns | App Router, SSR, RSC |
| vue | vue-expert | Vue 3, Composition API, Nuxt |
| angular | angular-expert, angular-architect, angular-migration | Full Angular lifecycle |
| svelte | svelte-expert | Svelte 5, SvelteKit |
| astro | astro-expert | Astro, content collections |
| remix | remix-expert | Remix, loaders/actions |
| solidjs | solidjs-expert | Fine-grained reactivity |
| javascript | javascript-pro, modern-javascript-patterns | ES6+, async patterns |
| typescript | typescript-pro, typescript-advanced-types | Advanced types, generics |
| css | css-expert, responsive-design, container queries, fluid layouts | Full CSS mastery |
| tailwind | tailwind-expert, tailwind-design-system | Utility-first, design tokens |
| html | html-expert | Semantic HTML |
| web-components | web-component-design | Custom elements, Shadow DOM |
| design-systems | design-system-architect, design-system-patterns | Tokens, theming, component libs |
| jquery | jquery-expert | Legacy jQuery support |
| animation | animation-libraries-reference, scroll-animations, microinteraction-patterns | Motion design |

### DOMAIN 2: Backend & APIs (15 agents)
| Target Agent | Merges From |
|---|---|
| nodejs | nodejs-expert, nodejs-backend-patterns |
| express | express-expert |
| fastify | fastify-expert |
| nestjs | nestjs-expert |
| bun | bun-expert |
| deno | deno-expert |
| rest-api | rest-expert, api-design-principles |
| graphql | graphql-expert, graphql-architect |
| grpc | grpc-expert |
| websockets | websocket-expert, websocket-engineer |
| openapi | openapi-expert, openapi-spec-generation |
| trpc | trpc-expert |
| api-documentation | api-documenter |
| api-mocking | api-mocking-framework |
| webhooks | (extracted from various) |

### DOMAIN 3: Python (18 agents)
| Target Agent | Merges From |
|---|---|
| python | python-pro |
| python-patterns | python-design-patterns, python-anti-patterns |
| python-async | async-python-patterns, python-background-jobs |
| python-testing | python-testing-patterns |
| python-typing | python-type-safety |
| python-packaging | python-packaging, uv-package-manager, python-project-structure |
| python-performance | python-performance-optimization |
| python-resilience | python-resilience, python-error-handling, python-resource-management |
| python-observability | python-observability |
| python-style | python-code-style, python-configuration |
| django | django-developer |
| flask | flask-expert |
| fastapi | fastapi-templates |
| celery | celery-expert |
| pandas | pandas-expert |
| numpy | numpy-expert |
| pytorch | pytorch-expert |
| tensorflow | tensorflow-expert |
| scikit-learn | scikit-learn-expert |

### DOMAIN 4: Java/JVM (5 agents)
| Target Agent | Merges From |
|---|---|
| java | java-pro, java-architect |
| spring-boot | spring-boot-expert, spring-boot-engineer |
| kotlin | kotlin-specialist |
| scala | scala-pro |
| clojure | clojure-expert |

### DOMAIN 5: .NET/C# (5 agents)
| Target Agent | Merges From |
|---|---|
| dotnet | dotnet-architect, dotnet-core-expert, dotnet-backend-patterns |
| dotnet-framework | dotnet-framework-4.8-expert |
| csharp | csharp-pro, csharp-developer, c-style-guide |
| aspnet | aspnet-core-expert |
| entity-framework | entity-framework-core-best-practices, dapper-patterns |

### DOMAIN 6: Systems Languages (11 agents)
| Target Agent | Merges From |
|---|---|
| rust | rust-engineer, rust-async-patterns |
| go | go-concurrency-patterns, gin-expert, fiber-expert |
| c | c-expert, c-pro |
| cpp | cpp-expert, cpp-pro, memory-safety-patterns |
| ruby | ruby-pro, rails-expert, sidekiq-expert |
| php | php-pro, php-expert, laravel-specialist |
| elixir | elixir-pro, phoenix-expert, erlang-expert |
| haskell | haskell-pro |
| ocaml | ocaml-expert |
| lua | lua-expert |
| perl | perl-expert |

### DOMAIN 7: Other Languages (3 agents)
| Target Agent | Merges From |
|---|---|
| julia | julia-pro |
| dart | dart-expert |
| wordpress | wordpress-master |

### DOMAIN 8: Mobile & Desktop (10 agents)
| Target Agent | Merges From |
|---|---|
| ios-swift | ios-expert, ios-developer, swift-expert, swiftui-expert |
| android | android-expert, mobile-android-design, jetpack-compose |
| flutter | flutter-expert, dart-expert |
| react-native | react-native-expert, react-native-architecture, react-native-design, expo-expert |
| mobile-security | mobile-security-coder, mobile-ios-design |
| electron | electron-pro |
| tauri | tauri-expert |
| visionos | visionos-spatial-engineer |
| macos-metal | macos-spatial-metal-engineer |
| unity-developer | unity-developer (standalone — game engine, not mobile) |

### DOMAIN 9: Databases (16 agents)
| Target Agent | Merges From |
|---|---|
| postgresql | postgresql-expert, postgresql-table-design, postgres-pro |
| mysql | mysql-expert, mariadb-expert |
| mssql | mssql-expert |
| sqlite | sqlite-expert |
| mongodb | mongodb-expert, mongoose-expert |
| redis | redis-expert |
| elasticsearch | elasticsearch-expert |
| opensearch | opensearch-expert |
| dynamodb | dynamodb-expert |
| cassandra | cassandra-expert |
| cockroachdb | cockroachdb-expert |
| neo4j | neo4j-expert |
| sql | sql-expert, sql-pro, sql-optimization-patterns |
| database-admin | database-admin |
| database-migration | database-migration, flyway-expert, liquibase-expert |
| orm | prisma-expert, sequelize-expert, typeorm-expert, knex-expert |

### DOMAIN 10: DevOps & Infrastructure (20 agents)
| Target Agent | Merges From |
|---|---|
| docker | docker-expert |
| kubernetes | k8s-manifest-generator, k8s-security-policies |
| helm | helm-chart-scaffolding |
| istio | istio-traffic-management |
| linkerd | linkerd-patterns |
| service-mesh | service-mesh-observability |
| terraform | terraform-specialist |
| terragrunt | terragrunt-expert |
| pulumi | pulumi-expert |
| ansible | ansible-expert |
| cloud-architect | cloud-architect, multi-cloud-architecture |
| hybrid-cloud | hybrid-cloud-architect, hybrid-cloud-networking |
| cloud-cost | cost-optimization |
| azure | azure-infra-engineer |
| network | network-engineer |
| platform-engineer | platform-engineer |
| windows-admin | windows-infra-admin |
| gitops | gitops-workflow, argocd-setup |
| deployment-pipelines | deployment-pipeline-design |
| secrets-management | secrets-management |

### DOMAIN 11: CI/CD (6 agents)
| Target Agent | Merges From |
|---|---|
| github-actions | github-actions-expert, github-actions-templates |
| gitlab-ci | gitlab-ci-expert, gitlab-ci-patterns |
| jenkins | jenkins-expert |
| circleci | circleci-expert |
| deployment-engineer | deployment-engineer |
| ci-cd-patterns | (extracted best practices) |

### DOMAIN 12: Testing & QA (14 agents)
| Target Agent | Merges From |
|---|---|
| jest | jest-expert |
| vitest | vitest-expert |
| cypress | cypress-expert |
| playwright | playwright-expert |
| selenium | selenium-expert |
| mocha | mocha-expert |
| jasmine | jasmine-expert |
| testcafe | testcafe-expert |
| bats | bats-testing-patterns |
| e2e-testing | e2e-testing-patterns |
| javascript-testing | javascript-testing-patterns |
| tdd | tdd-orchestrator |
| test-automation | test-automator, automated-unit-test-generation |
| code-review | code-review-excellence, code-reviewer, multi-reviewer-patterns |

### DOMAIN 13: Security (14 agents)
| Target Agent | Merges From |
|---|---|
| security-engineer | security-engineer |
| owasp | owasp-top10-expert, xss-vulnerability-scanner |
| penetration-testing | penetration-tester |
| threat-modeling | stride-analysis, attack-tree-construction, security-requirement-extraction, threat-mitigation |
| reverse-engineering | reverse-engineer, binary-analysis-patterns, anti-reversing-techniques, protocol-reverse-engineering |
| malware-analysis | malware-analyst |
| firmware-analysis | firmware-analyst |
| memory-forensics | memory-forensics |
| auth-patterns | auth-implementation-patterns, auth0-expert, oauth-oidc-expert, jwt-expert, keycloak-expert |
| mtls | mtls-configuration |
| pci-compliance | pci-compliance |
| gdpr | gdpr-data-handling |
| sast | sast-configuration, sast-security-plugin |
| ad-security | ad-security-reviewer |

### DOMAIN 14: Monitoring & SRE (12 agents)
| Target Agent | Merges From |
|---|---|
| prometheus | prometheus-configuration, prometheus-expert |
| grafana | grafana-dashboards, grafana-expert |
| loki | loki-expert |
| opentelemetry | opentelemetry-expert |
| elk | elk-expert |
| distributed-tracing | distributed-tracing |
| observability | observability-engineer, performance-engineer |
| sre | sre, incident-responder |
| incident-response | incident-response-commander, incident-runbook-templates |
| postmortem | postmortem-writing |
| on-call | on-call-handoff-patterns |
| chaos-engineering | chaos-engineer |
| slo | slo-implementation |

### DOMAIN 15: AI & ML (14 agents)
| Target Agent | Merges From |
|---|---|
| langchain | langchain-expert, langchain-architecture |
| rag | rag-implementation, hybrid-search-implementation |
| vector-database | vector-database-engineer, vector-db-expert, vector-index-tuning, similarity-search-patterns |
| embeddings | embedding-strategies |
| llm-evaluation | llm-evaluation |
| prompt-engineering | prompt-engineering-patterns, prompt-optimization, prompt-template-library, prompt-template-systems, few-shot-learning, system-prompt-design |
| openai-api | openai-api-expert |
| nlp | nlp-engineer |
| ml-pipelines | ml-pipeline-workflow |
| data-science | data-scientist |
| ai-engineer | ai-engineer |
| context-management | context-manager, context-restoration, context-save-tool |
| mcp-builder | mcp-builder, mcp-developer |
| ai-assistant | ai-assistant-development |

### DOMAIN 16: Architecture & Patterns (10 agents)
| Target Agent | Merges From |
|---|---|
| software-architect | software-architect, architect-review |
| architecture-patterns | architecture-patterns, architecture-decision-records |
| microservices | microservices-patterns, microservices-architect |
| event-sourcing | event-sourcing-architect, event-store-design, projection-patterns |
| cqrs | cqrs-implementation |
| saga-patterns | saga-orchestration |
| workflow-orchestration | workflow-orchestration-patterns, temporal-python-pro, temporal-python-testing |
| error-handling | error-handling-patterns |
| fullstack | fullstack-developer, full-stack-feature-orchestrator |
| legacy-modernization | legacy-modernizer, code-migration-assistant |

### DOMAIN 17: Data Engineering (10 agents)
| Target Agent | Merges From |
|---|---|
| kafka | kafka-expert |
| rabbitmq | rabbitmq-expert |
| nats | nats-expert |
| mqtt | mqtt-expert |
| aws-messaging | sns-expert, sqs-expert |
| airflow | airflow-dag-patterns |
| dbt | dbt-transformation-patterns |
| spark | spark-optimization |
| data-quality | data-quality-frameworks |
| data-engineer | data-engineer |

### DOMAIN 18: Developer Tools & Workflow (14 agents)
| Target Agent | Merges From |
|---|---|
| git | git-advanced-workflows, git-workflow-manager |
| monorepo | monorepo-management, turborepo-caching, nx-workspace-patterns |
| bazel | bazel-build-optimization |
| webpack | webpack-expert |
| rollup | rollup-expert |
| build-tools | build-engineer |
| cli-development | cli-developer |
| dependency-management | dependency-manager, dependency-upgrade |
| developer-tooling | tooling-engineer |
| developer-experience | dx-optimizer |
| github-workflows | github-issue-resolution, pull-request-enhancement |
| slack | slack-expert |
| changelog | changelog-automation |
| debugging | debugging-strategies, error-detective, debugger, parallel-debugging |

### DOMAIN 19: Documentation (6 agents)
| Target Agent | Merges From |
|---|---|
| technical-writer | technical-writer (community + engineering versions) |
| docs-architect | docs-architect, automated-documentation-generation |
| c4-documentation | c4-code, c4-component, c4-container, c4-context |
| mermaid | mermaid-expert |
| reference-builder | reference-builder |
| api-docs | api-documenter |

### DOMAIN 20: Design & UX (12 agents)
| Target Agent | Merges From |
|---|---|
| ui-designer | ui-designer, ui-ux-designer, ui-visual-validator |
| ux-architect | ux-architect |
| ux-researcher | ux-researcher (community + VoltAgent) |
| brand-design | brand-guardian |
| visual-storytelling | visual-storyteller |
| image-prompts | image-prompt-engineer |
| inclusive-design | inclusive-visuals-specialist, cultural-intelligence-strategist |
| whimsy-design | whimsy-injector |
| interaction-design | interaction-design |
| visual-design | visual-design-foundations, color-systems, typography-systems, spacing-iconography |
| accessibility | accessibility-expert, accessibility-compliance, wcag-audit-patterns, screen-reader-testing, aria-patterns, accessibility-tester |
| responsive-design | responsive-design, breakpoint-strategies, container-queries, fluid-layouts |

### DOMAIN 21: Game Development (14 agents)
| Target Agent | Merges From |
|---|---|
| unity | unity-developer, unity-architect, unity-ecs-patterns |
| unity-editor | unity-editor-tool-developer |
| unity-multiplayer | unity-multiplayer-engineer |
| unity-shaders | unity-shader-graph-artist |
| unreal | unreal-systems-engineer |
| unreal-multiplayer | unreal-multiplayer-architect |
| unreal-art | unreal-technical-artist, unreal-world-builder |
| godot | godot-gameplay-scripter, godot-gdscript-patterns, godot-multiplayer, godot-shader |
| roblox | roblox-systems-scripter, roblox-experience-designer, roblox-avatar-creator |
| game-design | game-designer, level-designer |
| narrative-design | narrative-designer |
| game-audio | game-audio-engineer |
| technical-art | technical-artist |
| minecraft | minecraft-bukkit-pro |

### DOMAIN 22: Worldbuilding (5 agents)
| Target Agent | Merges From |
|---|---|
| anthropologist | academic-anthropologist |
| geographer | academic-geographer |
| historian | academic-historian |
| narratologist | academic-narratologist |
| psychologist | academic-psychologist |

### DOMAIN 23: Web3 & Blockchain (5 agents)
| Target Agent | Merges From |
|---|---|
| blockchain | blockchain-developer, blockchain-security-auditor |
| solidity | solidity-smart-contract-engineer, solidity-security |
| web3-testing | web3-testing |
| defi | defi-protocol-templates |
| nft | nft-standards |

### DOMAIN 24: Marketing & SEO (20 agents)
| Target Agent | Merges From |
|---|---|
| seo-specialist | seo-specialist |
| seo-content | seo-content-writer, seo-content-planner, seo-content-auditor, seo-content-refresher |
| seo-technical | seo-keyword-strategist, seo-meta-optimizer, seo-snippet-hunter, seo-structure-architect, seo-authority-builder, seo-cannibalization-detector |
| content-marketing | content-marketer, content-creator |
| social-media | social-media-strategist |
| tiktok | tiktok-strategist |
| instagram | instagram-curator |
| linkedin | linkedin-content-creator |
| twitter | twitter-engager |
| reddit | reddit-community-builder |
| growth-hacking | growth-hacker |
| paid-media | paid-media-auditor, ppc-campaign-strategist, paid-social, ad-creative, programmatic-buyer, search-query-analyst, tracking-measurement |
| video-production | short-video-editing-coach |
| app-store | app-store-optimizer |
| ai-citation | ai-citation-strategist |
| search-specialist | search-specialist |
| book-authoring | book-co-author |
| developer-advocate | developer-advocate |
| carousel-engine | carousel-growth-engine |
| baidu-seo | baidu-seo-specialist |

### DOMAIN 25: China Market (10 agents)
| Target Agent | Merges From |
|---|---|
| douyin | douyin-strategist |
| xiaohongshu | xiaohongshu-specialist |
| weibo | weibo-strategist |
| kuaishou | kuaishou-strategist |
| bilibili | bilibili-content-strategist |
| wechat | wechat-official-account-manager, wechat-mini-program-developer |
| private-domain | private-domain-operator |
| livestream | livestream-commerce-coach |
| china-ecommerce | china-e-commerce-operator |
| cross-border | cross-border-e-commerce-specialist |
| podcast | podcast-strategist |
| zhihu | zhihu-strategist |

### DOMAIN 26: Sales (8 agents)
| Target Agent | Merges From |
|---|---|
| sales-coach | sales-coach |
| deal-strategist | deal-strategist |
| sales-engineer | sales-engineer |
| outbound | outbound-strategist |
| discovery-coach | discovery-coach |
| pipeline-analyst | pipeline-analyst |
| proposal-strategist | proposal-strategist |
| account-strategist | account-strategist |

### DOMAIN 27: Project Management (8 agents)
| Target Agent | Merges From |
|---|---|
| product-manager | product-manager, product-vision, product-guidelines |
| sprint-prioritizer | sprint-prioritizer |
| scrum-master | scrum-master |
| project-manager | project-manager, senior-project-manager, project-shepherd |
| experiment-tracker | experiment-tracker |
| jira | jira-workflow-steward |
| studio-producer | studio-producer, studio-operations |
| standup-notes | standup-notes-generator |

### DOMAIN 28: Business Operations (16 agents)
| Target Agent | Merges From |
|---|---|
| hr-recruitment | hr-pro, recruitment-specialist, employment-contract-templates |
| legal-compliance | legal-advisor, legal-compliance-checker, compliance-auditor |
| financial-modeling | financial-projections, startup-financial-modeling, finance-tracker |
| startup-tools | startup-analyst, startup-metrics-framework, market-sizing-analysis |
| business-analyst | business-analyst, business-case-generator |
| competitive-analysis | competitive-analyst, competitive-landscape |
| market-research | market-researcher, market-sizing-data-sources |
| payments | payment-integration, stripe-expert, stripe-integration, paypal-integration, braintree-expert |
| billing | billing-automation |
| customer-success | customer-success-manager, customer-support |
| kpi-dashboards | kpi-dashboard-design |
| data-storytelling | data-storytelling |
| analytics | analytics-reporter, data-analyst |
| executive-summary | executive-summary-generator |
| supply-chain | supply-chain-strategist |
| corporate-training | corporate-training-designer |

### DOMAIN 29: Research & Analysis (6 agents)
| Target Agent | Merges From |
|---|---|
| research-analyst | research-analyst |
| data-researcher | data-researcher |
| trend-analyst | trend-analyst |
| competitive-analyst | competitive-analyst |
| scientific-researcher | scientific-literature-researcher |
| market-researcher | market-researcher |

### DOMAIN 30: Scripting & Shell (5 agents)
| Target Agent | Merges From |
|---|---|
| bash | bash-pro, bash-defensive-patterns |
| powershell | powershell-5.1-expert, powershell-7-expert, powershell-module-architect, powershell-security, powershell-ui-architect |
| posix-shell | posix-shell-pro |
| shellcheck | shellcheck-configuration |
| m365-admin | m365-admin |

### DOMAIN 31: XR & Spatial (4 agents)
| Target Agent | Merges From |
|---|---|
| xr-developer | xr-immersive-developer |
| xr-interface | xr-interface-architect, xr-cockpit-interaction |
| visionos | visionos-spatial-engineer |
| macos-metal | macos-spatial-metal-engineer |

### DOMAIN 32: Embedded & IoT (3 agents)
| Target Agent | Merges From |
|---|---|
| embedded | embedded-systems, embedded-firmware-engineer, arm-cortex-expert |
| iot | iot-engineer |
| fintech | fintech-engineer |

### DOMAIN 33: Finance & Trading (3 agents)
| Target Agent | Merges From |
|---|---|
| quant-analyst | quant-analyst, backtesting-frameworks |
| risk-manager | risk-manager, risk-metrics-calculation |
| fintech | fintech-engineer |

### DOMAIN 34: Meta & Orchestration (12 agents)
| Target Agent | Merges From |
|---|---|
| team-lead | team-lead |
| team-implementer | team-implementer |
| team-reviewer | team-reviewer |
| team-debugger | team-debugger |
| multi-agent-coordinator | multi-agent-coordinator, agents-orchestrator |
| task-distributor | task-distributor, task-coordination-strategies |
| workflow-orchestrator | workflow-orchestrator, workflow-automation |
| knowledge-synthesizer | knowledge-synthesizer |
| error-coordinator | error-coordinator |
| performance-monitor | performance-monitor |
| agent-organizer | agent-organizer |
| onboarding | onboard |

### DOMAIN 35: Niche & Specialized (10 agents)
| Target Agent | Merges From |
|---|---|
| salesforce | salesforce-architect |
| blender | blender-addon-engineer |
| minecraft | minecraft-bukkit-pro |
| lsp-engineer | lsp-index-engineer |
| terminal | terminal-integration-specialist |
| zettelkasten | zk-steward |
| document-generator | document-generator |
| model-qa | model-qa-specialist |
| rapid-prototyper | rapid-prototyper |
| behavioral-nudge | behavioral-nudge-engine |

### DOMAIN 36: Regional & Industry (8 agents)
| Target Agent | Merges From |
|---|---|
| korea-market | korean-business-navigator |
| france-market | french-consulting-market-navigator |
| government-digital | government-digital-presales-consultant |
| healthcare | healthcare-marketing-compliance |
| study-abroad | study-abroad-advisor |
| identity-trust | agentic-identity-trust |
| automation-governance | automation-governance-architect |
| accounts-payable | accounts-payable-agent |

---

## FINAL NUMBERS

| Metric | Count |
|---|---|
| Current agents | 735 |
| Target unique agents | ~310 |
| Agents eliminated via merge | ~425 |
| Domains covered | 36 |
| Anthropic-specific (untouched) | 1 |

## Rewrite Strategy

Every non-Anthropic agent gets rewritten in BrainStormer format:
1. **New frontmatter** — BrainStormer-branded, no third-party source attribution
2. **Standardized structure** — Identity, Mission, Method, Output Format
3. **Original prose** — Not copied from source agents, synthesized fresh
4. **Quality floor** — Minimum 200 words, structured sections, actionable instructions
