# The dictionary-based configuration for logging
LOGGING_CONFIG = {
    "disable_existing_loggers": False,  # IMPORTANT: Keep this False to configure Uvicorn's loggers
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(levelname)s %(asctime)s [%(name)s:%(lineno)d] - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 3,
        },
    },
    "loggers": {
        # Root logger
        "": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        # Uvicorn loggers
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,  # Don't pass to the root logger
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,  # Don't pass to the root logger
        },
    },
}
