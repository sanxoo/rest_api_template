_config = {

    "log.config": {
        "version": 1,
        "formatters": {
            "default": {
                "format" : "%(asctime)s %(levelname)-5s %(filename)s:%(lineno)3d : %(message)s"
            }
        },
        "handlers": {
            "file" : {
                "formatter": "default",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "/home/sanxoo/py/rest_api_template/log/api.log",
                "mode": "a",
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 9
            }
        },
        "loggers": {
            "": {
                "handlers": ["file"],
                "level": "DEBUG"
            },
            "asyncio": {
                "level": "WARNING"
            }
        },
        "disable_existing_loggers": False
    },

    "run.args": {
        "host": "0.0.0.0",
        "port": 8080
    },

    "database.url": "sqlite:///./db.sqlite/rest_api_template.db"
}

get = _config.get
