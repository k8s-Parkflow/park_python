# Synchronous Orchestration Pattern

## Why

- Keep service ownership boundaries (DB per service)
- Avoid MQ for current phase
- Centralize multi-step workflow and error handling

## Principles

- Orchestrator calls downstream services synchronously
- Each request includes `Idempotency-Key` for write operations
- Timeout/retry/circuit-breaker configured centrally
- Compensation is explicit (best effort rollback)

## Initial flow

1. Entry request arrives at orchestration-service
2. Validate vehicle metadata via vehicle-service
3. Reserve/occupy slot via parking-command-service
4. Query current view from parking-query-service
5. Return unified response
