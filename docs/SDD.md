# Signal — System Design Document

## 1. Product
Signal is a local-first AI-assisted investigation workbench. A user states an analytical problem in text or, optionally, speech; Signal frames the problem, proposes hypotheses and an investigation plan, executes approved deterministic analyses, validates the resulting evidence, and produces an auditable finding and prescription. The product is deliberately narrow: an investigation workbench, not an autonomous analyst or general assistant.

## 2. Problem
People can describe an operational or analytical concern without knowing the exact queries, comparisons, statistical tests, or investigative sequence needed to examine it. Signal bridges that gap while keeping computation and evidence outside the LLM.

## 3. Goals
- Demonstrate modern AI application engineering in one coherent product.
- Convert ambiguous natural-language problems into structured investigations.
- Analyze local CSV/Parquet data deterministically.
- Let an LLM select among explicitly permitted tools.
- Keep findings traceable to actual computations.
- Support human approval before analysis execution.
- Evaluate framing, tool selection, numerical correctness, grounding, and prescription quality.
- Run locally without a paid API dependency.
- Provide a small React interface and one useful automation integration.

## 4. Non-goals
No generic chatbot, autonomous business-action system, BI platform, SaaS platform, browser agent, multi-agent framework, custom RAG framework, custom vector database, custom speech engine, Kubernetes deployment, Kafka/Celery infrastructure, or broad third-party integration suite. A technology is not added solely to create a resume keyword.

## 5. Product flow
1. User supplies a problem in text or audio.
2. Audio is transcribed locally when the voice path is used.
3. The LLM produces structured problem framing, hypotheses, unknowns, and data requirements.
4. Signal inspects supplied data deterministically.
5. The LLM proposes a bounded investigation plan.
6. The human approves, rejects, or edits the plan.
7. LangGraph orchestrates approved analysis tools.
8. Tools perform actual SQL, Python, statistical, and visualization work.
9. Results become provenance-bearing evidence objects.
10. Evidence validation checks whether findings are supported.
11. Signal produces findings, uncertainty, limitations, and a prescription.
12. A completion event may be sent to n8n for an external automation.

## 6. Architectural principle
**LLM reasons; tools calculate.** The LLM may decide that cancellation rate by platform is needed. A deterministic tool calculates the rate. Numerical claims in a final finding must reference an analysis result. The LLM cannot directly mutate datasets, execute arbitrary shell commands, issue arbitrary write SQL, or invent tool capabilities.

## 7. Architecture
React UI → FastAPI → LangGraph investigation workflow → controlled tool registry → DuckDB/Python/SciPy → evidence registry → evidence validation → final report. PostgreSQL stores application and investigation metadata. pgvector is conditional and is introduced only if historical retrieval demonstrates product value. Faster-Whisper is an optional input adapter. n8n is an external automation adapter triggered by a Signal webhook.

## 8. Components
- **React:** small UI for investigation input, dataset upload, workflow state, evidence inspection, and final report.
- **FastAPI:** HTTP boundary and orchestration API; business logic remains independent of HTTP concerns.
- **LangGraph:** stateful workflow orchestration, routing, checkpointing, and human interruption; no custom agent loop.
- **LLM provider:** narrow provider abstraction; local inference first, external providers optional.
- **DuckDB:** local analytical SQL engine for CSV/Parquet.
- **Python/Pandas/SciPy:** deterministic data transformations and approved statistical operations.
- **PostgreSQL:** application state, investigations, analysis metadata, evidence, findings, and prescriptions.
- **pgvector:** conditional historical retrieval; no separate vector database.
- **Faster-Whisper:** local speech-to-text; diarization deferred.
- **OpenTelemetry:** tracing and metrics for investigation steps, tools, and model calls.
- **n8n:** one external workflow integration through a completion webhook.

## 9. Investigation state
Initial fields: question, transcript (optional), hypotheses, data_requirements, dataset_context, investigation_plan, approved_plan, analysis_results, evidence, findings, prescription, status. State remains minimal; large datasets and redundant derived data do not enter workflow state.

## 10. Workflow and agent model
START → input/transcription → problem framing → hypotheses/data requirements → dataset inspection → investigation plan → human approval → bounded tool selection/execution → evidence sufficiency check → evidence validation → findings → prescription → END.

Agentic behavior means the model can choose among registered tools and route through permitted workflow states. It does not mean unrestricted autonomy. There is a hard iteration limit; failure or insufficient evidence terminates safely.

## 11. Structured outputs
LLM-facing contracts use typed schemas. Problem framing, hypotheses, data requirements, plans, tool calls, findings, and prescriptions must conform to explicit schemas before entering the next workflow state. Malformed or incomplete model output is rejected/retried within bounded limits.

## 12. Tool boundary
Initial tools: `inspect_dataset`, `run_sql`, `run_python_analysis`, `run_statistical_test`, `create_visualization`. Tools have explicit input/output contracts. SQL is read-only. Python analysis is controlled rather than arbitrary shell execution. The model can select only registered tools.

## 13. Evidence and provenance
An analysis run produces a stable analysis identifier. Evidence references its source dataset and analysis run. A finding references one or more evidence objects. A prescription references the findings/evidence supporting it. A final answer must be able to answer: **where did this claim come from?** If evidence is insufficient, Signal says so rather than manufacturing certainty.

## 14. Human-in-the-loop
Human approval occurs after investigation planning and before analysis execution. The user can approve, reject, or edit the proposed plan. LangGraph interrupt/checkpoint facilities are used; no custom approval framework is built.

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
The LLM has no arbitrary shell access. Analytical SQL is read-only. Tool execution is allow-listed. Uploaded data is untrusted input. Secrets are supplied through configuration and are never committed. Prompt-injection scenarios are included in evaluation.

## 22. Evaluation
A small manually verified benchmark tests problem framing, hypothesis quality, structured-output validity, tool selection, numerical correctness, evidence grounding, prescription quality, and failure/insufficient-evidence behavior. Evaluation tests actual outputs, not merely workflow completion.

## 23. Observability
OpenTelemetry traces the investigation lifecycle and important tool/model calls. At minimum, record latency, failures, tool usage, and model usage where available.

## 24. Build-vs-integrate rule
Before implementing a substantial capability, check whether a mature existing library or service already provides it. Prefer integration unless the dependency is unsuitable or implementation is an explicit learning objective. No custom replacement is created merely for portfolio value. The capability register is the first reference for these decisions.

## 25. Deferred features
These require explicit architecture review: RAG/pgvector if not yet justified; Redis; background job queues; external web browsing; MCP; additional agent frameworks; multi-agent orchestration; cloud deployment; authentication/multi-user features; additional automation integrations; diarization.

## 26. Failure and recovery policy
Every model/tool boundary has a defined failure path. Invalid structured output, unavailable models, failed analysis, empty datasets, unsupported files, insufficient evidence, and interrupted workflows produce explicit states rather than silent fallback. Agent loops are bounded. Retrying a failed model call is allowed only for transient failures or malformed output contracts.

## 27. Completion and acceptance criteria
A fresh local setup can accept a natural-language investigation problem and CSV/Parquet dataset, frame the problem, propose a plan, pause for approval, execute deterministic analysis through bounded tools, produce evidence-backed findings with uncertainty and limitations, and render the result through React. The system must also expose a useful completion webhook, support the optional voice path, and pass the evaluation suite.

## 28. Scope gate
The project stops when the acceptance criteria work. New capabilities require a written product requirement, a build-vs-integrate check, and an explicit decision that the capability is worth its implementation and maintenance cost.

**Stinginess rule:** if the current architecture can perform the required work without a new dependency, service, abstraction, or subsystem, do not add one. If stinginess prevents a required capability from working reliably, revisit the constraint with evidence rather than adding technology pre-emptively.
