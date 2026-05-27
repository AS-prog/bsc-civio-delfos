# Docker Runtime Environment Specification

## Purpose

Define the minimal local runtime for Civio-aligned data work while preserving this repository as docs-first. The runtime MUST provide Python and PostgreSQL only, with local secrets and state kept out of version control.

## Requirements

### Requirement: Compose Runtime Services

The system MUST provide a Docker Compose runtime that starts a Python service and a PostgreSQL service together.

#### Scenario: Start runtime successfully

- GIVEN Docker Compose is available and the project files are present
- WHEN a contributor starts the runtime from the repository root
- THEN the PostgreSQL service SHALL become available
- AND the Python service SHALL start without requiring host Python dependencies

#### Scenario: Unsupported service is requested

- GIVEN this change is limited to Python and PostgreSQL
- WHEN a contributor reviews the runtime definition
- THEN it MUST NOT include frontend, Jupyter, API framework, or Makefile behavior

### Requirement: Environment-based Database Connection

The Python service MUST connect to PostgreSQL using environment variables rather than hard-coded credentials.

#### Scenario: Connect using configured environment

- GIVEN database environment variables are supplied to the runtime
- WHEN the Python service runs the connection check
- THEN it SHALL connect to the PostgreSQL service using those variables

#### Scenario: Missing connection configuration

- GIVEN one or more required database environment variables are absent
- WHEN the connection check runs
- THEN it MUST fail clearly without embedding real credentials in source files

### Requirement: Local Secrets Policy

The repository MUST version a `.env.example` template and MUST NOT require or commit real local secrets.

#### Scenario: Contributor creates local environment file

- GIVEN `.env.example` exists with non-sensitive placeholder values
- WHEN a contributor copies it to `.env` and customizes local values
- THEN the runtime SHALL be configurable locally
- AND `.env` MUST remain ignored by version control

#### Scenario: Accidental secret candidate

- GIVEN a contributor creates a local `.env`
- WHEN they inspect version-control status
- THEN `.env` MUST NOT appear as a tracked or staged file

### Requirement: PostgreSQL Local Persistence

The PostgreSQL service MUST use local persistent storage that survives normal container restarts and remains disposable project state.

#### Scenario: Data survives ordinary restart

- GIVEN data has been written to PostgreSQL
- WHEN the contributor stops and starts the runtime without deleting volumes
- THEN the data SHOULD remain available

#### Scenario: Contributor removes persistent state

- GIVEN the contributor intentionally deletes the PostgreSQL volume
- WHEN the runtime starts again
- THEN PostgreSQL MAY initialize with empty local state

### Requirement: Smoke Verification

The change MUST provide a minimal verification path that proves Python can reach PostgreSQL.

#### Scenario: Smoke test passes

- GIVEN the runtime services are running
- WHEN the contributor executes the documented smoke verification command
- THEN the command MUST report a successful PostgreSQL connection

#### Scenario: Database unavailable

- GIVEN PostgreSQL is not reachable from the Python service
- WHEN the smoke verification command runs
- THEN it MUST exit unsuccessfully and identify connection failure

### Requirement: Scope Boundary

This change MUST remain a minimal data runtime scaffold and MUST NOT introduce unrelated product surfaces.

#### Scenario: Review confirms excluded scope

- GIVEN the change is ready for review
- WHEN reviewers inspect the changed files
- THEN they SHALL find no Svelte/frontend, Jupyter, API framework, CI/CD, scraper implementation, or Makefile additions
