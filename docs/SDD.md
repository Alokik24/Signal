# Signal — System Design Document

## 1. Product

Signal is a local-first AI-assisted investigation workbench. A user states an analytical problem in text or, optionally, speech; Signal frames the problem, proposes hypotheses and an investigation plan, executes approved deterministic analyses, validates the resulting evidence, and produces an auditable finding and prescription.

The product is deliberately narrow. It is an investigation workbench, not an autonomous analyst or general assistant.

## 2. Problem

People can describe an operational or analytical concern without knowing the exact data queries, comparisons, statistical tests, or investigative sequence needed to examine it. Signal bridges that gap while keeping computation and evidence outside the LLM.

## 3. Goals

- Demonstrate modern AI application engineering in one coherent product.
- Convert ambiguous natural-language problems into structured investigations.
- Support deterministic analysis of local CSV/Parquet data.
- Allow an LLM to select among explicitly permitted analytical tools.
- Keep findings traceable to actual computations.
- Support human approval before consequential analysis steps.
- Evaluate framing, tool selection, numerical correctness, grounding, and prescription quality.
- Run locally without a paid API dependency.
- Provide a small React interface and one useful n8n integration without turning either into a separate product.

## 4. Non-goals

No generic chatbot, autonomous business-action system, BI platform, SaaS platform, browser agent, multi-agent framework, custom RAG framework, custom vector database, custom speech engine, Kubernetes deployment, Kafka/Celery infrastructure, or broad third-party integration suite.

A technology is not added solely to create a resume keyword.

## 5. Product flow

1. User supplies a problem in text or audio.
2. Audio is transcribed locally when the voice path is used.
3. LLM produces structured problem framing, hypotheses, unknowns, and data requirements.
4. Signal inspects the supplied dataset deterministically.
5. LLM proposes a bounded investigation plan.
6. Human approves or rejects the plan.
7. LangGraph orchestrates approved analysis tools.
8. Tools perform actual SQL, Python, statistical, and visualization work.
9. Results become provenance-bearing evidence objects.
10. Evidence validation checks whether findings are supported.
11. Signal produces findings, uncertainty, limitations, and a prescription.
12. A completion event may be sent to n8n for an external automation.

## 6. Architectural principle

**LLM reasons; tools calculate.**

The LLM may decide that a cancellation rate by platform is needed. A deterministic tool must calculate the rate. Numerical claims in a final finding must reference an analysis result.

The LLM cannot directly mutate datasets, execute arbitrary shell commands, issue arbitrary write SQL, or invent tool capabilities.

## 7. Architecture

React UI → FastAPI → LangGraph investigation workflow → controlled tool registry → DuckDB/Python/SciPy → evidence registry → evidence validation → final report.

PostgreSQL stores application and investigation metadata. pgvector is conditional and is introduced only if historical investigation retrieval demonstrates product value.

Faster-Whisper is an optional input adapter. n8n is an external automation adapter triggered by a Signal webhook.

## 8. Components

### React

Small UI for investigation input, dataset upload, workflow state, evidence inspection, and final report. No frontend framework stack beyond what the product requires.

### FastAPI

HTTP boundary and orchestration API. Business logic remains independent of HTTP concerns.

### LangGraph

Stateful workflow orchestration, checkpointing, bounded routing, and human approval. Signal does not implement its own agent loop or checkpointing system.

### LLM provider

A provider abstraction isolates model-specific APIs. Local inference is the default development target. A paid/external model is optional.

### DuckDB

Local analytical SQL engine for CSV/Parquet data. It is preferred over building a warehouse ingestion layer for the MVP.

### Python/Pandas/SciPy

Deterministic data transformations and approved statistical operations.

### PostgreSQL

Application state, investigations, analysis metadata, evidence, findings, and prescriptions.

### pgvector

Conditional historical retrieval. No separate vector database.

### Faster-Whisper

Local speech-to-text adapter. Diarization is explicitly deferred.

### OpenTelemetry

Tracing and metrics for investigation steps, tools, and model calls. No custom observability platform.

### n8n

One external workflow integration through a completion webhook. n8n is not part of Signal's core reasoning engine.

## 9. Investigation state

Initial state fields:

- question
- transcript (optional)
- hypotheses
- data_requirements
- dataset_context
- investigation_plan
- approved_plan
- analysis_results
- evidence
- findings
- prescription
- status

State should remain minimal. Large datasets and redundant derived data must not be placed into workflow state.

## 10. Workflow

START → input/transcription → problem framing → hypotheses/data requirements → dataset inspection → investigation plan → human approval → bounded tool selection/execution → evidence sufficiency check → evidence validation → findings → prescription → END.

The investigation loop has a hard iteration limit. Failure or insufficient evidence must terminate safely rather than encourage uncontrolled agent loops.

## 11. Tool boundary

Initial approved tools:

- `inspect_dataset`
- `run_sql`
- `run_python_analysis`
- `run_statistical_test`
- `create_visualization`

Tools must have explicit input/output contracts. SQL is read-only. Python analysis is controlled rather than arbitrary shell execution. The model can select only registered tools.

## 12. Evidence and provenance

An analysis run produces a stable analysis identifier. Evidence references its source dataset and analysis run. A finding references one or more evidence objects. A prescription references the findings/evidence supporting it.

A final answer must be able to answer: **where did this claim come from?**

If available evidence is insufficient, Signal must say so rather than manufacture certainty.

## 13. Human-in-the-loop

Human approval occurs after investigation planning and before analysis execution. The user can approve, reject, or edit the proposed plan. LangGraph's existing interrupt/checkpoint facilities are used; no custom approval framework is built.

## 14. RAG policy

RAG is not part of the minimum analytical path. It may be added only after completed investigations exist and retrieval of prior investigations has a demonstrated use case. If added, PostgreSQL + pgvector is the default rather than a separate vector database. Historical context may inform an investigation but cannot override current empirical evidence.

## 15. Speech policy

Speech is an optional input adapter. Faster-Whisper is used rather than implementing speech recognition. The transcript enters the same problem-framing pipeline as typed text. Speaker diarization is out of scope unless a real requirement appears.

## 16. Automation policy

Signal emits one completion webhook. n8n may consume it for a useful external action such as notification or persistence. Scheduling, branching, retries, and third-party integrations belong to n8n rather than being reimplemented inside Signal.

## 17. Cost requirements

The normal local development and runtime path should require zero recurring spend. Paid model providers are optional and must be replaceable through the provider abstraction. Hosted databases, hosted vector stores, hosted observability, and n8n Cloud are not MVP dependencies.

## 18. Reproducibility

Primary development is Linux-first. Runtime dependencies should be containerized where practical. Windows + Docker Desktop is a secondary validation target. Setup documentation must distinguish required, optional, and OS-specific dependencies.

## 19. Security boundaries

The LLM has no arbitrary shell access. Analytical SQL is read-only. Tool execution is allow-listed. Uploaded data is untrusted input. Secrets are supplied through configuration and are never committed. Prompt-injection scenarios are included in evaluation.

## 20. Evaluation

A small manually verified benchmark will test:

- problem framing
- hypothesis quality
- tool selection
- numerical correctness
- evidence grounding
- prescription quality
- failure/insufficient-evidence behavior

Evaluation must test the system's actual outputs, not just whether a workflow completed.

## 21. Observability

OpenTelemetry traces the investigation lifecycle and important tool/model calls. At minimum, record latency, failures, tool usage, and model usage where available.

## 22. Build-vs-integrate rule

Before implementing a substantial capability, check whether a mature existing library or service already provides it. Prefer integration unless the dependency is unsuitable or implementing the capability is an explicit learning objective. No custom replacement should be created merely for portfolio value.

The capability register is the first reference for these decisions; implementation tickets must not silently override it.

## 23. Deferred features

The following require an explicit architecture review before implementation:

- RAG/pgvector if not yet justified
- Redis
- background job queues
- external web browsing
- MCP
- additional agent frameworks
- multi-agent orchestration
- cloud deployment
- authentication/multi-user features
- additional automation integrations
- diarization

## 24. Acceptance criteria

Signal is complete when a fresh local setup can accept a natural-language investigation problem and a CSV/Parquet dataset, frame the problem, propose a plan, pause for approval, execute deterministic analysis through bounded tools, produce evidence-backed findings with uncertainty and limitations, and render the result through the React interface. The system must also expose a useful completion webhook and pass the evaluation suite.

The project stops when these capabilities work. Additional technologies are not grounds for extension.
