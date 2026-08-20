# Capability Register

This register is the Phase 0 guardrail against rebuilding mature capabilities or adding technology without a product requirement.

| Capability | Decision | Rationale / boundary |
|---|---|---|
| HTTP API | FastAPI | Existing, mature Python API framework; no custom HTTP layer. |
| Data validation | Pydantic | Use typed contracts rather than hand-written validation. |
| Workflow orchestration | LangGraph | Use its state, routing, persistence/checkpointing, and human-interruption facilities. |
| LLM inference | Local provider first | Avoid mandatory recurring API cost. Provider abstraction permits optional external models. |
| Speech-to-text | Faster-Whisper | Use an existing local Whisper implementation; no speech engine work. |
| Analytical SQL | DuckDB | Direct local analysis of CSV/Parquet; avoids premature warehouse infrastructure. |
| Dataframes | Pandas | Existing project skill and mature ecosystem. |
| Statistical tests | SciPy | Do not implement statistical tests manually. |
| Visualizations | Matplotlib | Deterministic plotting; no custom charting engine. |
| Application database | PostgreSQL | Existing skill and sufficient for application/investigation state. |
| Vector search | pgvector, conditional | Add only when historical retrieval has a real use case; no separate vector DB. |
| Embeddings | Existing local embedding model/provider | No custom embedding model. Only add retrieval when justified. |
| Observability | OpenTelemetry | Standard instrumentation; no custom tracing platform. |
| Frontend | React | Needed to demonstrate an actual interactive AI workflow and close the frontend gap. Keep UI deliberately small. |
| Automation | n8n | Use for one external event-driven workflow; do not reimplement an automation engine. |
| Containerization | Docker / Compose | Reproducible local runtime. |
| CI | GitHub Actions | Existing ecosystem and sufficient for project CI. |

## Build policy

A capability marked **Use** must be integrated rather than reimplemented unless a later ticket documents a concrete incompatibility or an explicit learning objective.

A capability marked **Conditional** requires a product justification before implementation. The existence of an ATS keyword is not a sufficient justification.

## Deliberately excluded

No custom agent framework, custom RAG framework, custom vector database, custom speech recognition, multi-agent framework, Kafka, Kubernetes, Celery, or broad third-party integration layer in the MVP.

## Cost policy

The default development path must not require paid APIs or hosted services. External providers are optional adapters for comparison or later deployment, not architectural dependencies.
