# Capability Register

This register is the Phase 0 authority for what Signal demonstrates, how each capability is implemented, and when it is deliberately excluded. The default decision is to integrate mature capabilities rather than rebuild them.

## AI capability map

| AI capability | Signal coverage | Implementation boundary | Decision |
|---|---|---|---|
| LLM inference | Problem framing, hypotheses, planning, interpretation, prescription | Provider abstraction; local model first; external APIs optional | **Use** |
| Prompting | Structured prompts for each workflow state | Keep prompts small, versioned, and tied to schemas | **Use** |
| Structured outputs | Typed framing, plans, tool calls, findings | Pydantic/schema validation at every LLM boundary | **Use** |
| Tool calling | Model selects registered analytical tools | Allow-listed tools only; no arbitrary shell or SQL writes | **Use** |
| Agentic workflow | Bounded stateful investigation loop | LangGraph handles state/routing/checkpoints; no custom agent framework | **Use** |
| Planning | Investigation plan from problem + available data | LLM proposes; human approves before execution | **Use** |
| Human-in-the-loop | Plan approval/rejection/edit | LangGraph interrupt/checkpoint facilities | **Use** |
| RAG | Historical investigation retrieval | Conditional; only after completed investigations prove retrieval value | **Conditional** |
| Embeddings | Represent prior investigations for retrieval | Existing local embedding model/provider; no model training | **Conditional** |
| Vector search | Similar-investigation retrieval | PostgreSQL + pgvector if RAG is justified; no separate vector DB | **Conditional** |
| Speech-to-text | Audio → transcript → normal problem pipeline | Faster-Whisper; no custom speech engine | **Use** |
| AI evaluation | Benchmark framing, planning, tool choice, correctness, grounding, prescription | Small manually verified benchmark + repeatable evaluator | **Use** |
| AI observability | Trace model calls, workflow steps, tools, latency/failures | OpenTelemetry; no custom tracing platform | **Use** |
| Guardrails | Tool permissions, schema validation, evidence requirements, bounded loops | Application/tool boundaries rather than a separate guardrail product | **Use** |
| Grounding / provenance | Findings tied to analysis runs and evidence | Evidence objects carry source and analysis references | **Use** |
| Uncertainty / abstention | Refuse unsupported findings | Evidence sufficiency check and explicit insufficient-evidence state | **Use** |
| Local inference | Zero-cost normal runtime | Local provider such as Ollama; exact model deferred until hardware/setup phase | **Use** |
| Model/provider abstraction | Swap local/external inference without changing workflow | Narrow provider interface | **Use** |
| Automation workflows | Investigation completion → external action | One n8n webhook workflow; n8n owns automation logic | **Use** |
| Multimodal input | Speech as an additional input modality | Audio is optional; no image/video scope in MVP | **Limited** |
| Fine-tuning | None required | No custom training unless a later measured requirement exists | **Excluded** |
| Multi-agent orchestration | None | Single bounded workflow is sufficient | **Excluded** |
| Autonomous browser/web agents | None | No browsing requirement in core product | **Excluded** |
| Custom RAG framework | None | Use existing retrieval primitives if RAG is justified | **Excluded** |

## Supporting engineering capabilities

| Capability | Decision | Rationale / boundary |
|---|---|---|
| HTTP API | FastAPI | Mature API framework; no custom HTTP layer. |
| Data validation | Pydantic | Typed contracts rather than hand-written validation. |
| Analytical SQL | DuckDB | Local CSV/Parquet analysis without premature warehouse infrastructure. |
| Dataframes | Pandas | Mature ecosystem and existing project skill. |
| Statistical tests | SciPy | Do not implement statistical tests manually. |
| Visualizations | Matplotlib | Deterministic plotting; no custom charting engine. |
| Application database | PostgreSQL | Existing skill and sufficient for application/investigation state. |
| Containerization | Docker / Compose | Reproducible local runtime. |
| CI | GitHub Actions | Sufficient for project CI. |
| Frontend | React | Needed for the interactive workflow; UI remains deliberately small. |

## Decision rules

**Use:** integrate it when the product needs it. Do not rebuild the capability.

**Conditional:** do not implement until a concrete product requirement demonstrates that the MVP cannot perform its job without it.

**Limited:** cover only the narrow modality required by Signal.

**Excluded:** explicitly outside the product boundary.

ATS value is not a sufficient reason to move a capability from Conditional or Excluded to Use.

## Build-vs-integrate gate

Before a substantial implementation ticket starts, answer:

1. What user/product requirement needs this capability?
2. Does a mature library or service already solve it?
3. Can the existing capability meet Signal's requirements without disproportionate cost or complexity?
4. If not, what concrete limitation justifies additional implementation?

If the answer to #1 is missing, the ticket does not start.

## Cost policy

The default development and local runtime path must require no paid API or hosted service. External model providers are optional adapters, not dependencies. New paid infrastructure requires explicit justification.
