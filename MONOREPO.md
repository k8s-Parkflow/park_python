# AutoE Monorepo Skeleton

## Directory Layout

- `services/` : independently deployable services
- `docs/architecture/` : design docs and ADRs

## Services

- `parking-command-service` : parking entry/exit write model
- `parking-query-service` : read model and query projection
- `vehicle-service` : vehicle registration/type ownership
- `zone-service` : zone and slot metadata ownership
- `orchestration-service` : synchronous cross-service workflow coordinator

## Principles

- One service, one database
- No cross-service DB foreign keys
- Integration will be added after each domain service is implemented
- Each service owns migrations/tests independently
- TDD is mandatory: RED -> GREEN -> REFACTOR for every feature
