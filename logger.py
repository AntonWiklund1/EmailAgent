import colorlog
import logging


class ClientLogFilter(logging.Filter):
    """Filter to exclude logs from _client.py"""

    def filter(self, record):
        return not record.filename.endswith("_client.py")


def setup_logger():
    """Configure logger with colors, timestamps, and better formatting"""
    logger = colorlog.getLogger()
    if not logger.handlers:
        handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(
                fmt="%(log_color)s%(asctime)s [%(levelname)8s] %(blue)s%(filename)s%(reset)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
                secondary_log_colors={},
                style="%",
            )
        )
        # Add filter to exclude logs from _client.py
        client_filter = ClientLogFilter()
        handler.addFilter(client_filter)

        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
