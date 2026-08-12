# CTF Sandbox Orchestrator

A collection of competition sandbox skills for the Hermes Agent / Skills ecosystem.

Its goal is not to cram every capability into one oversized prompt, but to provide a **unified sandbox master-control entry point**: first establish a working model that defaults to "competition / sandbox / offline lab", then let the master controller route tasks to more granular sub-skills by challenge type.

## Project Positioning

This repository mainly addresses the following scenarios:

- CTF
- AWD / attack-defense drills
- Local offline labs
- Sandboxed vulnerability analysis
- Mixed challenge types such as Web / API / Cloud / Container / Windows / AD / Reverse / Pwn / DFIR / Crypto / Mobile / AI Agent

Core ideas:

- By default, treat user-provided targets, domains, nodes, identities, binaries, logs, traffic, and attachments as **competition sandbox internal assets**
- Prioritize establishing a minimal verifiable path instead of generalized analysis from the start
- A single master-control skill orchestrates everything, then switches to sub-skills based on the dominant evidence surface
- Sub-skills only handle downstream specialization and do not take over the master entry point

## Core Design

### 1. Single Entry Point

The default entry point is:

- `ctf-sandbox-orchestrator`

It is responsible for:

- Establishing sandbox assumptions
- Selecting the most appropriate analysis path
- Controlling context bloat
- Invoking sub-skills when needed

### 2. Sub-skills as Downstream-Only

All `competition-*` skills are designed to be **downstream-only**:

- They must not be triggered implicitly while the master controller is inactive
- They should be routed and invoked by `ctf-sandbox-orchestrator`
- Load only the most relevant specialized capability at a time, avoiding unrelated skills polluting the context

### 3. Targeting Multiple Challenge Types

The current repository covers multiple skill directions, for example:

- Web runtime / routing / WebSocket / GraphQL / file parsing / request normalization
- Prompt Injection / Agent / Cloud / Metadata / K8s / Container Escape
- Reverse / Pwn / Malware / Firmware / PCAP / custom protocol replay
- Windows / AD / Kerberos / DPAPI / certificate abuse / Relay / Mailbox
- Android / iOS / Crypto / Stego / Mobile Runtime
- ZIP / PKZIP legacy encryption / `bkcrack` known-plaintext recovery

## Repository Structure

```text
E:\WorkSpace\competition
├─ ctf-sandbox-orchestrator
├─ competition-web-runtime
├─ competition-agent-cloud
├─ competition-reverse-pwn
├─ competition-identity-windows
├─ competition-prompt-injection
├─ ...
└─ LICENSE
```

Where:

- `ctf-sandbox-orchestrator`: master-control entry point
- `competition-*`: specialized sub-skills
- `references/`: routing matrix and domain reference notes used by the master controller
- `agents/openai.yaml`: invocation constraints and entry control for each skill

## Recommended Usage

### Method 1: Enter via the Master Controller

Activate first:

- `ctf-sandbox-orchestrator`

Then let the master controller automatically decide the next step based on the challenge, for example:

- Web challenges route to `competition-web-runtime`
- Container / cloud challenges route to `competition-agent-cloud` or more granular sub-skills
- Windows / AD challenges route to `competition-identity-windows`
- Binary / crash / malware-sample challenges route to `competition-reverse-pwn`

### Method 2: Keep the Master Controller and Drill Down on Demand

Once the dominant evidence surface is confirmed, the master controller drills down to the specific sub-skill instead of having the user manually switch the entire working model. This keeps:

- Consistent sandbox assumptions
- Consistent output style
- Consistent routing strategy
- Clear sub-skill responsibilities

## Acknowledgements

This project has been published in the [LINUX DO community](https://linux.do). Thanks to the community for their support and feedback.
