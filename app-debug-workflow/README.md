<p align="center">🔧 App Debug Workflow — Audit Any Unfamiliar Codebase, Find Every Bug, Fix It Surgically, Under a 90-Minute Deadline</p>

**A Hermes Agent multi-session skill for auditing unfamiliar full-stack codebases under time pressure: security review, bug hunt, performance audit, and reliability review of Python gRPC + SQLAlchemy backends, TypeScript React frontends, and moonrepo monorepos — discover → duck-verify → plan → handoff → fix → validate.**

<p align="center">
  <img src="https://img.shields.io/badge/Type-Skill-8A2BE2?style=for-the-badge" alt="Type: Skill">
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge" alt="Platform: Windows">
  <img src="https://img.shields.io/badge/Agent-Hermes-FF6B6B?style=for-the-badge" alt="Agent: Hermes">
  <img src="https://img.shields.io/badge/Timebox-90%20min-00C853?style=for-the-badge" alt="Timebox: 90 minutes">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License: MIT">
</p>

**Version:** 2.0.0 · **Author:** Ringo / MilkyWay008 ([github.com/MilkyWay008](https://github.com/MilkyWay008)) · **Platforms:** Windows · **Tags:** `debug`, `audit`, `security`, `codebase-review`, `multi-session`, `timeboxed`

---

## 📑 Table of Contents

- [💡 What This Skill Does](#-what-this-skill-does)
- [✨ Key Features](#-key-features)
- [🚀 When to Use / How to Trigger](#-when-to-use--how-to-trigger)
- [⚙️ How It Works — Core Loop & Session Architecture](#️-how-it-works--core-loop--session-architecture)
- [🎯 Triage Matrix (P0–P3)](#-triage-matrix-p0p3)
- [🛠 Phase-by-Phase Workflow (0–6)](#-phase-by-phase-workflow-06)
- [📁 Files & Deliverables](#-files--deliverables)
- [⏱ Time Budget & Abort Protocols](#-time-budget--abort-protocols)
- [🔒 Hard Rules & Disciplines](#-hard-rules--disciplines)
- [⚠️ Pitfalls & Gotchas](#️-pitfalls--gotchas)
- [🔗 Skill Interactions](#-skill-interactions)
- [🔍 Search Keywords](#-search-keywords)
- [📝 Credits & License](#-credits--license)

---

## 💡 What This Skill Does

This workflow is purpose-built for **auditing an unfamiliar codebase under time pressure**. It inverts the `complex-project-workflow` — instead of building from scratch, you start from an existing (buggy) codebase and work backward to find and fix issues.

**Core loop:** Discover → Duck-Verify → Plan → Handoff → Fix → Validate (iterate)

**Why it exists:** In an earlier time-pressure SWE task, an agent spent the entire 90 minutes running a 50-bug sweep when the task page actually listed 5 specific structured engineering tasks — it failed because it never asked. This skill's gates (External Objectives Check, duck audit gates, user review gates) permanently prevent that failure mode.

**What it covers:** security vulnerabilities (hardcoded secrets, SQL injection, missing auth, XSS, CORS), performance bugs (N+1 queries, blocking calls, React re-renders), reliability issues (missing error handling, resource leaks, no loading states), DX gaps (slow builds, missing types, test gaps), and correctness bugs (race conditions, edge cases, state management).

---

## ✨ Key Features

- **🔴 90-minute timeboxed workflow** — 7 phases (Phase 0–6) targeting 73 min of work + a 17–20 min buffer, with hard stop rules at 80 min and 85 min
- **🧠 Multi-session architecture** — Session A (debug/plan, Phases 0–4+6, NEVER writes code) and Session B (fix, Phase 5, NEVER plans), bridged by `debug-fix-handoff/` docs to protect the main session's context health
- **🦆 Rubber-duck audit gates at every phase** — duck council verifies findings, catches blind spots, audits edge cases, and confirms severity; with a documented **subagent-audit fallback** when the rubber duck skill/MCP is unavailable
- **📊 Repo-size gate (< 70 MB standard vs ≥ 70 MB large)** — single check that controls subagent count (2 vs 4), duck squad size (3 ducks vs 1 Grok duck), and browser depth for the entire workflow
- **✂️ SURGICAL fix rule** — every fix must specify exact file path, exact line numbers, current code ("before"), replacement code ("after"), one-line rationale; ≤ 5 lines of change or it's not surgical enough
- **📋 4-line commit message template (mandatory)** — `[$BUG_ID] [$TASK_ID]: summary` + `Problem:` + `Fix:` + `Verification:` + `Refs:`; no one-liners allowed
- **✅ 3-way diff surgical verification** — diff fixed `repo/` vs buggy `repo-src/` vs original clean `repo-src (no bug)/` to prove fixes were surgical, not over-engineered
- **🚪 Mandatory user review gates** — External Objectives Check (before Phase 1), fix-scope agreement (before Phase 4), and the post-build/post-test bug-review gate (catalog → investigate → options → **WAIT for user** → implement)
- **📝 Versioned deliverables** — all docs use `-v1` initially, `-v2` after duck/edge-case corrections; v1 is never overwritten so the duck can compare
- **🌕 moonrepo dependency-aware testing** — `moon :test` only tests changed modules + dependents (saves 5–15 min per iteration on 500K-line suites); dependency layers (0: models/DB → 1: services → 2: API → 3: frontend) determine fix order
- **🧩 Subagent blank-slate + temp-file collision rules** — every `delegate_task()` is fully self-contained; multiple subagents writing to the same deliverable use unique `temp/<deliverable>-<role>-v1.md` files merged by the main agent
- **🖥 Screen-share aware** — per-phase announcements, narrations, and a ready-made script of what to say while subagents/ducks/fixes run

---

## 🚀 When to Use / How to Trigger

> ⚠️ **TRIGGER CONDITION:** Load this skill when starting a **codebase audit** — security review, bug hunt, performance audit of an unfamiliar full-stack application. Designed for a time-pressure LLM-Base Refactoring (Python) task: Python gRPC + SQLAlchemy backend, TypeScript React frontend, moonrepo monorepo.

**Trigger phrases / situations (from the skill's frontmatter):**
- "Audit this unfamiliar codebase for bugs"
- "Security review / bug hunt / performance audit of a full-stack app"
- "Find all the bugs before we fix anything" (post-build / post-test bug review)
- Any time-pressure coding/debug task with a hard deadline
- The user returns from testing a build with a list of bugs → the **strictly phased, gated** bug-review workflow kicks in (see below)

**🔴 HARD RULE — phase-start re-read:** At the start of EVERY phase (0 through 6), you MUST re-read this entire skill with `skill_view(name='app-debug-workflow')` before taking any action. No exceptions. Then state a brief checklist of what this phase produces before starting work.

**Post-build / post-test bug review — user's hard workflow rule (2026-08-02):** *"before we fix anything, let's find the bugs, discuss, come up with fix plan; only after we finalized everything, then we go fix."* Strict phase order, do NOT skip or merge:
1. **Catalog the bugs** — dated report `bugs-and-fixes-report-<YYYYMMDD>.md` at build workspace root (severity, symptom, observed location, log evidence)
2. **Investigate root cause** — read-only subagents find the ACTUAL root cause (file:line, code path); verify official docs via subagents when the fix depends on what a feature is supposed to do
3. **Design fix options** — A/B/C/D options table (description, pros, cons) with a preferred option + one-line rationale, plus a "fix order & dependencies" section
4. **USER REVIEW GATE** — present the full plan and WAIT. No fixes until the user says go; the gate is absolute
5. **Implement** — source changes → source repo; build-layer changes → build repo (hermes-otg-build two-repo model)

**Log verification step:** When the user reports test-machine bugs, ALWAYS check the test machine's `<package>/data/logs/` (errors.log, gateway.log, agent.log) — logs confirm reported bugs AND surface new ones (config drift, blocked context files, provider fallbacks). Read logs before finalizing the report.

**Bug-close discipline:** RESOLVED only after fix applied AND verified (with evidence) · CLOSED for user-explained non-bugs with their explanation recorded · tentative resolutions get "verify after next test" status — never claim fixed without the user's test confirmation.

---

## ⚙️ How It Works — Core Loop & Session Architecture

```
Discover → Duck-Verify → Plan → Handoff → Fix → Validate (iterate)
```

**Multi-session architecture (optional — context health fallback):**
- **Default (single session):** Run Phases 0–6 in one session. Simpler, no handoff overhead.
- **Fallback (multi-session):** If context health degrades (ECHO 🟡/🔴), split into **Session A** (debug/plan, Phases 0–4+6 — exploration, discovery, rubber-duck audit, task planning, handoff doc creation, **NO code writing**) and **Session B** (fix, Phase 5 — execute fixes from task registry via subagents/ACP, **NO planning**). Handoff docs in `debug-fix-handoff/` make this seamless.
- **Why prepare for multi-session:** The fix session produces heavy tool call volume — keeping it in the main session accelerates context degradation. The handoff protects the primary session's context health.

**Versioning convention for all docs:** All deliverables use `-v1` suffix initially (`big-picture-architecture-v1.md`, `bugs-report-v1.md`, `proposed-fix-v1.md`, `task-registry-v1.md`, `fix-handoff-v1.md`). When rubber-duck review or edge-case audit finds issues → create `-v2` versions with corrections. Never overwrite v1 — keep both so the duck can compare what changed.

### 🦆 Audit Gate Fallback (when rubber duck is unavailable)

Every audit point (Phase 2 duck verification, Phase 3 duck edge-case audit, Phase 4 duck final verification, and all pre-flight duck gates) normally runs through the rubber duck council. **If the rubber duck skill or MCP server is not available** (`skill_view(name='rubber-duck-council')` fails, wrapper script missing, MCP duck tools not registered) — **do NOT skip the audit**:
1. Spawn a `delegate_task` subagent with the EXACT duck prompt for that phase (verify findings, catch blind spots, confirm severity, check for missed bugs/edge cases)
2. Explicitly instruct: *"Look for ALL possible edge cases, gaps, contradictions, blind spots, and failure modes. Perform a thorough gap analysis — what's missing, underspecified, or would break in the real world? Do NOT edit any files — audit only, and return a structured findings list with severity + suggested fix for each."*
3. Treat findings exactly like duck findings: update docs to `-v2`, re-audit, iterate until nothing substantial is raised
4. Log which fallback was used (`subagent-audit` vs `duck-council`) in the phase record

The audit gate is non-negotiable — the *mechanism* (ducks vs subagent) is interchangeable, the *edge-case + gap analysis* is not.

---

## 🎯 Triage Matrix (P0–P3)

When time is tight, use this to decide what to do with each bug:

| Priority | Category | Action | Time to spend |
|----------|----------|--------|---------------|
| **P0 🔴** | Hardcoded secrets, SQL injection, missing auth, XSS | **Must fix** — highest severity | As long as needed |
| **P1 🟡** | N+1 queries, missing error handling, broken auth, CORS misconfig | **Fix if time allows** | Max 5 min per bug |
| **P2 🟢** | Missing loading states, console.log left in, verbose errors, type safety | **Document only** — note in bugs-report | 30 sec per bug |
| **P3 ⚪** | Code style, TODO comments, missing tests, DX improvements | **Skip entirely** — not evaluated | Zero |

**Decision flow:** For each bug → is it P0? Fix immediately. P1? Fix only if ahead of schedule. P2/P3? Document and move on.

**Security-first prioritization:** 1. 🔴 Plaintext secrets/credentials · 2. 🔴 SQL injection · 3. 🔴 Missing auth · 4. 🟡 Reliability (crashes, resource leaks) · 5. 🟡 Performance (N+1, blocking calls) · 6. 🟢 Developer experience (build speed, test gaps).

---

## 🛠 Phase-by-Phase Workflow (0–6)

> ⚠️ **Every phase starts with:** re-read the skill via `skill_view(name='app-debug-workflow')`, state the phase's checklist, and announce to the user ("Ready to proceed?").

### Phase 0 — Pre-Flight Setup (8 min)

**Purpose:** Load GitHub skill, get repo URL, clone repos. Finish before the timer truly starts ticking.

```python
skill_view(name='github-now')
skill_view(name='app-debug-workflow')
```

**Checklist (verify before beginning):**
- [ ] Python 3.12+ available (`python3.12 --version`)
- [ ] Node.js v22+ (`node --version`)
- [ ] pnpm latest (`pnpm --version`)
- [ ] moon (`moon --version` — check via `source ~/.bashrc` first if not in PATH)
- [ ] Git (`git --version`)
- [ ] Docker images cached (`docker images postgres` + `docker images redis`)
- [ ] Rubber duck MCP server running
- [ ] ECHO plugin active and healthy
- [ ] Model chain set: Main agent = frontier model (e.g. GLM 5.2, Claude, GPT), Subagents = fast capable model (e.g. DeepSeek v4 Pro), ACP = strong coder (e.g. MiniMax M3), King duck = strongest available (e.g. Grok 4.3)
- [ ] Duck file-read bridge active (sandboxfs — C:\Builds + C:\Projects)

**Docker check:** If the repo has `docker-compose.yml` or requires PostgreSQL → ask the user: *"Is Docker Desktop running and the engine unpaused?"*

**Clone the repo:**
```bash
# The user will provide the task repo URL
git clone <task-repo-url> repo
git clone <task-repo-url> repo-src   # reference copy, never touch
```

**🔴 Repo Size Gate — determines ALL subsequent phases.** Immediately after clone:
```bash
# Check repo size (exclude .git which inflates numbers)
du -sh repo --exclude=.git 2>/dev/null || du -sh repo
```

**Threshold: 70 MB**

| Repo size | Variant | Phase 1 subagents | Phase 2 ducks | Browser discovery |
|-----------|---------|-------------------|---------------|-------------------|
| < 70 MB | Standard | 2 subagents | 3 ducks (`--squad quick`) | Full click-through |
| >= 70 MB | Large | 4 subagents | 1 duck (`ask_duck(provider: "grok")`) | Main routes only |

🔴 HARD RULE: Set the variant BEFORE dispatching any Phase 1 subagents — it applies to ALL subsequent phases and does not change. File the result in `temp/repo-size-check.md`.

**🔴 Commit lockfile changes after dependency install** (keeps the working tree clean for Phase 6):
```bash
cd repo
git add pnpm-lock.yaml  # or package-lock.json, yarn.lock, etc.
git commit -m "chore: update lockfile after dependency install"
```

**🔴 MANDATORY GATE — External Objectives Check (before Phase 1 fires; do NOT skip, not even when the user says "go"):** Ask the user EXPLICITLY: *"Before I start Phase 1 reconnaissance, one critical question: Is there a separate task list, task page, rubric, or set of specific objectives I should know about — something that isn't in the README or AGENTS.md? If there's a task page or description you can see, please paste it or tell me what the tasks are. I'll prioritize those as the primary objectives, and treat everything else as secondary."*
1. Ask this question EVERY time. 2. Wait for the answer — do NOT dispatch subagents until they respond. 3. If "yes" → those objectives become the PRIMARY task list; bug-hunting runs as secondary support. 4. If "no" → proceed standard. 5. Do NOT skip because you're "pretty sure" there's nothing else — the earlier time-pressure failure happened precisely because this check was missing.

**🔴 Present the plan to the user (screen-share moment)** — outline Phases 1–6 and ask "Ready to proceed to Phase 1?"

### Phase 1 — Codebase Reconnaissance (15 min)

**Purpose:** Understand the system end-to-end before diagnosing anything. **DISCOVERY ONLY — NO FIXING.**

**1a — Read the README** and project docs; understand purpose, architecture, data flow, dependencies.

**1b — Map the structure:**
```bash
# Top-level directory structure
find . -type f -not -path './node_modules/*' -not -path './.git/*' -not -path './venv/*' | sort | head -60

# Build config — also reveals dependency layers
moon print 2>/dev/null || moon project 2>/dev/null || cat .moon/tasks.yml 2>/dev/null
# Note: moon print (moon <1.0) or moon project (moon 2.x) output shows the
# dependency graph — note which modules depend on which. This informs the
# fix order later (lowest layer first).

# Recent commits (if any) — check if git history exists for git blame later
git log --oneline -5

# Dependency graph — generate and save to file (source of truth for all later phases)
(moon print 2>/dev/null || moon project 2>/dev/null) | head -60 > /c/Projects/<project-root>/temp/moon-dependency-graph.md
```

The generated `temp/moon-dependency-graph.md` is the **source of truth** for the entire codebase structure (core models → services → API → frontend). Read these critical files: `README.md`, `moon.yml`, `pyproject.toml`, `package.json`, `.env.example`, `Dockerfile`, `docker-compose.yml`, key `.proto` files (gRPC service definitions), SQLAlchemy model files, main app entry points, test configuration + one sample test file.

**🔴 Dependency Chain Check — Frontend & Backend (regardless of stack):**
- **Frontend (HTML/JS):** 1. Curl every CDN/import URL — confirm 200 OK · 2. Curl imported files and check their **internal** imports — bare specifiers (e.g. `from 'three'`) or relative paths? · 3. Bare specifier ⇒ the page **must** have an import map · 4. Verify `<script type="importmap">` maps it to the correct CDN URL · 5. Check version compatibility (e.g. OrbitControls from Three.js X must match main Three.js X)
- **Backend (Python/Node):** 1. Verify all requirements/packages resolve (`pip install -r requirements.txt` or `npm install` completes) · 2. Check import-time crashes: `python -c "from app.main import app"` before starting the server · 3. Look for deliberate import blockers (a route file importing a nonexistent module to prevent server boot — a common task-style trap) · 4. Check version conflicts between direct and transitive dependencies · 5. For compiled languages (Rust, Go): verify crate/module resolution before building

**Why:** The Tetris debug case proved how easy this is to miss — ACP agents fixed 16 game logic bugs but never caught that `OrbitControls.js` imports `'three'` as a bare specifier with no import map — the real reason the game never started.

**🏗 Large repo variant (70MB+ / 100K+ lines):** Subagents 2 → 4 (split by module, all dispatched in parallel via separate `delegate_task()` calls, same 15-min budget): **A** Architecture big picture (configs, entry points, README, tree) · **B** Backend security + auth (secrets, SQL injection, auth, CORS via `rg`) · **C** Backend perf + reliability (N+1, error handling, session leaks via `rg`) · **D** Frontend + browser (UI patterns, console.log, XSS, state issues). Browser discovery: main routes only, console errors + API docs only. File reads: `rg` for targeted pattern search (handles 500K lines in ~10s). Rubber duck: single duck `ask_duck(provider: "grok")` directly instead of `--squad quick` (3 ducks too slow for large repos).

**1c — Parallel subagent dispatch (🔴 KEY STEP):** 🔴 DISCOVERY ONLY — NO FIXING. 🔴 GIT BLAME IS MANDATORY — for every bug, run `git blame -L <line>,<line> <file>`; include author, commit hash + date, and commit message in the report; if no meaningful git history, note "No git history available" (never skip the check). Spawn two subagents simultaneously (individual `delegate_task()` calls stack and run in parallel; `max_concurrent_children` limits batch size, NOT total parallelism). Verify both output files exist before 1d — subagents can silently fail to write files.

**⚡ Kick off moon `:test` in background** while subagents discover bugs — warms the dependency graph + test cache so Phase 1e results print instantly:
```bash
cd /c/Projects/<project-root>/repo
moon :test &
```

**Subagent A — Architecture & Big Picture:** `delegate_task(goal="Produce a merged architecture document from the repo. Save as file.", context="Repo at C:\Projects\<project-root>\repo — Produce ONE merged document: big-picture-architecture-v1.md. Include: What the app does when working correctly. Architecture flow, data model, components, routes/endpoints, dependencies, entry points. Also per-module breakdown: purpose, files, key classes, inter-module dependencies, entry points. Save to C:\Projects\<project-root>\big-picture-architecture-v1.md (project root)", toolsets=['terminal', 'file'])`

**Subagent B — Bug Discovery:** `delegate_task(goal="Audit the repo for bugs across all categories. Save as bugs-report-v1.md.", context="Repo at C:\Projects\<project-root>\repo — Scan for: Security (hardcoded secrets, SQL injection, missing auth, XSS, CORS misconfig), Performance (N+1 queries, no pagination, blocking calls, React re-rendering perf), Reliability (missing error handling, no retries, resource leaks, missing loading/error states), DX (slow builds, missing types, test gaps), Correctness (race conditions, edge cases, state mgmt). Split findings: GROUP 1 — Simple/local fixes; GROUP 2 — Complex fixes. For each bug: severity (Critical/High/Med/Low), file:line, reproduction steps, root cause, 🔴 MANDATORY git blame metadata. If no git history, note 'No git history available'. Save to C:\Projects\<project-root>\bugs-report-v1.md (project root)", toolsets=['terminal', 'file'])`

**1d — Run the app locally:**
```bash
# Check if target ports are in use before starting servers
netstat -ano | grep -E ':3000|:5173|:8000|:50051' 2>/dev/null || echo "Ports free"
```
Never assume a server is responding just because the process started. If a port is occupied, kill the process or change it in the app config (e.g. `vite.config.ts` `server.port`).

**🔴 Check for import-time crashes before starting the server** (a deliberate `import nonexistent_module` in a route file crashes at import time with `ModuleNotFoundError` before any server banner):
```bash
# Pre-flight: verify critical imports work before starting the server
python -c "from app.api.routes import router; print('Imports OK')" 2>&1 || echo "Import error detected — check output above"
```
```bash
cd /c/Projects/<project-root>/repo
# Start dev server (exact command depends on the repo)
moon run backend:dev 2>/dev/null || python main.py 2>/dev/null || npm run dev
```
**🔴 After starting the server, verify it is actually responding:**
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:<port> || echo "Server not responding"
```
"Process started" ≠ "server responding." Add any findings to `bugs-report-v1.md`.

**1e — Baseline test run:**
```bash
cd /c/Projects/<project-root>/repo
# Check for test scripts before running — many repos have no test runner configured
# Look at package.json scripts, pyproject.toml, moon.yml for test tasks first
for f in package.json pyproject.toml moon.yml; do
  [ -f "$f" ] && grep -E '"test"|pytest|jest|vitest' "$f" >/dev/null 2>&1 && echo "Test script found in $f"
done
# Then run whatever is available
moon test 2>/dev/null || pytest 2>/dev/null || npm test 2>/dev/null || echo "No test command found"
```
Document what passes/fails at baseline — this is your truth source for regression detection. **If no test runner exists:** run `tsc --noEmit` (TypeScript) or `python -m compileall .` (Python) as a bare-minimum compile check; document the absence of tests as a finding.

**1f — Browser Discovery (🔴 TIME-PRESSURE MODE: SKIP THIS PHASE entirely — static code analysis wins over live browser exploration).** Normal workflow only: start servers in background (`docker compose up -d` or `nohup python3.12 backend/main.py & nohup npm run dev &`), confirm with `curl localhost:8000/health`. Frontend checks per route: `browser_navigate("http://localhost:5173")` → `browser_console()` (errors/warnings/uncaught exceptions) → `browser_vision(question="Does this page have visual bugs, blank areas, missing elements, broken layouts?")` → click through flows → document URL + what broke in `bugs-report-v1.md`. Look for: console errors (React crashes, 404 API calls), broken UI, missing loading/error/empty states, broken navigation, form issues, performance, React key warnings / infinite re-renders / stale state. Backend checks: `browser_navigate("http://localhost:8000/docs")` (Swagger UI loads), test a GET endpoint, check health endpoint, check for verbose error messages (stack traces leaked to client), check auth responses. Then present findings to the user (servers stay running for the user to verify; admin login example: admin@example.com / password).

**Phase 1 Deliverables Checklist — HARD GATE (before Phase 2):**
```bash
ls -la /c/Projects/<project-root>/big-picture-architecture-v1.md
ls -la /c/Projects/<project-root>/bugs-report-v1.md
ls -la /c/Projects/<project-root>/temp/moon-dependency-graph.md
```

| # | Required File | Phase Step | What it contains |
|---|---------------|------------|-----------------|
| 1 | `big-picture-architecture-v1.md` | 1c (Subagent A) | Full architecture doc |
| 2 | `bugs-report-v1.md` | 1c (Subagent B) | All bug findings consolidated |
| 3 | `temp/moon-dependency-graph.md` | 1b | Moon dependency graph (source of truth for structure) |

If any file is missing, DO NOT proceed — return to the missing step and complete it (re-run the subagent or run `moon project <id> --json` for each project).

### Phase 2 — Rubber Duck Verification (8 min)

🔴 **MANDATORY PRE-FLIGHT — before ANY duck interaction:** 1. `skill_view(name='rubber-duck-council')` to reload the full toolkit (do NOT rely on memory) · 2. Verify the filesystem bridge is alive: `mcp__rubber_duck__mcp_status()` — confirm `filesystem_readonly-mcp` is healthy · 3. Re-read the "File-Read Access (Bridge Tool) 🆕" section — ducks read files via `sandboxfs_*` tools; pass FILE PATHS, not file contents.

**Method:** rubber-duck-council's **quick compare** mode (fastest — no debate rounds, just compare + king duck synthesis, ~20–40s instead of 2–5 min):
```python
# 🔴 MUST load rubber-duck-council skill first to find the wrapper script location
skill_view(name='rubber-duck-council')
# The wrapper script path is printed in the skill output — copy it from there.
# Do NOT hardcode the path or guess — it may change between Hermes versions.
```
```bash
# Default: quick squad (3 ducks), compare mode (fastest)
python <wrapper-path-from-skill> --mode compare "prompt..."

# If you need all 6 ducks for thoroughness:
python <wrapper-path-from-skill> --mode compare --squad max "prompt..."

# If your prompt contains long file paths, use --file to pass them:
python <wrapper-path-from-skill> --mode compare --file C:\path\to\file.txt "instruction..."
```

**🔴 HARD RULE:** DO NOT use `--squad max` unless the user explicitly asks — default is always `--squad quick` (3 ducks). All 6 ducks waste OpenRouter API budget and add 2–3x latency.

**What to feed the ducks:** `big-picture-architecture-v1.md` · `bugs-report-v1.md` · `temp/moon-dependency-graph.md` · path to the actual repo (ducks have filesystem read access).

**Duck prompts:**
- **Prompt 1 — Verify architecture:** *"Read the dependency graph at {project}/temp/moon-dependency-graph.md... Is it accurate? Did we miss any critical component or dependency? Are the dependencies correct?"*
- **Prompt 2 — Verify bug findings + missed bugs:** *"Here's a bug report for this codebase at {repo_path}. Review each finding: 1. Is it a real bug? (false positive check) 2. Is the severity correct? 3. Are there additional bugs we missed in these same areas? 4. Are there bugs in completely different areas we didn't discover at all? For each confirmed bug, verify by tracing the code path."*
- **Prompt 3 — Security-focused deep audit (use `duck_debate` for sharpest critique):** *"Conduct a focused security audit... Hardcoded secrets / credentials in source · SQL injection vectors (raw queries, f-string SQL) · Missing authentication on gRPC endpoints · Missing input validation · Insecure data storage · Rate limiting absence · Any OWASP Top 10 vulnerability"*

**Update docs with duck findings:** ducks found more/corrections → create `bugs-report-v2.md` (and `big-picture-architecture-v2.md` if architecture was corrected); keep v1 files as reference.

### Phase 3 — Fix Planning (8 min)

**Purpose:** Design surgical, minimal fixes for every confirmed bug. Classify by triage matrix (P0/P1 = fix, P2 = document, P3 = skip).

**🔴 SURGICAL FIX RULE:** Each fix in `proposed-fix-v1.md` MUST specify: exact file path · exact line number(s) · current code (the "before", quoted from the actual file) · replacement code (the "after") · one-line rationale. If a fix cannot be described in under 5 lines of code change, it is NOT surgical enough — reconsider and narrow the scope. Do not restructure, refactor, or rewrite surrounding code.

**Structure of `proposed-fix-v1.md`** — organized by triage priority first, then dependency layer (from moon graph), then by round. Fix order by layer: **Layer 0** Core models/DB (foundation) → **Layer 1** Backend services → **Layer 2** API endpoints → **Layer 3** Frontend (independent fix possible). Always fix lower layers first — a Layer 0 fix may require re-testing Layers 1–3; a Layer 3 fix only needs frontend tests.

```markdown
# Proposed Fix — v1

## 🔴 P0 — Must Fix (highest priority)
### Round 1 — Simple fixes
| Bug | File | Fix |
|-----|------|-----|
| Hardcoded API key | utils.py:36 | Move to .env |
| Broken import | items.py:8 | Remove NonExistentModel |

### Round 2 — Complex fixes
| Bug | File | Fix | Depends on |
|-----|------|-----|-----------|
| SQL injection | crud.py:35 | Parameterize query | — |
| Missing auth | items.py:14 | Restore CurrentUser | — |

## 🟡 P1 — Fix If Time Allows
### Round 1 — Simple fixes
| Bug | File | Fix |
|-----|------|-----|
| Missing 404 check | items.py:42 | Restore HTTPException |

### Round 2 — Complex fixes
| Bug | File | Fix | Est. time |
|-----|------|-----|-----------|
| N+1 query | items.py:28 | selectinload | 10 min |

## 🟢 P2 — Document Only
- Bug 2: console.log leaking IDs → noted in bugs-report
- Bug 5: TODO in code → noted in bugs-report

## ⚪ P3 — Skip
- Code style issues, test gaps
```

**Agreement gate:** After ducks approve, present the fix scope to the user (P0 confident, P1 if time allows, P2/P3 documented only) and ask: *"Do you agree with this scope? If yes, I'll build the task registry with only these P0 and selected P1 tasks."* 🔴 Do NOT proceed to Phase 4 until the user explicitly agrees. Task registry should ONLY include approved tasks — P2/P3 never get tasks.

**Duck edge-case audit (quick compare):** feed `proposed-fix-v1.md` (+ `bugs-report-v1.md`/`-v2.md`):
```bash
python scripts/duck-research-wrapper.py --mode compare "Review this proposed fix document against the codebase..."
```
Questions: 1. Does it actually solve the root cause? 2. Does it introduce new bugs or edge cases? 3. Is the fix minimal, or does it overreach? 4. Are there back-compat concerns? 5. Does it break existing tests? Issues found → bump to `proposed-fix-v2.md` → re-audit → repeat until clean.

### Phase 4 — Task Registry & Handoff (5 min)

**Purpose:** Decompose only the **user-approved fixes** into executable tasks (P0 + user-approved P1). P2/P3 NEVER get tasks.

**Create `task-registry-v1.md`** — organized by dependency layer first, then round (lower layers always execute first). **🔴 Every task entry MUST include:** Task ID + Bug ID reference · Priority + Round · File path (absolute) · Exact line number(s) · Current code (the "before", quoted exactly) · Fixed code (the "after") · One-line rationale · Verification command for that specific fix · Estimated time.

**🔴 COMMIT MESSAGE TEMPLATE — every task entry MUST include a 4-line commit message template:**
- **Line 1 (ID line):** `[$BUG_ID] [$TASK_ID]: <one-line summary>`
- **Line 2 (Problem):** `Problem: <what was wrong, in plain English>`
- **Line 3 (Fix):** `Fix: <what we changed, in plain English>`
- **Line 4 (Reasoning):** `Verification: <how to confirm it works>\n\nRefs: Task-Registry <TASK_ID>, Bugs-Report v2 <BUG_ID>`

**Example:**
```
[B-BUG-005] [T-001]: Remove broken import that prevents backend boot

Problem: routes.py imports nonexistent_module on line 6, causing ImportError that blocks server boot.
Fix: Removed import statement from routes.py.
Verification: Backend boots successfully, /api/user endpoint responds 200 OK.

Refs: Task-Registry T-001, Bugs-Report v2 B-BUG-005
```

This template is the **source of truth** the fix session copies verbatim into each `git commit -m` — the fix session does NOT generate commit messages independently. If a task cannot specify the fix at line-level detail, the fix is not understood well enough — go back and investigate. Vague tasks ("fix SQL injection") produce over-engineered fixes; precise tasks ("change line 34 from `f"SELECT * FROM users WHERE email = '{email}'"` to `text("SELECT * FROM users WHERE email = :email"), {"email": email}`") produce surgical fixes. The task registry is the **fix manifest** — subagents execute from it; the main agent creates this file directly (never delegated).

```markdown
# Task Registry — Fix Session

## 🔴 SURGICAL FIX RULE — READ BEFORE EXECUTING
- Touch MINIMAL code. Change only the lines identified in each task.
- Do NOT restructure, refactor, or rewrite surrounding code.
- Do NOT add new files unless absolutely necessary.
- Do NOT change imports unless the fix requires it.
- Each fix = one code change = one commit.
- If a fix seems to require rewriting a function, STOP and reconsider — you're over-engineering.

## Dependency order (from moon graph)
Layer 0: Core models / DB → Layer 1: Backend services → Layer 2: API endpoints → Layer 3: Frontend

## 🔴 Round 1: P0 Simple Fixes
| # | Triage | File(s) | Change | Verification |
|---|--------|---------|--------|-------------|
| 1 | P0 🔴 | utils.py:36 | Move API key to .env | Run tests |
| 2 | P0 🔴 | items.py:8 | Remove NonExistentModel import | App boots |

## 🟡 Round 1: P1 Simple Fixes
| # | Triage | File(s) | Change | Verification |
|---|--------|---------|--------|-------------|
| 3 | P1 🟡 | items.py:42 | Restore 404 check | GET nonexistent item |

## Round 2: Complex Fixes (all P0, P1 if time)
| # | Triage | Depends on | File(s) | Change | Verification |
|---|--------|-----------|---------|--------|-------------|
| 4 | P0 🔴 | — | crud.py:35 | Parameterize query | Test SQL injection |
| 5 | P0 🔴 | — | items.py:14 | Restore CurrentUser | Auth check passes |
| 6 | P1 🟡 | Task 4 | items.py:28 | selectinload | N+1 gone |
```

**Create `fix-handoff-v1.md`** in `C:\Projects\<project-root>\debug-fix-handoff\` — contains: context (repo path, reference copy, model for this session, "This session is Phase 5 of the app-debug-workflow", dependency graph at `repo/.moon/`), dependency order (fix lower layers first, `moon :test` after each layer), what to fix (task-registry Round 1), critical rules (load app-debug-workflow skill; one commit per fix with atomic messages; run tests after EVERY change; never break existing functionality; browser-verify UI fixes; announce "Round 1 fix is done, proceeding to Round 2" and "Phase 5 complete — all fixes applied"), and the completion signal (all tasks complete, all tests pass, git status clean).

**Create `/goal draft` prompt** — `/goal draft "..."` triggers Hermes' **completion contracts** feature (v0.18+): the plain-language objective expands into a structured contract (outcome, verification, constraints, boundaries, stop_when) and auto-continues until achieved. **🔴 COMMIT MESSAGE FORMAT REQUIREMENT — HARD RULE:** every `git commit -m` must use the 4-line template; **NO ONE-LINERS ALLOWED** — `git commit -m "fix: T-001"` will be rejected. The copy-paste block for the fix session: `/goal draft "Execute fixes from task-registry-v1.md in [project-root]/repo. Follow the fix-handoff-v1.md instructions. This is Phase 5 of app-debug-workflow. Load app-debug-workflow skill first. SURGICAL FIXES ONLY — touch minimal code, change only the lines identified in each task, do not restructure or refactor surrounding code. One commit per fix. Run tests after every change. Use browser to verify UI fixes. Notify after Round 1 and Round 2. Do NOT do git push — the main session handles git after verification. 🔴 COMMIT MESSAGE FORMAT: Every commit must use the 4-line template from the task registry: ID line + Problem + Fix + Verification + Refs. NO ONE-LINERS. Copy the exact commit message template from each task in task-registry-v1.md. This is mandatory for the task."`

**Duck final verification (quick compare):** feed updated proposed fix (v1 or v2), `task-registry-v1.md`, `fix-handoff-v1.md`, and the `/goal draft` prompt: *"Review these documents. Are the tasks properly decomposed? Correct order? Any missing steps? Will executing this task registry produce the fixes described in the proposed fix doc? Is the handoff doc complete enough for another agent to execute?"* Issues → `-v2` versions → re-audit.

**⚡ Parallel optimization — prepare v1.1 while v1 executes:** as soon as the user takes v1 to the fix session, dispatch a subagent to create `task-registry-v1.1.md` + `fix-handoff-v1.1.md` for the P2 documented fixes (single round, no duck audit needed — P2 fixes are simple/isolated/low-risk and already documented in bugs-report). Save both to `C:\Projects\<project-root>\debug-fix-handoff\`. Cost: zero (primary session is idle during the ~20 min fix session).

### Phase 5 — Fix Execution (Session B, 25 min)

**Fix execution strategy (before dispatching Round 1):**
1. **Create a fix brief first** — spawn a research subagent to read ALL source files + ALL planning docs (bugs-report, proposed-fix, task-registry) and produce `temp/fix-brief-v1.md` with, per bug: bug ID, task ID, file path, exact line numbers, current code (quoted in a code block), replacement code (quoted in a code block), one-line explanation. The brief is the single source of truth for fix subagents.
2. **Group fixes by file for parallel subagent dispatch** — prevents race conditions (two subagents editing the same file will conflict):
   - Subagent 1: all `routes.py` fixes (T-01, T-02, T-05, T-06, T-12, T-13, T-14, T-19)
   - Subagent 2: all `main.py` + `database.py` + proto fixes (T-03, T-04, T-09, T-10, T-11, T-15, T-16, T-23, T-24)
   - Subagent 3: all `App.tsx` fixes (T-07, T-08, T-17, T-18, T-22)
3. **Verification subagents can fail silently** (max_iterations, no summary) — if so, the main agent does the boot verification directly. See `references/fix-execution-playbook.md` for the exact boot-test sequence.

**Fallback chain for fix execution** (if the primary coding agent fails, fall through in order): 1. **ACP with the user's preferred strong coder** (primary; e.g. MiniMax M3) · 2. **Subagent with the user's fast capable model** (fallback; `delegate_task` with explicit fix instructions from the fix brief; e.g. DeepSeek v4 Pro) · 3. **Manual coding with `write_file`/`patch`** (last resort; single-file, simple fixes only). Do NOT give up after ACP fails — always try at least one fallback before going manual.

**🔴 Time exhaustion fallback — create `temp/fixed-vs-no_fix.md`:** if the fix session exhausts its time budget: 1. Immediately stop all fix subagents, do NOT start new tasks · 2. Create `temp/fixed-vs-no_fix.md` with ✅ Fixed (committed) table (Task ID, Bug ID, Priority, File, Commit) and ❌ Not Fixed (time exhausted) table (Task ID, Bug ID, Priority, File, Reason) · 3. For each ❌ task include the Problem and Fix from `task-registry-v1.md` — the reviewer needs to know what was intended · 4. Commit and push whatever is done — uncommitted work is worthless · 5. Tell the user: *"Time exhausted. I've documented what's fixed and what's not in `fixed-vs-no_fix.md`. Phase 6 will pick up from here."* This file is the bridge between Phase 5 and Phase 6.

**Round 1 — Simple fixes:** applied first (isolated, no cross-module impact). One commit per fix with detailed body. **Use moon's dependency tracking:**
```bash
moon :test   # only runs tests for changed modules and their dependents
```
Saves 5–15 minutes per iteration vs the entire 500K-line test suite. UI bugs → browser tools to verify visually. After all Round 1 done → notify user: *"Round 1 fix is done, now proceeding to Round 2"* → only then begin Round 2.

**Round 2 — Complex fixes (broad → narrow):** fix the module with widest impact first, test after each module fix (always `moon :test`), then narrower-impact modules. UI bugs → browser verify. After all Round 2 done → notify: *"Round 2 is done. Phase 5 complete — all fixes applied."* Return to debug session for validation.

**Blockers:** document in `C:\Projects\<project-root>\temp\` with a descriptive filename, complete what can be done, return to the debug session with the blocker report.

### Phase 6 — Validation + Git Push (7 min)

**Purpose:** Verify all fixes work, no regressions. If some fixes missed the mark, create a v2 handoff for another round. Only push when everything is clean.

**🔴 Time exhaustion check — read `fixed-vs-no_fix.md` if it exists:**
```bash
ls /c/Projects/<project-root>/temp/fixed-vs-no_fix.md 2>/dev/null && echo "FOUND" || echo "NOT FOUND"
```
**If FOUND:** pull the ❌ "Not Fixed" list; for each ❌ task pull Problem/Fix/Verification from `task-registry-v1.md`; add a **"## Tasks Not Fixed (Time Constraint)"** section at the end of `fix-summary-v1.md`; each entry MUST have the same four fields as fixed tasks (File, Problem, Fix, Verification):
```markdown
## Tasks Not Fixed (Time Constraint)

### T-018 [P1] [B-BUG-022] Add Suspense boundary for lazy-loaded components
- **File:** repo/frontend/src/App.tsx, line 45
- **Problem:** React.lazy used without Suspense fallback causes runtime crash during chunk loading.
- **Fix:** Wrap lazy-loaded component in <Suspense fallback={<div>Loading...</div>}>.
- **Reason not fixed:** Time exhausted before frontend P1 round (90-min hard limit reached).
```
🔴 HARD RULE: not-fixed tasks get the SAME level of detail as fixed tasks. "Ran out of time" is an acceptable answer — silence is not. **If NOT FOUND:** all tasks completed, skip this section.

**Full test suite — leverage moon's caching:**
```bash
cd /c/Projects/<project-root>/repo
moon :test
```
Moon only tests changed modules; unchanged modules return cached results instantly.

**Browser re-verification:** UI fixes verified in browser; check console for new errors.

**🔴 Surgical fix verification (3-way diff):** requires three folders — `repo/` (fixed), `repo-src/` (buggy, no fixes), `repo-src (no bug)/` (original clean, if available):
```bash
# Diff fixed vs clean original — should show ONLY bug-fix lines, nothing else
diff -r repo/ "repo-src (no bug)/" --exclude=node_modules --exclude=.git --exclude=__pycache__ --exclude=app.db | head -80
```
Lines matching the bug-fix tasks → GOOD (surgical). Unrelated changes (restructured imports, rewritten functions, new files, changed formatting) → BAD (over-engineered) — flag as regressions. If over-engineering is detected, document which fixes need to be redone surgically and create a v2 task registry for those fixes only.

**If bugs remain (incomplete fixes):** create `task-registry-v2.md` (only tasks not fixed properly) → `fix-handoff-round-2.md` (remaining issues only) → updated `/goal draft` prompt → update `bugs-report-v1.md` or create `bugs-report-v2.md` → tell the user: *"Some fixes need another pass. Here's the v2 handoff. Take these back to the fix session."* → back to fix session → repeat until clean.

**Generate `fix-summary-v1.md` — mirrored commit detail:** every task section MUST mirror the git commit detail — no one-liner checklists. 🔴 HARD RULE: every task includes ALL four fields — File, Problem, Fix, Verification — no "see commit message" references; the fix-summary IS the deliverable the reviewer reads and must stand alone:
```markdown
### T-001 [P0] [B-BUG-005] Remove broken import that prevents backend boot
- **File:** repo/backend/app/api/routes.py, line 6
- **Problem:** Import of `nonexistent_module` causes `ImportError`, backend cannot boot.
- **Fix:** Removed `import nonexistent_module` statement.
- **Verification:** Backend boots successfully (`python -c "from app.main import app; print('OK')"` returns OK).
```
Save to `C:\Projects\<project-root>\fix-summary-v1.md` (project root).

**Documentation for each fix:** verify each commit body includes Problem / Root cause (specific file/line/pattern) / Fix (why this exact change is correct) / Verification (test results): `git log --oneline`.

**Git push — final step:**
```bash
cd /c/Projects/<project-root>/repo
```
**Step 1: Stage and commit the fix-summary-v1.md:**
```bash
git add fix-summary-v1.md
git commit -m "[FIX-SUMMARY] Document all bugs, fixes, and time-constraint gaps

Problem: Reviewer needs to understand full scope of work at task end.
Fix: Included fix-summary-v1.md with 4-field format per task (Problem/Fix/Verification)
  for all completed tasks and all time-constraint gaps (from fixed-vs-no_fix.md).
Verification: File exists, contains all P0/P1 fixes, documents all skipped tasks
  with clear instructions on how to fix if time permits.

Refs: Task-Registry v1, Bugs-Report v2, Time-Constraint Report (if exists)"
git push
```
**Step 2: Push remaining fix commits (20 individual commits for each T-XXX).** Final step before the 90-min timer expires. If the push fails due to auth, ask the user to authenticate.

---

## 📁 Files & Deliverables

```
C:\Projects\<project-root>\
  ├── AGENTS.md                        ← system prompt
  ├── repo\                            ← working copy (fixes happen here)
  ├── repo-src\                        ← untouched clone (reference)
  ├── big-picture-architecture-v1.md   ← architecture & module breakdown
  ├── bugs-report-v1.md                ← all bug findings
  ├── proposed-fix-v1.md               ← fix plan
  ├── task-registry\                   ← task breakdown docs
  │   └── task-registry-v1.md
  ├── debug-fix-handoff\               ← handoff docs between sessions
  │   └── fix-handoff-v1.md
  └── temp\                            ← scratch files
```

**File location quick reference:**

| Document | Save to | Notes |
|----------|---------|-------|
| `big-picture-architecture-v1.md` | **Project root** (per AGENTS.md folder structure) | Created in Phase 1c |
| `bugs-report-v1.md` | **Project root** (per AGENTS.md folder structure) | Updated throughout Phase 1 |
| `proposed-fix-v1.md` | **Project root** (per AGENTS.md folder structure) | From Phase 3 |
| `task-registry-v1.md` | `task-registry/` | For fix session |
| `fix-handoff-v1.md` | `debug-fix-handoff/` | For fix session |
| Temp files | `temp/` | Anything temporary |

Plus phase-specific files: `temp/repo-size-check.md` (Phase 0), `temp/moon-dependency-graph.md` (Phase 1b — source of truth), `temp/fix-brief-v1.md` (Phase 5), `temp/fixed-vs-no_fix.md` (Phase 5 time-exhaustion bridge), `fix-summary-v1.md` (Phase 6, project root), `bugs-and-fixes-report-<YYYYMMDD>.md` (post-build bug review, build workspace root), and `-v2` versions of any corrected doc.

**This skill folder contains:**
```
app-debug-workflow/
  ├── SKILL.md                          ← this workflow (full 90KB spec)
  └── references/
      ├── fix-execution-playbook.md                     ← exact boot-test sequence & verification issues
      ├── path-stale-registry-and-missing-artifacts.md  ← pre-clone registry paths + gitignored artifacts
      └── python-venv-isolation-windows.md              ← fix recipe for Hermes venv contamination
```

**Note:** "Project root" = the root folder of the project being debugged (where AGENTS.md lives). The workflow is not specific to one task — it works for any project.

---

## ⏱ Time Budget & Abort Protocols

**Time Budget Management (CRITICAL — target 73 min, 17 min buffer):**

| Phase | Duration | Cumulative | If running behind |
|-------|----------|------------|-------------------|
| Phase 0 — Pre-Flight + Clone | 8 min | 8 min | Skip (should be done before the task) |
| Phase 1 — Recon (static only in the task) | 15 min | 23 min | Skip browser step (1f) — time-pressure mode skips this automatically |
| Phase 2 — Duck Verify | 8 min | 31 min | Only ask security-specific ducks |
| Phase 3 — Fix Planning | 8 min | 39 min | Skip complex fixes, focus on simples |
| Phase 4 — Task Registry | 5 min | 44 min | Minimize documentation, skip duck final verify |
| Phase 5 — Fix Exec | 25 min | 69 min | Only P0 + P1 fixes |
| Phase 6 — Validation + Push | 4 min | 73 min | Verify only, push whatever is committed |
| **Buffer** | **20 min** | **90 min** | **Absorbs any phase overrun or accident** |

**Hard rule at 80 min:** Stop fixing. Commit what's done, document remaining findings in `bugs-report.md` with severity and fix guidance, and **push**. A partially-fixed audit with clear documentation beats rushing and breaking things.
**Hard rule at 85 min:** Stop everything. Push whatever is committed. Uncommitted work is worthless.

**📋 Abort/Fallback Protocols:**

| Time remaining | Situation | Action |
|---------------|-----------|--------|
| **T-30 min** (60 min elapsed) | Behind schedule | Skip Phase 2 (duck verify), go straight to fix planning. P2/P3 bugs get documented only. |
| **T-15 min** (75 min elapsed) | Still fixing | **Stop fixing.** Commit whatever is done. Skip Phase 6 validation — just run tests and push. |
| **T-10 min** (80 min elapsed) | 🔴 HARD STOP FIXING | `git add`, `git commit`, `git push`. Document remaining findings in a quick notes file. |
| **T-5 min** (85 min elapsed) | Push failed | Try `git push` again. If still failing, zip the repo folder: `zip -r task-output.zip repo/` and save to desktop. Tell the user to upload manually. |
| **Docker dead** | Container won't start | Switch to SQLite (check if app supports it). If not, document the issue and move to static code analysis only. |
| **Model timeout** | Subagents timing out | Switch to manual mode — read files directly, use `rg`/`grep` for pattern scanning. Skip subagents entirely. |
| **Git push auth fail** | SSH key rejected | Try: `git remote set-url origin https://<token>@github.com/...` or ask user for credentials. Last resort: zip repo. |

---

## 🔒 Hard Rules & Disciplines

### 🔴🔴 Subagent Blank-Slate Rule (applies to ALL phases)
Every subagent prompt MUST include: exact file names to create or read · absolute output paths (never relative, never assumed) · expected format/structure of the output · all relevant context (subagents do NOT have access to AGENTS.md, prior phases, conversation history, or the agent's memory). Subagents are **blank slates** — spell out everything explicitly in every `delegate_task()` call.
- BAD: `"Produce an architecture document and save it."`
- GOOD: `"Save the architecture document as big-picture-architecture-v1.md at C:/Projects/<project-root>/big-picture-architecture-v1.md. Include: app purpose, architecture flow, data model, components, routes, dependencies, entry points, per-module breakdown."`

### 🔴🔴 Subagent Temp-File Rule — No Collisions (applies to ALL phases)
**TRIGGER:** whenever 2+ subagents contribute to the same final deliverable file. 1. Assign each subagent a unique temp filename in `temp/`: `temp/<deliverable>-<role>-v1.md` · 2. Subagents write ONLY to their assigned temp file — never the final deliverable · 3. The **main agent consolidates** the temp files into the final deliverable at the correct location · 4. Clean up temp files after consolidation. **Example:** Subagent A → `temp/bugs-backend-v1.md`, B → `temp/bugs-frontend-v1.md`, C → `temp/bugs-runtime-v1.md`; main agent merges into `bugs-report-v1.md`, then deletes temps. Single-subagent tasks are unaffected. **Why:** without this, the last subagent to finish silently overwrites all others' work — discovered in practice when a 406-line, 28-bug report was replaced by a 90-line report.

### 🔴🔴 Post-Phase Verification Gate (applies to ALL phases)
After each phase, the main agent MUST verify all expected deliverable files exist at their correct paths before proceeding. If ANY is missing: DO NOT start the next phase → determine why (subagent failed, wrong path) → re-run the subagent or create the file directly → only proceed when all deliverables are confirmed present.

### 🔴🔴 Pre-Flight Gate Before ALL Duck Phases
Before ANY rubber-duck phase (Phase 2, Phase 3 duck audit, Phase 4 duck verify), verify at project root: `big-picture-architecture-v1.md`, `bugs-report-v1.md`, `temp/moon-dependency-graph.md`. Missing any → do NOT start the duck council; return to the prior phase first. Feeding nonexistent files to ducks wastes time and produces garbage.

### Main Agent Orchestrator Rule (context health #1)
The main agent is the **orchestrator** — protecting context health is the #1 priority.

**🟢 Main agent does DIRECTLY (no subagent):**
1. **Rubber duck interaction** — MUST load `rubber-duck-council` skill before ANY duck work; MUST use the wrapper script found inside the skill (never call MCP duck tools directly — the wrapper handles prompt construction, squad selection, file-feeding, synthesis); ALWAYS `--mode compare --squad quick` (3 ducks) unless the user says otherwise, **never** `--squad max` (6 ducks). **LARGE REPO EXCEPTION (70MB+ / 100K+ lines):** don't use the wrapper — use `ask_duck(provider: "grok")` directly, single duck only, passing file paths (not contents) with the sandboxfs bridge instruction. Loading the skill, preparing prompts, calling duck tools, interpreting results — all done directly; never delegate duck work to subagents.
2. Writing/updating the proposed fix doc, fix handoff doc, and `/goal draft` prompt — **never delegated**.
3. Direct conversation with the user (progress updates, phase transitions, presenting findings).
4. Loading skills (`skill_view`, `skills_list`).

**🔴 Main agent MUST delegate to subagents or ACP agents:** reading/analyzing the codebase (Phase 1) · running browser discovery (Phase 1f, Hermes browser tools) · executing bug discovery scans and architecture mapping · running tests and verification · ANY coding work — never write code directly · file operations that produce large output (prevent context bloat).

**Why:** every tool call the main agent makes directly fills the context window with intermediate output. Subagents isolate that noise. If a subagent gets stuck in a loop, the main agent can detect and restart it; if the main agent gets stuck, nobody notices until it's too late.

### Multi-session discipline
- **Session A (debug) NEVER writes code.** Period. All fixes happen in Session B.
- **Session B (fix) NEVER plans.** Use the handoff doc and task registry.
- Handoff docs and task registries are the contract between sessions.

### Screen-share discipline (task-specific)
- Before EVERY phase, announce what comes next and ask "Ready to proceed?" · present the FULL plan between Phase 0 and Phase 1 so the judge sees the workflow · the user should appear engaged and in control on camera.

| Situation | What to say |
|-----------|-------------|
| While subagents scan code | *"Let me give the subagents a moment to analyze the codebase. I'll review their findings as they come in."* |
| While rubber duck compares | *"I'm cross-referencing our findings with multiple AI perspectives to catch blind spots. This takes about a minute."* |
| While reading duck results | (Scrolling through report on screen) *"Good, the ducks confirmed most of our findings. One thing they caught..."* |
| While fix session runs | *"I'm applying the fixes now — running tests between each change to make sure nothing breaks."* |
| If stuck / thinking | *"Let me investigate this path further before deciding on the approach."* |
| If behind schedule | *"We're a bit behind, so I'll prioritize the critical fixes and document the rest."* |
| After each commit | *"One fix done, tests passing. Moving to the next issue."* |

### Skill-writing convention: pronoun clarity
Use **"the user"** (not "you") for the human; use **"I"** or **"the agent"** (not "you") for the agent reading the skill. ✅ *"The user verifies my findings afterward"* · ❌ *"You verify my findings afterward"* (ambiguous — who is "you"?).

### Commit discipline
One commit per issue · `git commit -m "fix: [problem]" -m "Problem: ... \nRoot cause: ... \nFix: ... \nBack-compat: ..."` · clean worktree before moving to the next issue.

### Test discipline
Run tests BEFORE any changes (baseline) · run tests AFTER every change · never declare a fix done without green tests.

### Documentation discipline
Every finding gets documented, even if there's no time to fix it — severity, location, reproduction steps, potential fix. This counts as "diagnostic depth" even when time runs out.

### Subagent discipline (context health)
Phase 1 subagents are the MOST critical — their output is large and would destroy context; always delegate Phase 1. Phase 1 subagents → fast accurate model (e.g. DeepSeek v4 Pro) · Phase 5 fix execution → ACP strong coder (primary) → subagent fast capable model (fallback) → manual (last resort) · Rubber duck → quick compare via wrapper script (`--mode compare`, default `--squad quick`) · files read by ducks → `filesystem_readonly-mcp` bridge (sandboxfs); explicitly tell ducks they have these tools.

---

## ⚠️ Pitfalls & Gotchas

| Issue | Fallback |
|-------|----------|
| `moon print` not found (moon 2.x) | Use `moon project` instead — shows project list and dependencies |
| `moon :test` cold cache (first run) | Kick off `moon :test &` in Phase 1c to warm cache before Phase 1e |
| Moon not in PATH | `source ~/.bashrc` first, or use full path to moon binary |
| Moon toolchain plugin vs runtimes | `moon toolchain download` only installs the plugin. Python/Node runtimes download lazily on first `moon run` — expect a one-time delay. Cached after that at `~/.moon/toolchains/`. |
| **Port collision on dev server start** | Check the port first: `netstat -ano | grep :3000` (or target port). If occupied, kill the process or change the port in the app config (e.g. `vite.config.ts` `server.port`). Subagents may report "server started with no errors" even when the port was taken — always verify with `curl localhost:<port>` afterward. |
| **Import-time crash blocks all startup** | A deliberately broken `import nonexistent_module` in a route file crashes the server at import time with `ModuleNotFoundError`, before any server loop runs — process exits immediately, no port binding, curl just reports "Server not responding." **Pre-flight:** `python -c "from app.api.routes import router; print('OK')"` before starting. Common time-pressure task trap. |
| **Subagent success report not verified** | "frontend started on :3000 with no errors" is NOT proof of accessibility. Always verify: `curl -s localhost:<port>` or `browser_navigate("http://localhost:<port>")`. "Process started" ≠ "server responding." |
| **Patch tool backslash escape on Windows** | The `patch` tool interprets `\r`, `\n`, `\t` in paths as escape chars — `C:\Projects\...\repo` becomes `C:\Projects\...\nepo` (the `\r` is eaten). Use forward-slash paths (`C:/Projects/.../repo/`) in terminal commands, or `write_file` with absolute Windows paths for file creation. |
| **Fabricated bug counts** | Never report bug counts not directly read from `bugs-report-v1.md`. If a subagent summary says 16 bugs, report 16 — do NOT extrapolate, round, or invent "25 injected + 10 natural = 35." If uncertain, say "approximately N based on the subagent summary" and verify against the file. |
| **`uvicorn app.main:app` fails — app not at module level** | Some FastAPI apps define `app` inside a `run_fastapi()` function (multiprocessing pattern) → `AttributeError: module 'app.main' has no attribute 'app'`. Fix: run via `python -m app.main` instead, which triggers the `if __name__ == "__main__"` block that starts both gRPC and FastAPI subprocesses. |
| **Handoff port mismatch vs actual code** | The fix-handoff doc may say port 8000 but `uvicorn.run()` may use 8001. Always read `main.py` for the actual port before curling. Don't trust handoff docs for port numbers — trust the source code. |
| **Verification subagent hits max_iterations** | A subagent booting the backend may hit max_iterations (50 tool calls) with no summary. Main agent should boot-verify directly: (1) `python -c "from app.api.routes import router; print('OK')"`, (2) `python -m app.main` in background, (3) `sleep 6 && curl -s -o /dev/null -w "%{http_code}" http://localhost:<port>/docs`, (4) test individual endpoints with curl. |
| **Seed data email may not match handoff doc** | Handoff may say `GET /api/user?email=candidate1@example.com` → 200, but seed data may use `test@example.com`. If lookup 404s, check what users exist via the admin endpoint (with auth): `curl -s -H "X-API-Key: dev-only-key" http://localhost:<port>/api/admin/users`. |
| **Stale DB state after mutation bug fix** | After fixing a data-mutation bug (e.g. GET endpoint that writes to DB), the SQLite file may still hold stale mutated data — API returns wrong data though source is correct. Verify: (1) kill backend, (2) delete the DB file (`app.db` or similar), (3) restart so it recreates from seed, (4) test. Confirmed: `grep -rn "Modified Name" backend/app/ --include="*.py"` returns nothing (fix in code), but `grep "Modified Name" backend/app.db` returns a match (stale DB). |
| **rm on locked DB file fails silently** | `rm -f app.db` fails with "Device or resource busy" while the backend holds the file. Kill the process first, wait 2–3 seconds, then delete. If `rm` runs in a background terminal the failure may be silent — check exit code or verify the file is gone. |
| **taskkill syntax in git-bash** | `taskkill //F //PID <pid>` fails in git-bash ("Invalid argument/option"). Use `powershell -Command "Stop-Process -Id <pid> -Force"` instead. Or find the PID via `netstat -ano | grep :<port>` and kill via PowerShell. |
| **Practice mode — skip git push** | For practice runs, Phase 6 validation is still required but git push can be skipped. Verify fixes end-to-end (backend boots, API responds, frontend connects, no regressions). Tell the user "no git push needed for practice." |
| **🔴 Copilot shell CWD mismatch** | Launched inside VS Code Copilot shell ("Hermes soul, Copilot shell"), the Hermes session CWD is the Hermes install directory (`C:\Users\<user>\Workspaces-agents\hermes`), NOT the VS Code workspace. Subagents inherit this and create files at the wrong location. **Workaround:** (a) absolute paths in ALL subagent prompts and `write_file`/`patch` calls — never relative; (b) pass `workdir` to `terminal()`; (c) permanent fix: update session CWD in `state.db` directly (`UPDATE sessions SET meta = json_set(meta, '$.cwd', '<project-root>') WHERE id = '<session-id>'`). Do NOT trust subagent file paths without verifying with `ls`/`search_files`. Backup state.db before modifying. |
| **🔴 Fabricated verification claims** | Saying "File verified on disk (3.5 KB)" without running a check is a critical trust violation. NEVER claim a file exists unless `search_files` or `terminal ls -la` confirmed it IN THIS TURN. "I wrote the file" ≠ "the file exists." Subagent reports are claims, not facts — verify independently. If you cannot verify, say "I cannot verify that." Applies to: file existence, bug counts, port availability, server responsiveness, test results. |
| **🔴 Narrating instead of executing** | When the user says "go" or "feed the ducks," the tool call MUST happen in the SAME response. No "I'll do it next" — do it now. Tool-use enforcement is absolute. |
| **3-way diff for surgical fix verification** | Diff the fixed repo against BOTH the buggy and original clean versions (three folders: `repo/`, `repo-src/`, `repo-src (no bug)/`). Run `diff -r repo/ "repo-src (no bug)/"` — output should show ONLY bug-fix lines. Unrelated changes = over-engineering. Catches fix-session drift toward rewriting instead of patching. |
| **🔴 Task registry old_string ≠ actual file content** | In Session B, the registry's `old_string` may not match the file on disk (line endings/whitespace differences, a prior fix changed surrounding context, UI title differs from the debug session's assumption). For EVERY task, the fix subagent MUST read the file first and confirm the old_string before calling `patch()`. If it doesn't match, adjust to actual content — the intent of the fix matters, not the exact bytes. (Affected T-020 in practice: registry expected "Vite + React + TS", actual was "TS Frontend".) |
| **🔴 Task registry false positives — bugs already fixed in baseline** | bugs-report may flag issues the baseline already addresses (JWT secret via env var, passwords already hashed, SQL already parameterized). Before writing any task in Phase 4, VERIFY the bug still exists in the actual `repo/` source — don't blindly convert every bugs-report entry into a task. P0-1 (hardcoded JWT) and P0-2 (plaintext passwords) were false positives in the real task: code already used `os.environ.get("GRPC_JWT_SECRET", ...)` and SHA-256 hashing. |
| **🔴 Python venv isolation — Hermes venv contaminates project venv** | The Hermes agent's own venv may pollute the project's Python import path — even when invoking the project venv's Python directly, `google.protobuf` etc. may load from the Hermes venv. **Fix recipe in `references/python-venv-isolation-windows.md`.** Short version: `unset VIRTUAL_ENV PYTHONHOME PYTHONPATH && export PATH="/path/to/project/venv/Scripts:/path/to/system/python:/usr/bin:$PATH"`. Verify with `python -c "import google.protobuf; print(google.protobuf.__file__)"` — must point to the project venv. 61 tests that failed under contaminated env passed instantly once isolated. |
| **🔴 search_files fails on MSYS2/Cygwin paths — fall back to terminal grep** | On Windows (git-bash/MSYS), `search_files` with paths under `/c/Projects/...` frequently fails with "IO error: The system cannot find the file specified" (path resolution bug — retrying does not fix it). **Immediate fallback:** `terminal()` with `grep -rn "pattern" path/`. Do NOT retry `search_files` more than once — it wastes task minutes. |
| **🔴 pnpm-lock.yaml (or any lockfile) uncommitted after Phase 0** | `pnpm install` in Phase 0 modifies lockfiles; the uncommitted artifact persists through all phases and shows in `git status` at Phase 6. **Fix:** commit as `chore: update lockfile after dependency install` during Phase 0, or document in the handoff. |
| **🔴 Task registry paths all wrong (pre-clone) + missing build artifacts** | See `references/path-stale-registry-and-missing-artifacts.md` for two failure modes: (1) task registry written before repo clone → every file path wrong → all P0 bugs false positives; (2) gitignored build artifacts not generated → dev server 500s with import errors. Both discovered during a real task fix session. |
| **🔴 Coding agent hangs (no output) — check logs first** | When a coding agent (OpenCode PTY/ACP) produces no output after timeout, do NOT assume the prompt was wrong. Check `~/.local/share/opencode/log/opencode.log` for `step=N` incrementing, `evaluated permission`, `touching file` — the model was working but ran out of time. Retry with longer timeout. Also look for `Upstream idle timeout exceeded` — OpenRouter's 5-min upstream limit when a reasoning model (e.g. MiniMax M3) is enabled. Fix: disable reasoning (`reasoning: none` in opencode config). |

---

## 🔗 Skill Interactions

| Skill | Role |
|-------|------|
| `filesystem_readonly-mcp` | Read-only file access for ducks (jailed to C:\Builds, C:\Projects). See system-doc for details. |
| `rubber-duck-council` | Verification and audit at every phase — use fire-and-forget hybrid mode. If unavailable, use the **Audit Gate Fallback** (subagent audit with explicit edge-case + gap analysis) |
| `systematic-debugging` | Per-bug investigation methodology |
| `subagent-first` | Always delegate, never implement directly |
| `github-now` | GitHub repo management — create, update, search, plus clone/commit/push via git |
| `complex-project-workflow` | Template this skill was derived from |

---

## 🔍 Search Keywords

`app debug workflow`, `codebase audit`, `bug hunt`, `security review`, `performance audit`, `full-stack debugging`, `multi-session workflow`, `90-minute timebox`, `time-pressure debugging`, `LLM-Base Refactoring`, `Python gRPC`, `SQLAlchemy`, `TypeScript React`, `moonrepo monorepo`, `moon :test`, `rubber duck council`, `duck verification`, `subagent audit`, `task registry`, `fix handoff`, `surgical fix`, `triage matrix`, `P0 P1 P2 P3`, `git blame`, `dependency graph`, `import map`, `bare specifier`, `import-time crash`, `port collision`, `N+1 queries`, `SQL injection`, `hardcoded secrets`, `XSS`, `CORS`, `context health`, `context compaction`, `/goal draft`, `completion contracts`, `fix-summary`, `fixed-vs-no_fix`, `3-way diff`, `surgical verification`, `venv isolation`, `MSYS2 path`, `patch tool backslash`, `taskkill git-bash`, `OpenCode log`, `OpenRouter idle timeout`, `Windows debugging`, `Hermes Agent skill`

---

## 📝 Credits & License

- **Author:** Ringo / MilkyWay008 · [github.com/MilkyWay008](https://github.com/MilkyWay008)
- **Version:** 2.0.0 · **Platforms:** Windows · **Related skills:** `complex-project-workflow`, `systematic-debugging`, `rubber-duck-council`, `subagent-first`, `github-now`
- **Derived from:** `complex-project-workflow` (inverted: audit an existing buggy codebase instead of building from scratch)

Distributed under the **MIT License**. This skill is provided as-is, with no warranty — use it to audit codebases you have permission to audit, and always back up repositories before applying fixes.

---

<p align="center">🔧 Discover → Duck-Verify → Plan → Handoff → Fix → Validate — find every bug, fix it surgically, and ship it before the timer hits zero.</p>
