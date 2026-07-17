# NFP Specification

Version: 0.1

## 1. Executive Summary

NFP (Nitin Financial Platform) is a personal financial operating system.

The purpose of the software is not bookkeeping. The purpose is to answer financial questions accurately using verifiable financial data.

The system imports financial documents, converts them into normalized financial events, stores them in SQLite, performs tax and investment calculations, and produces reports.

## 2. Goals

Primary goal:
- Create a trusted financial platform capable of answering personal financial questions accurately.

Secondary goals:
- Generate tax reports.
- Generate CA-ready summaries.
- Track investments.
- Track real estate.
- Track cash flows.
- Provide portfolio analytics.
- Provide retirement planning.
- Support AI-powered financial insights.

## 3. Non Goals

The first version of NFP will not attempt to become:
- An accounting package
- A trading platform
- A banking application
- A tax filing website
- A budgeting application
- A payment platform

NFP is a decision-support system.

## 4. MVP

The MVP has a single objective: generate a CA tax pack.

The MVP must ingest:
- Fidelity Investment Reports
- Fidelity Monthly Statements
- Fidelity Stock Plan Statements
- Fidelity Transaction Reports
- Builder Payment Ledger

The MVP must generate:
- RSU Summary
- Holdings Summary
- Capital Gains Summary
- FIFO Report
- Dividend Summary
- Foreign Tax Credit Summary
- Builder Payment Summary
- Section 54 Summary

No graphical interface is required. A command line application is sufficient.

## 5. Repository Structure

- `README.md`
- `SPEC.md`
- `TASKS.md`
- `PROMPTS.md`
- `SAMPLE_OUTPUTS.md`
- `DECISIONS.md`
- `CHANGELOG.md`
- `docs/`
- `samples/`
- `src/`
- `tests/`
- `pyproject.toml`
- `requirements.txt`
- `.gitignore`

## 6. Technology Stack

- Python 3.12+
- SQLite
- SQLAlchemy
- Alembic
- Pandas
- PyMuPDF
- pdfplumber
- OpenPyXL
- Pytest
- Ruff
- Black
- MyPy

## 7. High-Level Architecture

Documents -> Import Framework -> Financial Events -> SQLite Database -> Business Rules -> Report Generator -> CA Tax Pack

## 8. Architectural Principles

- Source documents are immutable.
- Every value must be traceable.
- Financial correctness is more important than performance.
- Imported data must be idempotent.
- Business logic must be separated from UI.
- Reports are generated, not manually edited.

## 9. Coding Standards

- Type hints required.
- Logging required.
- Tests required.
- Meaningful docstrings required.
- No hardcoded tax rates.
- No duplicated calculations.
- No calculations inside report generators.
- No parsing PDFs inside business logic.

## 10. Definition of Success

The MVP is successful when:
- Fidelity statements import successfully.
- Builder ledger imports successfully.
- FIFO calculations reconcile.
- Capital gains reconcile with Fidelity reports.
- Dividend totals reconcile.
- Builder payments reconcile.
- Excel reports are generated.
- The Chartered Accountant can use the generated reports without manual spreadsheets.

## 11. Instructions for AI Coding Agents

Read this specification completely before implementing.
Implement incrementally.
Write tests.
Preserve auditability.
If requirements are ambiguous, record assumptions instead of guessing.
Never sacrifice correctness for convenience.
