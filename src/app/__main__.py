"""``python -m app`` entrypoint for local development."""

from __future__ import annotations

import uvicorn

from app.core.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=not settings.is_production,
        log_config=None,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
