# NFP Codex Prompts

## Prompt 1: Project setup
Read README.md, SPEC.md and TASKS.md. Create the project scaffold for EPIC-01 only. Do not implement business logic yet. Add tests for the scaffold and ensure linting passes.

## Prompt 2: Database foundation
Implement EPIC-02 only. Create SQLite schema, SQLAlchemy models, and Alembic migrations. Keep the model aligned with SPEC.md. Add tests for basic persistence.

## Prompt 3: Event model
Implement EPIC-03 only. Add document tracking, event tracking, and audit trail support. Ensure imports are idempotent.

## Prompt 4: Import framework
Implement EPIC-04 only. Create a base importer interface and validation/reconciliation pipeline. Do not add Fidelity-specific parsing yet.

## Prompt 5: Fidelity importer
Implement EPIC-05 only. Parse Fidelity annual reports, monthly statements, and transaction summaries into normalized events. Add sample-based regression tests.

## Prompt 6: Builder importer
Implement EPIC-06 only. Parse the builder ledger and normalize payments, GST, and milestones.

## Prompt 7: Business rules engine
Implement EPIC-07 only. Add FIFO, capital gains, dividends, foreign tax credit, Section 54, and Section 54F rules. Each rule must be deterministic and test-covered.

## Prompt 8: Reports
Implement EPIC-08 only. Generate CA tax pack Excel reports and reconciliation outputs. Keep reporting separate from calculations.

## Prompt 9: CLI
Implement EPIC-09 only. Create command line entry points for import and report generation.

## Prompt 10: Testing and QA
Implement EPIC-10 only. Add regression tests, sample-data tests, and reconciliation tests.

## Prompt 11: Documentation
Implement EPIC-11 only. Keep docs synchronized and update DECISIONS.md when architectural choices are made.

## Prompt 12: Future dashboard
Implement EPIC-12 only. Add a minimal API and dashboard foundation without changing the core domain model.
