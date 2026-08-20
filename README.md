# Signal

**Signal** is a local-first AI-assisted investigation workbench: it turns an ambiguous human problem into a structured, auditable investigation and an evidence-backed recommendation.

## Phase 0 status

SIG-000 through SIG-003 are frozen in the Phase 0 baseline. The full system design is in `docs/SDD.md`; `docs/CAPABILITY-REGISTER.md` maps every AI capability Signal deliberately covers, defers, limits, or excludes.

## Core boundary

The probabilistic layer (LLM) interprets, plans, routes and explains. Deterministic tools calculate, query, test and record evidence. The LLM must not manufacture analytical results.

## MVP path

Human problem → problem framing → hypotheses → data requirements → dataset inspection → investigation plan → human approval → bounded tool use → evidence validation → findings → prescription.

Text is the primary input. Audio is optional through Faster-Whisper. RAG, embeddings, vector search and n8n are conditional/limited capabilities governed by the capability register rather than added for keywords.

## Cost target

Development and normal local use should require no paid API or hosted service. Local inference is preferred; external model providers are optional adapters.

## Development model

Linux-first development with Docker-based reproducibility. Windows + Docker Desktop is a secondary validation target. See `SETUP.md` for environment instructions as implementation progresses.
