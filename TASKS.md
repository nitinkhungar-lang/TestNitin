# NFP Tasks

## EPIC-01 Project Setup
- Create Python project scaffold
- Configure linting and formatting
- Configure testing
- Configure logging
- Configure configuration loading

Acceptance criteria:
- Project installs successfully
- Linting passes
- Tests run
- Basic CLI entry point exists

## EPIC-02 Database Foundation
- Create SQLite schema
- Add SQLAlchemy models
- Add Alembic migrations
- Add repository layer

Acceptance criteria:
- Database initializes cleanly
- Migrations run cleanly
- Basic CRUD works

## EPIC-03 Event Model
- Define financial events
- Define document tracking
- Define audit trail

Acceptance criteria:
- Events are immutable
- Documents are idempotent
- Event lifecycle is documented

## EPIC-04 Import Framework
- Create importer interface
- Create parser base class
- Create validation pipeline
- Create reconciliation hooks

Acceptance criteria:
- Importers follow one interface
- Duplicate imports are prevented
- Validation and reconciliation are explicit

## EPIC-05 Fidelity Importer
- Parse annual reports
- Parse monthly statements
- Parse transaction summaries
- Normalize to common events

Acceptance criteria:
- Fidelity documents parse deterministically
- Holdings reconcile to statements

## EPIC-06 Builder Importer
- Parse builder ledger
- Normalize payments
- Map GST and milestones

Acceptance criteria:
- Ledger totals reconcile
- Payments are auditable

## EPIC-07 Business Rules Engine
- Implement FIFO
- Implement capital gains
- Implement dividend handling
- Implement foreign tax credit support
- Implement Section 54 and 54F support

Acceptance criteria:
- Calculations are reproducible
- Historical recalculation works

## EPIC-08 Reports
- Generate CA tax pack
- Generate Excel summaries
- Generate reconciliation reports

Acceptance criteria:
- Reports are reproducible
- Reports reference source documents

## EPIC-09 CLI
- Add command line commands for import and report generation

Acceptance criteria:
- CLI can run end-to-end flow

## EPIC-10 Testing & QA
- Add regression tests
- Add sample data tests
- Add reconciliation tests

Acceptance criteria:
- All core paths covered by tests

## EPIC-11 Documentation
- Keep docs synchronized with implementation
- Maintain architectural decisions
- Maintain prompts for Codex

Acceptance criteria:
- Documentation explains project structure clearly

## EPIC-12 Future Dashboard
- Add API foundation
- Add dashboard foundation
- Add financial copilot foundation

Acceptance criteria:
- Future extensibility preserved
