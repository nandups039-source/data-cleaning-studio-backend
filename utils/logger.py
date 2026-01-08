import logging

# Initialize root logger (will use settings from settings.py)
logger = logging.getLogger(__name__)

def log_info(message, extra=None):
    """
    Log an INFO message.
    :param message: str - The log message
    :param extra: dict - Optional extra info
    """
    if extra:
        logger.info(f"{message} | Extra: {extra}")
    else:
        logger.info(message)

def log_warning(message, extra=None):
    """
    Log a WARNING message.
    :param message: str - The log message
    :param extra: dict - Optional extra info
    """
    if extra:
        logger.warning(f"{message} | Extra: {extra}")
    else:
        logger.warning(message)

def log_error(message, extra=None):
    """
    Log an ERROR message.
    :param message: str - The log message
    :param extra: dict - Optional extra info
    """
    if extra:
        logger.error(f"{message} | Extra: {extra}")
    else:
        logger.error(message)
