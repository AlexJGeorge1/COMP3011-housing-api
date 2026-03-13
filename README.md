# UK Housing Affordability Intelligence API

> **COMP3011 Web Services and Web Data — Individual Coursework**
> University of Leeds, 2025/26

A RESTful API that combines three UK public datasets to answer: **can someone on a regional median salary realistically afford to buy or rent a home in that region?**

The API integrates:
- 🏠 **HM Land Registry Price Paid Data** — property transaction prices (2015–2024)
- 💷 **ONS Annual Survey of Hours and Earnings (ASHE)** — median salaries by region
- 🔑 **ONS Private Rental Market Summary (PRMS)** — median rents by area



## Tech Stack

| Layer | Technology | Justification |
||||
| API Framework | FastAPI 0.111 | Async-native, auto-generates OpenAPI docs |
| Database | PostgreSQL 16 | Mandated; ACID-compliant, handles 8M+ rows |
| ORM | SQLAlchemy 2.x | Type-safe, migration-compatible |
| Migrations | Alembic | Schema version control |
| Vector Search | pgvector | Semantic search without a separate vector DB |
| Authentication | JWT (python-jose) | Stateless, industry-standard |
| LLM Integration | Anthropic Claude | AI-powered narrative analysis endpoint |
| Embeddings | sentence-transformers | Local CPU inference — free, private, reproducible |
| Containerisation | Docker Compose | Single-command deployment, reproducible |
| Testing | pytest + httpx | Async-compatible API testing |



## Prerequisites

- Docker Desktop 4.x+ (running)
- Python 3.11+
- Git



## Setup & Running

### 1. Clone and configure

```bash
git clone https://github.com/<your-username>/COMP3011-housing-api.git
cd COMP3011-housing-api
cp .env.template .env
# Edit .env and fill in required values (see below)
```

### 2. Start the stack

```bash
docker compose up --build
```

The API will be available at **http://localhost:8000**

### 3. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. Import data (optional — seeds the database with real data)

```bash
docker compose exec api python scripts/import_land_registry.py
docker compose exec api python scripts/import_ons_data.py
```



## Environment Variables

Copy `.env.template` to `.env` and configure:

| Variable | Required | Description |
||||
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | Random string for JWT signing (min 32 chars) |
| `ALGORITHM` | ✅ | JWT algorithm, use `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | Token lifetime, e.g. `30` |
| `ANTHROPIC_API_KEY` | ⚠️ Optional | Required for `/insights` endpoint; degrades gracefully if absent |



## API Endpoints

| Method | Endpoint | Auth | Description |
|||||
| GET | `/health` | Public | Service health check |
| POST | `/token` | Public | Obtain JWT access token |
| GET/POST/PUT/DELETE | `/listings` | Mixed | Property listing CRUD |
| GET/POST/PUT/DELETE | `/regions` | Mixed | Regional data CRUD |
| GET | `/affordability/{region}` | Public | Price-to-salary affordability score |
| GET | `/trends/{region}` | Public | Historical price trends |
| GET | `/rent-to-buy/{region}` | Public | Rent vs buy cost comparison |
| POST | `/search` | Public | Natural language semantic search |
| POST | `/insights` | Public | LLM-generated affordability narrative |

> Full interactive documentation: **http://localhost:8000/docs**
>
> API documentation PDF: see [`docs/api-documentation.pdf`](docs/api-documentation.pdf)



## Authentication

Write endpoints (POST, PUT, DELETE) require a Bearer token. To obtain one:

```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=secret"
```

Use the returned `access_token` as a Bearer token in subsequent requests.



## Data Scope & Ethics

This API uses a **2015–2024** window of Land Registry data (~8 million transactions). This scope was chosen deliberately:

- **Computational:** The full dataset (1995–present, 28M+ rows) would require significant infrastructure to import and query efficiently
- **Ethical:** Pre-2015 data predates consistent ONS salary methodology and key housing policy changes; cross-dataset joins against inconsistent historical methodology would introduce analytical bias



## Project Structure

```
housing-api/
├── app/
│   ├── main.py           # FastAPI app, middleware, router registration
│   ├── config.py         # Pydantic settings from .env
│   ├── database.py       # SQLAlchemy engine, session, Base
│   ├── auth.py           # JWT creation, verification, dependencies
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   └── routers/          # One file per resource/feature
├── scripts/              # Data import utilities
├── alembic/              # Database migrations
├── tests/                # pytest test suite
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.template
```

## GenAI

This project was developed with assistance from **Claude Sonnet 4.6** for architecture planning and design decision discussion. AI use is declared in accordance with COMP3011 assessment guidelines. Full conversation logs are included as Appendix A in the technical report.



