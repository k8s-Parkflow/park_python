# Services

Each service directory is self-contained.

## Standard subdirectories

- `src/` : application source
- `test/` : acceptance/contract/unit tests (TDD order)
- `migrations/` : database migrations

## Current services

- `parking-command-service`
- `parking-query-service`
- `vehicle-service`
- `zone-service`
- `orchestration-service`

## TDD baseline

For each service feature:

1. acceptance test first
2. contract test second
3. unit test third
4. minimum implementation
5. refactor
