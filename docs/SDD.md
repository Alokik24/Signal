# Signal — System Design Document

## 1. Product
Signal is a local-first AI-assisted investigation workbench. A user states an analytical problem in text or, optionally, speech; Signal frames the problem, assesses supplied data, proposes only the transformations needed for the investigation, executes approved deterministic analyses, validates the resulting evidence, and produces an auditable finding and prescription. The product is deliberately narrow: an investigation workbench, not an autonomous analyst or general data-cleaning platform.

## 2. Problem
People can describe an operational or analytical concern without knowing the exact queries, comparisons, statistical tests, investigative sequence, or data preparation needed to examine it. Signal bridges that gap while keeping computation and evidence outside the LLM.

## 3. Goals
- Demonstrate modern AI application engineering in one coherent product.
- Convert ambiguous natural-language problems into structured investigations.
- Accept reasonably raw CSV/Parquet data and determine whether it is usable for the current question.
- Detect material data-quality issues and propose only investigation-relevant transformations.
- Keep source data immutable during analysis.
- Let an LLM select among explicitly permitted tools.
- Keep findings traceable to actual computations.
- Support human approval before material analysis/transformation execution.
- Evaluate framing, tool selection, numerical correctness, grounding, and prescription quality.
- Run locally without a paid API dependency.
- Provide a small React interface and one useful automation integration.

## 4. Non-goals
No generic chatbot, autonomous business-action system, BI platform, general-purpose ETL/data-cleaning platform, SaaS platform, browser agent, multi-agent framework, custom RAG framework, custom vector database, custom speech engine, Kubernetes deployment, Kafka/Celery infrastructure, or broad third-party integration suite. A technology is not added solely to create a resume keyword.

## 5. Product flow
1. User supplies a problem in text or audio.
2. Audio is transcribed locally when the voice path is used.
3. The LLM produces structured problem framing, hypotheses, unknowns, and data requirements.
4. Signal profiles supplied data deterministically.
5. Signal assesses data quality against the current investigation.
6. Signal classifies the data as usable, usable with warnings/approval, or insufficient.
7. Where needed, Signal proposes investigation-specific transformations; ambiguous/material transformations require human approval.
8. Signal creates a temporary analytical representation without modifying the source data.
9. The LLM proposes a bounded investigation plan using the available data and approved transformations.
10. The human approves, rejects, or edits the plan.
11. LangGraph orchestrates approved analysis tools.
12. Tools perform actual SQL, Python, statistical, and visualization work.
13. Results become provenance-bearing evidence objects.
14. Evidence validation checks whether findings are supported.
15. Signal produces findings, uncertainty, limitations, and a prescription.
16. A completion event may be sent to n8n for an external automation.

## 6. Architectural principle
**LLM reasons; deterministic systems inspect, transform, and calculate.** The LLM may identify a data-quality issue or request a transformation, but the transformation is represented explicitly and executed by deterministic code after the required approval. Numerical claims in a final finding must reference an analysis result. The LLM cannot directly mutate source datasets, execute arbitrary shell commands, issue arbitrary write SQL, or invent tool capabilities.

## 7. Architecture
React UI → FastAPI → LangGraph investigation workflow → data profiling/quality layer → controlled transformation layer → DuckDB/Python/SciPy → evidence registry → evidence validation → final report. PostgreSQL stores application and investigation metadata. pgvector is conditional and is introduced only if historical retrieval demonstrates product value. Faster-Whisper is an optional input adapter. n8n is an external automation adapter triggered by a Signal webhook.

## 8. Components
- **React:** small UI for investigation input, dataset upload, data-quality findings/approval, workflow state, evidence inspection, and final report.
- **FastAPI:** HTTP boundary and orchestration API; business logic remains independent of HTTP concerns.
- **LangGraph:** stateful workflow orchestration, routing, checkpointing, and human interruption; no custom agent loop.
- **LLM provider:** narrow provider abstraction; local inference first, external providers optional.
- **Data profiler/quality layer:** deterministic schema, type, missingness, duplicate, category, date, and validity checks relevant to the investigation.
- **Transformation layer:** small allow-listed transformations for the current investigation; produces derived analytical views and never overwrites source data.
- **DuckDB:** local analytical SQL engine for CSV/Parquet and derived analytical views.
- **Python/Pandas/SciPy:** deterministic data transformations and approved statistical operations.
- **PostgreSQL:** application state, investigations, data-quality findings, transformation decisions, analysis metadata, evidence, findings, and prescriptions.
- **pgvector:** conditional historical retrieval; no separate vector database.
- **Faster-Whisper:** local speech-to-text; diarization deferred.
- **OpenTelemetry:** tracing and metrics for investigation steps, tools, and model calls.
- **n8n:** one external workflow integration through a completion webhook.

## 9. Investigation state
Initial fields: question, transcript (optional), hypotheses, data_requirements, dataset_context, data_quality_findings, data_readiness, proposed_transformations, approved_transformations, analytical_view, investigation_plan, approved_plan, analysis_results, evidence, findings, prescription, status. State remains minimal; large datasets and redundant derived data do not enter workflow state.

## 10. Workflow and agent model
START → input/transcription → problem framing → hypotheses/data requirements → dataset profiling → investigation-specific quality assessment → readiness decision → transformation proposal/approval when required → analytical view → investigation plan → human approval → bounded tool selection/execution → evidence sufficiency check → evidence validation → findings → prescription → END.

Agentic behavior means the model can choose among registered tools and route through permitted workflow states. It does not mean unrestricted autonomy. There is a hard iteration limit; failure or insufficient evidence terminates safely.

## 11. Structured outputs
LLM-facing contracts use typed schemas. Problem framing, hypotheses, data requirements, quality interpretations, transformation proposals, plans, tool calls, findings, and prescriptions must conform to explicit schemas before entering the next workflow state. Malformed or incomplete model output is rejected/retried within bounded limits.

## 12. Tool boundary
Initial tools: `profile_dataset`, `assess_data_quality`, `propose_transformation`, `apply_approved_transformations`, `inspect_dataset`, `run_sql`, `run_python_analysis`, `run_statistical_test`, `create_visualization`. Tools have explicit input/output contracts. SQL is read-only with respect to source/application data; analytical SELECT queries may perform temporary query-time transformations. Transformation tools operate only on derived analytical representations. Python analysis is controlled rather than arbitrary shell execution. The model can select only registered tools.

## 13. Evidence and provenance
An analysis run produces a stable analysis identifier. Evidence references its source dataset, analytical view/transformation set where applicable, and analysis run. A finding references one or more evidence objects. A prescription references the findings/evidence supporting it. A final answer must be able to answer: **where did this claim come from, and what transformations were applied?** If evidence is insufficient, Signal says so rather than manufacturing certainty.

## 14. Human-in-the-loop
Human approval occurs before material/ambiguous data transformations and before investigation execution. Safe, deterministic, non-destructive profiling may run automatically. The user can approve, reject, or edit proposed transformations and investigation plans. LangGraph interrupt/checkpoint facilities are used; no custom approval framework is built.

## 15. RAG policy
RAG is not part of the minimum analytical path. It may be added only after completed investigations exist and retrieval of prior investigations has a demonstrated use case. Historical context may inform an investigation but cannot override current empirical evidence.

## 16. Embeddings and vector search
Embeddings are an implementation detail of historical retrieval, not a standalone feature. If retrieval is justified, use an existing local embedding model/provider and PostgreSQL + pgvector. Do not train an embedding model or introduce a separate vector database. Signal must remain fully useful when historical retrieval is disabled.

## 17. Speech-to-text
Speech is an optional input adapter. Faster-Whisper is used rather than implementing speech recognition. The transcript enters the same problem-framing pipeline as typed text. Speaker diarization is out of scope unless a real requirement appears.

## 18. Automation
Signal emits one completion webhook. n8n may consume it for a useful external action such as notification or persistence. Scheduling, branching, retries, and third-party integrations belong to n8n rather than being reimplemented inside Signal.

## 19. Cost requirements
The normal local development and runtime path should require zero recurring spend. Paid model providers are optional and replaceable through the provider abstraction. Hosted databases, hosted vector stores, hosted observability, and n8n Cloud are not MVP dependencies.

## 20. Reproducibility and setup
Primary development is Linux-first. Runtime dependencies should be containerized where practical. Windows + Docker Desktop is a secondary validation target. Setup documentation must distinguish required, optional, and OS-specific dependencies. A fresh clone must eventually be runnable from the documented setup without machine-specific configuration.

## 21. Security boundaries
The LLM has no arbitrary shell access. Analytical SQL is read-only against source/application data. Transformation execution is allow-listed and operates on derived representations. Uploaded data is untrusted input. Secrets are supplied through configuration and are never committed. Prompt-injection and malicious-transformation scenarios are included in evaluation.

## 22. Evaluation
A small manually verified benchmark tests problem framing, hypothesis quality, structured-output validity, data-readiness classification, transformation proposal quality, tool selection, numerical correctness, evidence grounding, prescription quality, and failure/insufficient-evidence behavior. Evaluation tests actual outputs, not merely workflow completion.

## 23. Observability
OpenTelemetry traces the investigation lifecycle and important tool/model calls. At minimum, record latency, failures, tool usage, model usage where available, data-quality decisions, transformation decisions, and analysis provenance.

## 24. Build-vs-integrate rule
Before implementing a substantial capability, check whether a mature library or service already provides it. Prefer integration unless the dependency is unsuitable or implementation is an explicit learning objective. No custom replacement is created merely for portfolio value. The capability register is the first reference for these decisions.

## 25. Deferred features
These require explicit architecture review: RAG/pgvector if not yet justified; Redis; background job queues; external web browsing; MCP; additional agent frameworks; multi-agent orchestration; cloud deployment; authentication/multi-user features; additional automation integrations; diarization; broad automated data-cleaning rules outside the current investigation.

## 26. Failure and recovery policy
Every model/tool boundary has a defined failure path. Invalid structured output, unavailable models, failed profiling, unsupported files, unresolvable data-quality issues, failed transformations, empty datasets, insufficient evidence, and interrupted workflows produce explicit states rather than silent fallback. Source data remains recoverable and unchanged. Agent loops are bounded. Retrying a failed model call is allowed only for transient failures or malformed output contracts.

## 27. Completion and acceptance criteria
A fresh local setup can accept a natural-language investigation problem and reasonably raw CSV/Parquet data, profile and assess the data for that investigation, propose and obtain approval for any material required transformations, create a temporary analytical representation without changing the source, execute deterministic analysis through bounded tools, produce evidence-backed findings with uncertainty and limitations, and render the result through React. The system must also expose a useful completion webhook, support the optional voice path, and pass the evaluation suite.

## 28. Scope gate
The project stops when the acceptance criteria work. New capabilities require a written product requirement, a build-vs-integrate check, and an explicit decision that the capability is worth its implementation and maintenance cost.

**Stinginess rule:** if the current architecture can perform the required work without a new dependency, service, abstraction, or subsystem, do not add one. If stinginess prevents a required capability from working reliably, revisit the constraint with evidence rather than adding technology pre-emptively. Signal cleans/transforms **only what the current investigation needs**; it does not promise to clean every aspect of an uploaded dataset.
