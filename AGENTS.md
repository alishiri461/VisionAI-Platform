# Repository Engineering Instructions

These instructions apply to the entire VisionAI-Platform repository.

## Mission
Build a modular, secure, observable computer-vision platform with a Python/FastAPI backend and a React/TypeScript web client. Deliver capabilities incrementally; do not claim a capability exists until its implementation and acceptance evidence are present.

## Non-negotiable engineering rules
1. Inspect the current branch, working tree, relevant source, tests, contracts, and CI evidence before editing.
2. Never commit directly to `main`. Work only on an explicitly scoped feature/fix/docs branch and use a pull request.
3. Preserve existing behavior, public API contracts, configuration names, and data formats unless a justified migration is documented.
4. Do not invent requirements, model performance, test results, security guarantees, endpoints, environment values, or infrastructure.
5. Implement only evidence-backed fixes. Avoid unrelated refactors and cosmetic churn.
6. Keep API/transport code separate from application orchestration, domain contracts, processing engines, model adapters, and infrastructure.
7. Bound all untrusted input and resource consumption: upload bytes, decoded pixels/dimensions, frame queues, batch sizes, inference concurrency, timeouts, and retained artifacts.
8. Make external resources explicit and lifecycle-managed. Avoid hidden global mutable state and unbounded background tasks.
9. Keep model runtimes behind adapters. Model weights are external artifacts; never commit large weights, secrets, or user data.
10. Add or update tests for behavior changes, negative cases, boundary conditions, and compatibility.
11. Update docs and examples whenever behavior, configuration, architecture, or operational requirements change.
12. Do not weaken lint, tests, typing, security checks, or CI merely to obtain a green pipeline.

## Architecture constraints
- Prefer a modular monolith until measured scale or deployment needs justify service extraction.
- Keep domain contracts independent of FastAPI, React, storage vendors, and concrete inference frameworks.
- Use explicit interfaces for image processing, object detection, model loading, video decoding, tracking, storage, and event delivery.
- Treat synchronous CPU/GPU work carefully in async request handlers. Use bounded worker execution or job processing when justified by profiling and workload requirements.
- Keep image coordinates, color channel order, tensor layout, preprocessing, normalization, and model metadata explicit in contracts.
- Keep browser video media transport separate from session/control signaling. Do not design unbounded WebSocket frame queues.
- Make persistence, queues, object storage, authentication, and multi-tenancy opt-in architecture decisions backed by requirements.

## Quality gates
- Backend: supported Python version, reproducible dependency installation, pytest, Ruff, and type checking when configured.
- Frontend: dependency installation, lint/typecheck when configured, and production build.
- API: schema/contract tests, upload rejection tests, and error-response consistency.
- Security: input validation, upload and decode limits, safe error handling, no secrets in source, and dependency review.
- CI: required jobs must pass on the exact PR head commit. Report skipped, unavailable, or inconclusive checks explicitly.
- Never state that tests/builds passed unless the command or CI result was actually observed.

## Change workflow
1. State observed baseline and target outcome.
2. Identify files/contracts affected and risks.
3. Make the smallest coherent change.
4. Add regression tests and docs.
5. Run available checks or inspect CI; capture exact result and commit SHA.
6. Review the diff for accidental changes and verify `main` is untouched.
7. Summarize changed files, evidence, limitations, and follow-up work.

## Capability status
The README and roadmap are the source of truth for implemented versus planned features. A type, protocol, placeholder, UI control, or roadmap entry is not a working capability by itself.
