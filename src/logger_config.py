import logging

def setup_logging(log_file: str, log_level: int = logging.INFO):
    """
    Sets up logging with a console handler and a file handler.
    
    Args:
        log_file (str): The path to the log file.
        log_level (int): The logging level (default is logging.INFO).
    """
    # Create a logger object
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    file_handler = logging.FileHandler(
        filename=log_file,
        mode='a',
        encoding='utf-8',
    )

    # Create a formatter and set it for the handlers
    formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)

    return logger
