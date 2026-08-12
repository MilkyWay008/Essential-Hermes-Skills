# AI Agent Obedience Engineering — Getting AI to Actually Work After Reading the Workflow

> Source: 2026 multi-source synthesis (Anthropic Skill Engineering, Microsoft Code Words, Strands Steering Hooks, Gradient Flow Harness Engineering)
> When to use: AI coding agents (various agent CLIs / IDE-embedded agents) that, after reading README/RULES.md, only acknowledge without executing, skip steps, or take liberties omitting critical operations

---

## Core Problem Diagnosis

The root cause of an AI agent "reading the workflow but not doing the work" is not model capability, but **semantic escape room in natural-language instructions**:

| Root cause | Explanation |
|------|------|
| **Context attention decay** | Content in the middle of long documents is down-weighted by the LLM attention mechanism; the agent effectively only "sees" the beginning and end |
| **Semantic overriding** | When optimizing for "helpfulness," the model creatively reinterprets explicit instructions (e.g. reading MUST DO X as "suggested to do X") |
| **Passive language treated as optional** | "Ready for next step → invoke X" is treated as a suggestion rather than an instruction |
| **No state enforcement** | No external state machine validates workflow order, so the agent can skip steps undetected |
| **Silent state corruption** | The agent produces results that are structurally correct but semantically wrong; errors accumulate silently |

---

## Technique 1: Instruction-First Principle (Critical-First Pattern)

**Put "what to do next" at the very top, and context after it.**

```
WRONG (agent ignores):
  [70 lines of project background and tool list]
  → "Next step: run bootstrap to install missing tools"

CORRECT (agent executes):
  "## Execute now: run `bootstrap-reverse.ps1` to check and install missing tools
   → after it finishes, read routing.md to decide which skill to enter"
  [then project background and tool list]
```

**Why**: LLMs assign the highest attention weight to the beginning and end of a prompt. Middle content may be completely ignored.

**Applying to this project**:
- The "routing entry" section of RULES.md should come after the trigger keywords but before the execution principles
- The first section of every SKILL.md should be "Execute now" rather than "When to use"

---

## Technique 2: Directive Language Over Suggestive

Replace all "suggestive" language with RFC 2119-level directive language:

| Weak language (agent may skip) | Strong language (agent must execute) |
|---|---|
| "You can try..." | **MUST**: you must execute... |
| "Ready for next step → invoke X" | **NOW**: invoke X immediately, do not wait for confirmation |
| "It's suggested to read routing.md first" | **REQUIRED**: you must read routing.md fully before entering any submodule |
| "If tools are missing you can bootstrap" | **NO EXCUSE**: when tools are missing, the only correct action is calling bootstrap; manual install-by-guessing is forbidden |
| "Remember to update field-journal" | **CHECKLIST ENFORCED**: tick the Checklist item by item after the task; you may not claim task completion without it |
| "You should..." | **MUST** / **MUST NOT** |

**Key patterns**:
```
MUST — violation = task failure
MUST NOT — violation = security breach
SHOULD — not doing it requires explaining why
MAY — genuinely optional
```

---

## Technique 3: Excuse Rebuttal Table

**This is the most critical patch for this project.** When AI agents hit friction, they auto-generate "reasonable excuses" to skip steps. Pre-list common excuses and rebut each one:

| Common agent excuse | Rebuttal (enforced) |
|---|---|
| "This step can be omitted, I'll just..." | **Skipping is forbidden.** Every step in the behavior chain is required. If you think a step can be skipped, first output the specific reason and let the user decide. |
| "Based on my judgment, this isn't necessary" | **Your judgment does not apply here.** List the specific criteria you used, and explain why those criteria permit skipping an explicitly written step. |
| "The user probably doesn't need this" | **Never decide for the user.** Present all options to the user, mark your recommendation, but never hide alternatives. |
| "I already know how, no need to read X" | **Read X first, then act.** Even if you're sure you know how, X may contain constraints specific to this task. Reading takes 2 seconds. |
| "To save time, I can skip ahead in parallel..." | **The right way to save time is running independent steps in parallel, not skipping steps.** If two steps don't depend on each other, do them in parallel; if they depend, do them in order. |
| "I've used this tool before, I know the path" | **Guessing paths is forbidden.** You must get the actual path from tool-index; install locations differ between machines. |
| "The task is basically done, no need for the checklist" | **The only definition of task completion is every Checklist box ticked.** A task with an incomplete Checklist is not complete. |
| "I couldn't find tool-index, so I just guessed the path" | **A missing file is 100x safer than a wrong guessed path.** When tool-index is missing, first run refresh-tool-index.ps1 to generate it. |
| "The user didn't explicitly ask for a report, so I won't write one" | **Reporting is default behavior, not optional.** A security task must produce a report when done, unless the user explicitly says "no report". |
| "This was too simple to log in the journal" | **Simple tasks also have pitfall value.** At minimum record: target type + what you used + any surprises; one line is fine. |
| "The user asked me to redo the import table / a step, but I did something more useful instead" | **Redo = redo the exact step that was named.** When the user asks to redo X (e.g. import table check), you MUST re-execute X and update the corresponding Evidence; impersonating completion with other steps is forbidden, silently skipping X is forbidden. |


**How to use**: place this table near the end of RULES.md or other instruction files (high-attention zone). The agent sees the rebuttals before it can make excuses.

---

## Technique 4: Five Skill Engineering Patterns (Anthropic 2026 official)

| Pattern | Best for | Key tricks |
|---|---|---|
| **Linear Flow** | Well-defined step sequences (deploy, install) | Provide safe defaults, use negative directives ("MUST NOT use --force") |
| **Decision Tree** | Platform navigation, troubleshooting | Tree navigation + progressive loading from `references/` |
| **Iterative Loop** | TDD, review-fix loops | Hard rules up front + **excuse rebuttal table** to block shortcuts |
| **Baton Loop** | Multi-session, multi-agent collaboration | Externalize state to `next-prompt.md` (MUST write before exiting) |
| **Multi-Phase + Checkpoints** | Multi-day complex workflows | Orchestrator "parent" skill + human Go/No-Go checkpoints, annotate time cost |

**Mapping to this project**:
- Full behavior chain = Linear Flow (15 steps executed in order)
- Routing matrix = Decision Tree (three-dimension matching)
- Checklist = Multi-Phase Checkpoint (every step must be ticked)
- Field Journal = Baton Loop (cross-session state externalization)

---

## Technique 5: In-Band Forced Validation (Steering Hooks idea)

Don't rely on AI "conscientiousness"; embed self-validation instructions in the prompt:

```
Before claiming "task complete", you MUST self-check:
1. Did I skip any step in the behavior chain? Which one?
2. Did I guess any tool path? If so, what is the actual tool-index path?
3. Is every Checklist box ticked? If not, why?
4. If any answer above is "yes"/"not ticked", the task is NOT complete —
   go back to the corresponding step and re-execute; do not declare completion.
```

This makes the agent self-audit before saying "done", which is more immediate than external validation.

---

## Technique 6: Opaque Identifiers (Code Words) — for API/tool parameters

Microsoft 2026 research found that semantic parameter names trigger the model's "help optimize" tendency.

```
WRONG: { "query": "...", "top": 9 }        → 68.4% parameter adherence
CORRECT: { "query": "...", "code": "alpha" } → 100% parameter adherence
```

**When to use**:
- When precise config must be passed into bootstrap scripts, use short codes instead of semantic parameters
- For parameters in tool calls that need strong guarantees, use code-word mapping

---

## Technique 7: Dual AI Review Loop (Dual Validation)

```
AI A (executor) produces output
  ↓
AI B (reviewer) checks against rules
  ↓ pass
output to user
  ↓ fail
returned to AI A for fixes, with specific violation citations
```

**Application in this project**:
- Embed a "self-review" step in RULES.md: before outputting a report, the agent checks itself item by item against the Checklist using its own capability
- If it finds unfinished items, it goes back to the corresponding step and completes them

---

## Technique 8: Context Window Layout Optimization

LLM attention distribution (high → low):
```
[first 10%] ████████████ ← highest attention; put "act now" instructions
[middle 80%]  ████░░░░░░░░ ← decreasing attention; put reference material
[last 10%]  ████████████ ← attention rebounds; put "no skipping" and Checklist
```

**Concrete application**:
1. **First 10%**: execute-now instructions + trigger keywords
2. **Middle 80%**: detailed workflow, reference links, tool list
3. **Last 10%**: excuse rebuttal table + hard Checklist + forbidden-actions list

---

## Practical Prompt Templates

### Template A: Forced-Start Template (embed at the top of RULES.md)

```markdown
## CRITICAL: After reading this file you must immediately execute the following (don't just acknowledge, actually execute)

1. **NOW**: detect the directory containing this file → that is the pack root
2. **NOW**: if first use, write these rules into the global config (see Global Injection section)
3. **NEXT**: read `skills/SKILL.md` → `skills/routing.md` → decide which sub-skill to enter
4. **NEXT**: read `skills/tool-index.md` to confirm tool status
5. **THEN**: start the actual task; do not stay in "read" state

If you only reply "acknowledged", "done", "I understand" without actually executing the steps above,
you have failed. The user needs tools installed, code analyzed, vulnerabilities validated —
not a confirmation message.
```

### Template B: Submodule Entry Template (embed at the top of every SKILL.md)

```markdown
## ACTION REQUIRED (execute immediately after reading, don't wait)

After reading this file:
1. Confirm you understand this skill's applicable scenarios
2. Check whether this machine has the required tools (read `../tool-index.md`)
3. If tools are missing → call bootstrap
4. If tools exist → start workflow step 1
5. If unsure → list the specific questions; don't stay silent
```

### Template C: Task-Completion Self-Check Template (embed at the end of every SKILL.md)

```markdown
## Task Completion Self-Check (MUST confirm item by item before claiming completion)

□ I actually executed every step of the behavior chain (none skipped)
□ I guessed no tool paths (all from tool-index.md)
□ I produced reproducible commands/scripts/reports (not just described steps)
□ I updated field-journal (if pitfalls were hit)
□ I ran the completion Checklist (report + diagrams + lessons written back)
```

---

## Forbidden Behaviors (from an agent-obedience angle)

- Forbidden: after reading RULES.md, only replying "understood, please tell me the specific task"
  → Correct: run global injection → read SKILL.md → read routing.md → determine the entry point
- Forbidden: saying "steps 1-4 are done" when you only read them
  → Correct: distinguish "document read" from "operation executed"; the latter produces real side effects
- Forbidden: saying "task complete" without executing the Checklist
  → The Checklist is the only definition of task completion
- Forbidden: replacing reading tool-index with "based on experience"
  → Paths differ between machines; reading tool-index is the only reliable way

---

## Summary: If You Can Only Change One Thing

**Add an "act now" directive block at the very top of RULES.md**, using strong directive words like bold, CRITICAL, NOW.

This is the highest ROI change. Most agent "not working" behavior comes from auto-entering "wait for user instruction" mode after reading a file. A mandatory "act now" block breaks that pattern.

If you change a second thing: **add the excuse rebuttal table**. Agents find an excuse to stop at the first friction; block those excuses in advance.

