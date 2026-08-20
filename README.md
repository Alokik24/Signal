# Signal

**Signal** is a local-first AI-assisted investigation workbench: it turns an ambiguous human problem into a structured, auditable investigation and an evidence-backed recommendation.

## Phase 0 status

Architecture and scope are frozen in `docs/SDD.md`. The capability register in `docs/CAPABILITY-REGISTER.md` is the authority for build-vs-integrate decisions.

## Core boundary

The probabilistic layer (LLM) interprets, plans, routes and explains. Deterministic tools calculate, query, test and record evidence. The LLM must not manufacture analytical results.

## MVP path

Human problem → problem framing → hypotheses → data requirements → dataset inspection → investigation plan → human approval → bounded tool use → evidence validation → findings → prescription.

Text is the primary input. Audio is an optional input path through Faster-Whisper. Historical retrieval, pgvector, and n8n automation are conditional capabilities and are not allowed to expand the core product without a demonstrated requirement.

## Cost target

Development and normal local use should require no paid API or hosted service. Local inference is preferred; external model providers are optional adapters.

## Development model

Linux-first development with Docker-based reproducibility. Windows + Docker Desktop is a secondary validation target. See `SETUP.md` for environment instructions as implementation progresses.
