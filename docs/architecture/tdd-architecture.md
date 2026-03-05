# TDD Architecture Rules

This repository follows strict TDD for all services.

## Mandatory sequence (per feature)

1. Acceptance test first (business scenario)
2. Contract test second (API/schema compatibility)
3. Unit test third (domain/policy logic)
4. Minimal implementation
5. Refactor

## Merge gate

- No production code change without preceding failing tests.
- No contract change without compatibility test updates.
- Green test suite is required for all touched services.

## Test scope per service

- command services: domain integrity, transaction, idempotency
- query services: projection accuracy, query latency checks
- orchestration service: retry/timeout/compensation flow
