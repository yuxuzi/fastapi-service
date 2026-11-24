# FastAPI services

A reference pack provided by the pytemplate-hub maintainer.

Two starting points for a FastAPI service, both with health and readiness endpoints, settings from
the environment, JSON logs with request IDs, an example resource behind a repository port, and
offline tests. Use them as a base to copy, change, and grow.

## What you get

Generated project with `-p service` (the `service-sql` profile adds `infrastructure/sql.py`,
`tests/test_sql.py`, and a database setting):

```text
my_app/
  pyproject.toml          # uv_build, ruff, mypy strict, pytest
  README.md  AGENTS.md  CLAUDE.md
  Dockerfile  .dockerignore  .env.example  .gitignore
  my_app/
    main.py               # ASGI entry point
    app.py                # create_app(): middleware, routers, repository
    settings.py           # typed settings, production checks
    logs.py               # JSON logs with request IDs
    domain/               # entity, error, repository port
    application/          # use cases
    infrastructure/       # in-memory repository (service) or SQLAlchemy (service-sql)
    api/                  # routers, schemas, dependencies, error mapping
  tests/                  # settings, logs, use cases, HTTP behaviour
```

## Profiles

| Profile | Kind | Status | What it adds |
| --- | --- | --- | --- |
| `service` | service | stable | FastAPI, uvicorn, pydantic-settings; in-memory example resource |
| `service-sql` | service | stable | The same, with the example stored through SQLAlchemy 2: SQLite by default, tables created at startup, tests on a temporary SQLite file, and a `postgres` extra for the PostgreSQL driver |

Both profiles need no secrets and include no authentication. Add authentication before exposing a
service beyond a trusted network. The profile files carry the full `security_posture` text.

## Create a project

```bash
uvx pytemplate-uv@latest create my-app -p service --template gh:yuxuzi/fastapi-service --template-ref v1.0.0 -y
```

Use `-p service-sql` for the SQL profile. The hub's listing page adds `--template-commit` and
`--template-digest` to pin the exact revision.

## What the generated checks run

Each profile's lifecycle runs, in order: `uv sync`, `uv run ruff check .`,
`uv run ruff format --check .`, `uv run mypy <package> tests`, and `uv run pytest`. The tests are
offline. They do not run the Dockerfile, deploy anything, or test PostgreSQL.

## Customizing

Fork the repository or copy the profile you need, edit the files under `<profile>/template/`, and
tag your own version. Keep `pytemplate-pack.toml`, `copier.yml`, and each `profile.toml` consistent
with the template files.

## License

MIT. See [LICENSE](LICENSE).
