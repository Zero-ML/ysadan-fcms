import os
import sys
import dotenv
import pymongo
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

CASEFILES = Path('/casefiles')

# Setup logging
logger = logging.getLogger("fcms")
logger.setLevel(logging.DEBUG)
log_format = "%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s"
max_bytes = 10 * 1024 * 1024  # 10 MB
log_handlers = [
    logging.StreamHandler(sys.stdout),
    RotatingFileHandler(
        "fcms.log", maxBytes=max_bytes, backupCount=5, encoding="utf-8"
    ),
]
for handler in log_handlers:
    handler.formatter = logging.Formatter(log_format)
    logger.addHandler(handler)


class FCMSException(Exception):
    pass


class MissingEnvVar(FCMSException):
    pass


def get_env_var(var: str, default: str | None = None, error: bool = True) -> str | None:
    dotenv.load_dotenv()
    # Enable the next line to debug the env variables
    # logger.debug(json.dumps(dotenv.dotenv_values(verbose=True), indent=4))
    logger.info(f"Getting env var {var}")
    value = os.getenv(var, default)
    if value is None:
        message = f"Missing environment variable: {var}"
        if error:
            logger.error(message)
            raise MissingEnvVar(message)
        else:
            logger.warning(message)
    return value


def get_db() -> pymongo.database.Database:
    MONGODB_URI = get_env_var("MONGODB_URI")
    return pymongo.MongoClient(MONGODB_URI).get_default_database()
