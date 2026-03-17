# Generative AI Declaration

## Overview

This document declares all Generative AI tools used during the development of the UK Housing Affordability Intelligence API, in accordance with the COMP3011 coursework assessment requirements. AI was used as a primary development tool throughout the project lifecycle.

## Tools Used

| Tool | Version / Model | Purpose |
|------|----------------|---------|
| Claude Code (Anthropic) | Claude Opus 4.6 | Primary development assistant — architecture planning, code generation, debugging, code review, security analysis |
| Claude (Anthropic) | Claude Sonnet / Opus | Conversational planning, exploring design alternatives, understanding FastAPI and SQLAlchemy patterns |

## How GenAI Was Used

### 1. Architecture and Planning
- Used Claude to evaluate technology stack options (FastAPI vs Django vs Express), weighing trade-offs around async support, automatic OpenAPI generation, and Pydantic validation.
- Discussed database design decisions including the use of pgvector for semantic search versus a separate vector database.
- Explored the feasibility of integrating LLM-powered insights using Groq's free tier.

### 2. Code Generation and Implementation
- Generated initial project scaffolding including Docker Compose configuration, Alembic migration setup, and SQLAlchemy model definitions.
- Used AI to write CRUD endpoint boilerplate, then manually reviewed and adapted each endpoint to the housing domain.
- AI assisted with writing the pgvector semantic search query and the embedding generation pipeline.
- The `/insights` endpoint prompt engineering was developed iteratively with AI assistance to ground LLM output in real database statistics and prevent hallucination.

### 3. Debugging and Testing
- Used Claude Code to identify and fix issues such as missing region imports in the Land Registry importer.
- AI generated the initial test suite structure, which was then extended to cover edge cases and authentication flows.
- Security vulnerability analysis was performed using Claude Code to identify issues like missing rate limiting and hardcoded credentials.

### 4. Documentation
- AI assisted with structuring the README and generating the OpenAPI specification.
- This GenAI declaration itself was drafted with AI assistance.

## Reflective Analysis

### Benefits
- AI significantly accelerated the development process, particularly for boilerplate code and configuration files that follow well-established patterns (Docker, Alembic, pytest fixtures).
- Exploring architectural alternatives through conversation helped identify the pgvector approach early, avoiding the complexity of maintaining a separate vector database.
- AI-assisted security analysis identified vulnerabilities that might have been missed in manual review.

### Limitations and Risks
- AI-generated code required careful review — initial suggestions sometimes included unnecessary abstractions or over-engineered patterns that were simplified.
- The AI occasionally produced code that worked in isolation but didn't account for project-specific constraints (e.g., suggesting features incompatible with Render's free tier).
- There is a risk of over-reliance: understanding *why* the code works is essential for the oral examination and professional development. Each AI-generated component was studied to ensure full comprehension.

### Critical Evaluation
- AI was most valuable for exploring unfamiliar technologies (pgvector, sentence-transformers) and for rapidly prototyping ideas before committing to an approach.
- AI was least valuable for domain-specific decisions about housing data — understanding the ONS and Land Registry datasets required reading the actual documentation and data dictionaries.
- The iterative workflow of prompting, reviewing, testing, and refining produced better results than accepting AI output uncritically.

## Conversation Logs

Selected conversation logs demonstrating AI usage are attached as supplementary material alongside this declaration.
