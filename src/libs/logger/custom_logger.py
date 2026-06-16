import logging


def setup_logging(level: str | None = None):
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": {"()": "pythonjsonlogger.jsonlogger.JsonFormatter"}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"level": level or "INFO", "handlers": ["console"]},
        }
    )


def get_logger(name: str):
    return logging.getLogger(f"booking.{name}")
