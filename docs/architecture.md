# System Architecture & Technical Design

## 1. Architectural Model
The platform adopts a modular layered architecture:
- **Presentation Layer**: HTML5, Bootstrap 5 Executive Theme, Flask Jinja2 templates.
- **Application Routing Layer**: 18 decoupled Flask blueprints registering under `app/routes/`.
- **Domain Service Layer**: Service interfaces under `app/services/` encapsulating business logic.
- **AI Engine Layer**: Multi-agent orchestration under `ai_engine/` handling LLM prompts, parsing, and vector representations.
- **Persistence Layer**: Flask-SQLAlchemy dual gateway supporting PostgreSQL and local SQLite.
