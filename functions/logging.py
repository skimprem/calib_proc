import logging


def setup_logging(enable_file_logging=False, log_file='calibration.log'):
    """
    Setup logging configuration
    
    Args:
        enable_file_logging (bool): Enable logging to file
        log_file (str): Path to log file
    """
    logger = logging.getLogger('calib_proc')
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler - always enabled
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
    
    # File handler - only if requested
    if enable_file_logging:
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        logger.info('Logging to file enabled: %s', log_file)
        logger.info('=' * 50)
    
    return logger

class CustomFormatter(logging.Formatter):
    """Simple formatter for console output without color codes"""
    
    def __init__(self):
        super().__init__("%(name)s: %(levelname)s: %(message)s")
