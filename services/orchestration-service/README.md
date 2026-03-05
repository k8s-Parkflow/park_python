# orchestration-service

Synchronous orchestrator for cross-service parking workflows.

## Responsibility

- Entry/exit orchestration across command/query/vehicle/zone services
- Retry/timeout/circuit-breaker policy at orchestration layer
- Idempotency handling for command APIs
- Compensation flow for partial failures

## TDD-first workflow (mandatory)

1. Write failing acceptance test in `test/acceptance/`
2. Write failing contract test in `test/contract/`
3. Write/adjust failing unit tests in `test/unit/`
4. Implement minimum code in `src/` to pass tests
5. Refactor while keeping tests green

Rule: no feature code merge without tests created first.

## Test directory convention

- `test/acceptance/`: user scenario tests (entry/exit/find/availability)
- `test/contract/`: API contract compatibility tests
- `test/unit/`: orchestration policy/domain logic tests
