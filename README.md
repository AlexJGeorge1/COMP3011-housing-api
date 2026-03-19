# UK Housing Affordability Intelligence API

## Live API Demo 🚀
The API is fully deployed and accessible in the cloud. You can interact with it and test all endpoints directly through the browser without needing to install any code locally:

**[Live Interactive Documentation (Swagger UI)](https://housing-api-d2jt.onrender.com/docs)**
**[Live Health Check](https://housing-api-d2jt.onrender.com/health)**

*(Note: Hosted on Render's free tier, so it may take ~30 seconds to wake up if it has been idle).*

## Project Overview
This project is an Individual Web Services API Development Project for the COMP3011 module. 

The **UK Housing Affordability Intelligence API** is a data-driven web API that integrates and analyzes UK housing market data. It combines HM Land Registry Price Paid Data with Office for National Statistics (ONS) Annual Survey of Hours and Earnings (ASHE), and the ONS Private Rental Market Summary. By fusing these datasets, the API provides comprehensive affordability insights, regional price trends, rent-to-buy calculations, and AI-powered semantic search capabilities for properties across UK regions.

The API is built using **Python** and **FastAPI**, with **PostgreSQL** as the primary database, leveraging the **pgvector** extension for advanced embedding-based semantic search.

## Features
- **CRUD Operations**: Complete CRUD functionality for property listings and regional economic data.
- **Affordability Analytics**: Endpoints calculating price-to-income ratios and estimated mortgage requirements based on regional median salaries.
- **Rent-to-Buy Strategies**: Insights comparing local rental costs against potential mortgage payments.
- **Semantic Search**: AI-powered natural language property search using Groq LLM and pgvector embeddings.
- **Secure Access**: JWT-based authentication for sensitive endpoints.

## API Documentation
The complete API documentation, detailing all available endpoints, parameters, request/response formats, error codes, and the authentication process, is available as a PDF in the `docs` directory:
**[View API Documentation (PDF)](docs/API_Documentation.pdf)**

---

## Setup Instructions

### 1. Prerequisites
Ensure you have the following installed:
- **Python 3.11+**
- A **PostgreSQL** database that supports the `pgvector` extension (e.g., Neon or Supabase).

### 2. Installation
Clone the repository and install the required dependencies:
```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory (you can use `.env.template` as a starting point) and add the following:
```ini
# PostgreSQL connection string (must support pgvector)
DATABASE_URL="postgresql://[USER]:[PASSWORD]@[HOST]/[DBNAME]?sslmode=require"

# Authentication settings
SECRET_KEY="your-super-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES="30"
DEMO_USERNAME="admin"
DEMO_PASSWORD="secret"

# (Optional) Required for AI / Semantic Search features
GROQ_API_KEY="your-groq-api-key"
```

### 4. Database Setup & Migrations
Run Alembic migrations to create the database tables:
```bash
alembic upgrade head
```

### 5. Importing Data
The database must be seeded with regional data and property listings using the provided scripts:

1. **Import ONS Regional Data (Salaries & Rent)**:
   ```bash
   python scripts/import_ons_data.py
   ```
2. **Import Land Registry Data** (Use `--limit` for a manageable sample):
   ```bash
   python scripts/import_land_registry.py --year 2023 --limit 5000
   ```
3. **Generate Embeddings** (Optional, required for semantic `/search`):
   ```bash
   python scripts/generate_embeddings.py --limit 500
   ```

### 6. Running the API Locally
Start the FastAPI server using Uvicorn:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
You can view the interactive Swagger documentation locally at `http://localhost:8000/docs`.

## Testing
The project includes a comprehensive test suite utilizing an in-memory SQLite database to ensure functionality without requiring external database connections.
Run the tests using pytest:
```bash
pytest
```

## Deployment
The API is configured to be deployed as a Docker web service. A `render.yaml` and `Dockerfile` are included for seamless deployment to platforms like Render.

## 🤖 AI-Native Access (MCP Server)
The project includes an **MCP (Model Context Protocol)** server in `mcp_server.py` that exposes API functionality directly to AI assistants.

### Running the MCP Server
1. Ensure your core API is running (e.g., `uvicorn app.main:app`).
2. Run the MCP server with the **MCP Inspector** for testing:
   ```bash
   source .venv/bin/activate
   npx @modelcontextprotocol/inspector python mcp_server.py
   ```
   Open the printed URL (usually `http://localhost:5173`) in your browser to test endpoints visually using a nice UI interface dashboard easily.

