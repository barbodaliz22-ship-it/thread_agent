# Crypto Research Agent

An autonomous crypto **market research** system: it collects data, evaluates
strategies and analyst predictions, and runs backtests / paper trading. It
does **not** trade real money in its current phase.

## Project status: Phase 2 — Database layer

Phase 1 (foundation) plus:

- SQLAlchemy async engine/session (`app/database/session.py`)
- First ORM model: `OHLCVBar` (`app/models/market_data.py`) — carries
  `source`, `asset`, `timeframe`, business `timestamp`, `ingested_at`, and
  `quality_status` on every row, per the data-quality rules in section 6
  of the Master Prompt. A unique constraint on
  `(source, asset, timeframe, timestamp)` prevents duplicate bars at the
  DB level.
- Alembic migrations (`migrations/`), with an initial migration that
  creates the `ohlcv_bars` table.
- `/readiness` now actually pings the database instead of returning a
  stub.

Still not present: no data provider is wired up yet (nothing calls an
exchange API), no strategies, no execution. Phase 1 items remain:

- App configuration via environment variables (`app/config`)
- Structured (JSON) logging (`app/config/logging_config.py`)
- FastAPI app with `/health` and `/readiness` endpoints
- Docker + docker-compose setup (API, Postgres, Redis)
- pytest test suite
- A hard safety gate: the app **refuses to boot** if `TRADING_MODE=live`,
  because the risk and execution layers required for live trading do not
  exist yet. Safe defaults are `research_only` (default) and `paper`.

## Safety model

`TRADING_MODE` is the single switch controlling what the system is allowed
to do:

| Mode            | Behavior                                              |
|------------------|--------------------------------------------------------|
| `research_only` | Default. No orders of any kind — data + backtesting.   |
| `paper`         | Simulated orders against a virtual portfolio only.     |
| `live`          | Real orders. **Not implemented.** App refuses to start.|

No performance claims are made anywhere in this codebase. Every metric the
system will eventually report must come from measured, timestamped data —
see the Master Prompt's sections on analyst tracking (predictions must be
stored *before* their outcome is known) and analyst scoring.

## Getting started (local, no Docker)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env

uvicorn app.main:app --reload
```

Then visit `http://localhost:8000/health`.

## Getting started (Docker)

```bash
cp .env.example .env
docker compose up --build
```

## Running tests

```bash
pytest
```

## Running database migrations

Requires a running Postgres (via `docker compose up postgres` or your own):

```bash
alembic upgrade head
```

To create a new migration after changing a model:

```bash
alembic revision --autogenerate -m "describe the change"
```

## Project layout

```text
crypto-agent/
├── app/
│   ├── api/            # FastAPI routers
│   ├── config/          # settings + logging
│   ├── database/        # (Phase 2) SQLAlchemy models/session
│   ├── models/           # (Phase 2) ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── data/             # (Phase 2+) market/onchain/derivatives/news/sentiment providers
│   ├── research/          # (Phase 3) analyst + strategy tracking
│   ├── analysis/          # (Phase 3) technical/fundamental/sentiment/regime analysis
│   ├── prediction/        # (Phase 4)
│   ├── strategy/          # (Phase 4)
│   ├── risk/              # (Phase 5) risk controls, position sizing, emergency shutdown
│   ├── execution/         # (Phase 6) paper trading first, live later
│   ├── backtesting/       # (Phase 5) reproducible historical simulation
│   ├── paper_trading/     # (Phase 6)
│   ├── monitoring/        # (Phase 7)
│   └── main.py            # FastAPI app entrypoint
├── tests/
├── scripts/
├── migrations/            # Alembic migrations (Phase 2)
├── docker/
├── .env.example
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Roadmap (next phases)

1. ~~Foundation: config, logging, health endpoint, Docker, tests~~
2. ~~Database layer: SQLAlchemy models, Alembic migrations~~ ← you are here
   (note: model + migration exist; an actual market-data *provider* that
   fetches and writes real OHLCV rows is still Phase 2 unfinished business
   or early Phase 3, depending on how you want to sequence it)
3. Research layer: analyst/prediction tracking with pre-outcome timestamping
4. Analysis + regime detection, multi-layer signal combination
5. Backtesting engine + risk management layer
6. Paper trading execution
7. Monitoring, performance evaluation, and (much later, only after passing
   defined safety criteria) live trading
