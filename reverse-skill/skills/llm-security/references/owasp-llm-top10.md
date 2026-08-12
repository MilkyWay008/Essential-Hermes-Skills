# OWASP LLM & Agentic AI Top 10 (2025-2026)

## OWASP Top 10 for LLM Applications v2.0 (2025)

| # | Risk | Core issue | Test direction |
|---|------|---------|---------|
| LLM01 | Prompt Injection | Manipulating model behavior through crafted input | Direct injection, indirect injection, encoding bypasses |
| LLM02 | Sensitive Information Disclosure | PII/API Key/training data leakage | Prompt extraction, output analysis |
| LLM03 | Supply Chain | Poisoned models/libraries/datasets | Model source verification, dependency scanning |
| LLM04 | Data & Model Poisoning | Backdoors in training/fine-tuning data | Data provenance, behavior anomaly detection |
| LLM05 | Improper Output Handling | Output causing XSS/SQLi/RCE | Downstream system injection testing |
| LLM06 | Excessive Agency | Too much tool/autonomy causing real harm | Permission audits, human-in-the-loop testing |
| LLM07 | System Prompt Leakage | Extracting hidden instructions/secrets/business logic | Cascade extraction, canary tokens |
| LLM08 | Vector & Embedding Weaknesses | RAG pipeline attacks, embedding inversion | Retrieval poisoning, semantic similarity attacks |
| LLM09 | Misinformation | Hallucinations as a security risk in high-stakes scenarios | Factual verification, confidence calibration |
| LLM10 | Unbounded Consumption | DoS/Denial-of-Wallet | Token consumption testing, rate limiting |

## OWASP Top 10 for Agentic Applications (ASI 2026)

| # | Risk | Core harm | Test direction |
|---|------|---------|---------|
| ASI01 | Agent Goal Hijack | Malicious input/tool output hijacks the goal | Instruction override, goal tampering |
| ASI02 | Tool Misuse & Exploitation | Unexpected use of legitimate tools | Tool chain assembly, parameter injection |
| ASI03 | Identity & Privilege Abuse | Agent operating beyond its privileges | Credential theft, delegation chain testing |
| ASI04 | Agentic Supply Chain | Real-time risk from MCP descriptors/third-party tools | Dynamic supply chain scanning |
| ASI05 | Unexpected Code Execution | Prompt→tool→script RCE chains | Multi-layer code execution testing |
| ASI06 | Memory & Context Poisoning | Long-term memory/embedding poisoning | Memory persistence attacks |
| ASI07 | Insecure Inter-Agent Communication | Tampering with inter-agent communication | Man-in-the-middle, replay attacks |
| ASI08 | Cascading Failures | Single point of failure triggering system-wide collapse | Failure propagation testing |
| ASI09 | Human-Agent Trust Exploitation | Manipulating human operators into approving dangerous actions | Authority bias/urgency testing |
| ASI10 | Rogue Agents | Agent self-replication/persistent malicious behavior | Persistence backdoor detection |

## Real-World Data Distribution

Issue share in real evaluations:
- LLM01 Prompt Injection: ~45%
- LLM06 Sensitive Info Disclosure: ~20%
- LLM08 Excessive Agency: ~15%
- Remaining 7 items: ~20%

## Key Defense Principles

1. Separate planning from execution — the model that interprets intent ≠ the model that executes actions
2. Bind identity/purpose/scope/expiry — don't use broad ambient permissions
3. Log everything — tool calls/memory/communication as first-class security telemetry
4. Blast radius control — circuit breakers/rollback/emergency stop over convenience
5. Treat all natural-language input (including retrieved content) as untrusted
6. Output is equally untrusted — sanitize before rendering/executing/querying

