import logging
import sys

from healthcare_api.core.config import get_settings


def configure_logging(debug: bool = False) -> None:
    """Configure structured, predictable logging for the application.

    `debug=True` (typically `settings.debug`) forces DEBUG-level output
    regardless of `LOG_LEVEL`; otherwise the configured `log_level` is used.
    """
    settings = get_settings()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if debug else settings.log_level)

    # Quiet down noisy third-party loggers by default.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
