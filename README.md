# NFP

NFP (Nitin Financial Platform) is a personal financial operating system.

It is designed to help answer financial questions using auditable data from source documents.

## Primary objective

Create a decision-support system for personal finance, taxes, RSUs, property, and investments.

## Immediate MVP

Generate a CA-ready tax pack focused on:
- Fidelity RSU and stock plan data
- FIFO capital gains
- Dividend summaries
- Foreign tax credit support
- Builder payment summaries
- Section 54 / Section 54F support

## Core principles

- Financial correctness first
- Every value traceable to a source document
- Immutable source documents
- Idempotent imports
- Reproducible calculations
- Business logic separated from UI

## Technology stack

- Python 3.12+
- SQLite
- SQLAlchemy
- Alembic
- Pandas
- PyMuPDF / pdfplumber
- OpenPyXL
- Pytest
- Ruff / Black

## Repository layout

- `docs/` — architecture, domain model, database, importers, business rules, reports, testing
- `src/` — application code
- `tests/` — unit and integration tests
- `samples/` — representative input documents and expected outputs
- `scripts/` — helper scripts

## Development workflow

1. Read `SPEC.md`
2. Follow `TASKS.md`
3. Use `PROMPTS.md` for Codex instructions
4. Record architectural decisions in `DECISIONS.md`
5. Keep implementation incremental and test-driven

## Status

This repository is the starter kit for the first implementation of NFP.
