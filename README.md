# UK Housing Affordability Intelligence API

A RESTful API built with **FastAPI**, **PostgreSQL + pgvector**, and **Llama 3 via Groq** that combines HM Land Registry Price Paid Data, ONS salary data, and ONS private rental statistics to deliver housing affordability insights across UK regions.

---

## Quick Start

```bash
# 1. Clone and enter the repo
git clone https://github.com/AlexJGeorge1/COMP3011-housing-api.git
cd COMP3011-housing-api

# 2. Copy environment config
cp .env.template .env           # then edit .env with your values

# 3. Build and start all services
docker compose up -d --build

# 4. Run database migrations
docker compose exec api alembic upgrade head
```

API is now running at `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

---

## Data Setup

No manual file downloads required — the importers fetch or use bundled data automatically.

```bash
# Import ONS salary + rent data into the `regions` table
# (data is hardcoded from ONS ASHE 2023 and ONS PRMS 2023)
docker compose exec api python scripts/import_ons_data.py

# Import Land Registry Price Paid data into the `listings` table
# (downloads directly from publicdata.landregistry.gov.uk — takes ~10 min per year)
docker compose exec api python scripts/import_land_registry.py
```

Run `import_ons_data.py` first — the affordability and rent-to-buy endpoints depend on region data being present.

---

## API Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/token` | — | Get a JWT token (`username: admin`, `password: secret`) |

### Listings (CRUD)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/listings` | — | List all listings (supports `?region=`, `?limit=`, `?offset=`) |
| GET | `/listings/{id}` | — | Get a single listing by UUID |
| POST | `/listings` | ✅ JWT | Create a new listing |
| PUT | `/listings/{id}` | ✅ JWT | Update a listing |
| DELETE | `/listings/{id}` | ✅ JWT | Delete a listing |

### Regions (CRUD)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/regions` | — | List all ONS regions |
| GET | `/regions/{id}` | — | Get a region by ID |
| POST | `/regions` | ✅ JWT | Create a region |
| PUT | `/regions/{id}` | ✅ JWT | Update a region |
| DELETE | `/regions/{id}` | ✅ JWT | Delete a region |

### Analytics
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/affordability/{region}` | — | Price-to-income ratio, rent-to-income %, affordability band |
| GET | `/trends/{region}` | — | Year-on-year median prices (2015–2024) + CAGR |
| GET | `/rent-to-buy/{region}` | — | Mortgage vs rent comparison + deposit savings timeline |

### Intelligence (AI)
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/search?q=` | — | Semantic property search using pgvector cosine similarity |
| GET | `/insights/{region}` | — | AI-generated market summary (Llama 3 via Groq) |

### Utility
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |
| GET | `/docs` | Interactive Swagger UI |

### Static Documentation
The comprehensive API documentation is included as a PDF: [API_Documentation.pdf](docs/API_Documentation.pdf).

---

## MCP Server

The API exposes an [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server so AI assistants can call the API as native tools:

```bash
# Start the API first, then run:
python mcp_server.py
```

Available tools: `get_affordability`, `get_trends`, `get_rent_to_buy`, `get_insights`, `search_listings`, `list_regions`.

---

## Testing

```bash
source .venv/bin/activate
pytest tests/ -v
```

Tests use an in-memory SQLite database — no Docker required. A small number of tests are skipped on SQLite as they require PostgreSQL's `percentile_cont` aggregate.

---

## Architecture

```
┌─────────────────────────────────────────┐
│             FastAPI Application         │
│  ┌─────────┐  ┌──────────┐  ┌───────┐  │
│  │Listings │  │ Regions  │  │ Auth  │  │
│  │  CRUD   │  │  CRUD    │  │  JWT  │  │
│  └─────────┘  └──────────┘  └───────┘  │
│  ┌──────────────────────────────────┐   │
│  │       Analytics Endpoints        │   │
│  │  /affordability  /trends         │   │
│  │  /rent-to-buy                    │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │        Intelligence Layer        │   │
│  │  /search (pgvector)              │   │
│  │  /insights (Llama 3 via Groq)    │   │
│  └──────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
        ┌───────▼────────┐
        │  PostgreSQL 16  │
        │  + pgvector     │
        └────────────────┘
```

### Key Design Decisions
- **pgvector** — enables cosine similarity semantic search without a separate vector database
- **`percentile_cont(0.5)`** — true SQL median (not average) for accurate house price reporting  
- **`all-MiniLM-L6-v2`** — 384-dim local sentence embedding model; no API calls, fully reproducible
- **Groq / Llama 3** — free-tier LLM grounded in real DB statistics to prevent hallucination
- **Alembic** — schema migrations keep the database schema version-controlled

---

## Environment Variables

See `.env.template` for all variables. Key ones:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret (generate with `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `GROQ_API_KEY` | Free key from [console.groq.com](https://console.groq.com) — required for `/insights` |

---

## Tech Stack

| Component | Technology |
|---|---|
| Framework | FastAPI 0.111 |
| Database | PostgreSQL 16 + pgvector |
| ORM / Migrations | SQLAlchemy 2 + Alembic |
| Auth | JWT (python-jose + passlib) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| LLM | Llama 3.1 8B via Groq API |
| MCP | FastMCP |
| Testing | pytest + SQLite (in-memory) |
| Containerisation | Docker Compose |

---

## License

MIT — see [LICENSE](LICENSE).
