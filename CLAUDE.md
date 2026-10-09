# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Windows dev environment, Python 3.12, virtualenv in `venv/`.

```bash
venv\Scripts\activate
pip install -r requirements.txt        # note: requirements.txt is UTF-16 encoded (pip freeze from PowerShell)
uvicorn main:app --reload              # Swagger UI is served at "/" (docs_url="/"), ReDoc at /redoc

alembic revision --autogenerate -m "msg"
alembic upgrade head

python -m scheduler.main               # standalone scheduler process (only for multi-instance setup, see below)
```

There is no test suite, linter, or formatter configured.

Config is read from `.env` via `core/config.py` (pydantic-settings): `DATABASE_URL` (PostgreSQL), `FRONTEND_URL` (sole CORS origin), `JWT_SECRET_KEY`, SMTP `EMAIL_*`/`SMTP_*`, and `UPSTASH_REDIS_REST_URL`/`_TOKEN`. Startup pings Redis, so the app won't boot without valid Upstash credentials.

## Architecture

FastAPI + SQLAlchemy 2.0 (sync, `Mapped`/`mapped_column`) + PostgreSQL, multi-tenant inventory management SaaS.

**Layering:** `routes/` (APIRouter, thin) → `services/` (business logic, raise `HTTPException` directly, take `db` and `business_id`) → `models/`. Pydantic request/response models live in `schema/`. `controllers/` is an empty leftover from a refactor that removed it — don't add code there. Every router must be registered manually in `main.py`.

**Schema changes go through Alembic** (`Base.metadata.create_all` is commented out). New model modules must be imported in both `models/__init__.py` and `alembic/env.py` for autogenerate to see them.

**Tenancy and auth (`core/dependencies.py`):**
- A user belongs to exactly one business via `BusinessMember` (roles: `OWNER`, `OPERATOR` in `models/enums.py`).
- `get_current_user` decodes the JWT, then also rejects users with no membership, a soft-deleted business, or a blocked subscription (`services/subscription_service.should_block_access`). So every authenticated route is subscription-gated.
- `get_current_business` is what most routes depend on; scope every query by `business.id`.
- `require_role(MemberRole.X)` for role-restricted endpoints.

**Automatic audit logging (`utils/audit_listener.py`):** global SQLAlchemy `before_flush`/`after_flush_postexec` listeners on `Session` record CREATE/UPDATE/DELETE diffs into `AuditLog` for any model instance that has an `id` and a resolvable `business_id`. Don't write audit rows manually; just be aware that any flush on a business-scoped model produces audit entries.

**Denormalized stock counters:** `Business` holds `total_products`, `low_stock_products`, `out_of_stock_products`. Any change to a product's `stock` or `minimum_stock` (create, quantity change, sale, delete) must go through `utils/inventory.apply_stock_change` so these counters stay consistent; don't mutate `product.stock` directly.

**Soft delete + retention:** most entities use a `deleted_at` column and queries filter `deleted_at.is_(None)`. Scheduler cleanup jobs hard-delete after the retention periods in `scheduler/policies.py`. Subscription lifecycle timings (grace period, warnings, permanent deletion) live in `utils/subscription_config.py`.

**Scheduler (APScheduler, `scheduler/`):** jobs registered via `scheduler/registery.py` (cleanup + subscription emails). Currently a `BackgroundScheduler` started/stopped in `main.py` startup/shutdown events, which assumes a single server instance. For multiple instances/workers, switch to the `BlockingScheduler` in `scheduler/scheduler.py`, remove the scheduler imports/events from `main.py`, and run `python -m scheduler.main` as a separate process (see `scheduler/ReadMe for Scheduelr`).

**Rate limiting (`services/rate_limiter/`):** Redis-backed, IP-based. Attach as a route dependency: `dependencies=[Depends(rate_limit(AuthRateLimits.LOGIN))]`; policies in `policies.py`.

**Email:** `utils/email_service.py` over SMTP; HTML templates in `utils/email_templates/`.

## Notes

- `graphify-out/` contains a generated call-graph/report of the codebase (`GRAPH_REPORT.md`) — may be useful for orientation but can be stale.
- `readme.md` and `changes needed back.md` are TODO lists of planned work (sale snapshots, RBAC expansion, reports export, low-stock alerts, query optimization), not documentation of current behavior.
