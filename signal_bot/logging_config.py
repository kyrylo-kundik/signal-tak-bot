import logging
import logging.handlers
import pathlib

import config


def setup_logging(cfg: config.AppConfig) -> None:
    """Configure application logging"""

    log_path = pathlib.Path(cfg.log_file).parent
    log_path.mkdir(parents=True, exist_ok=True)

    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(cfg.log_level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(cfg.log_level)
    root_logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        cfg.log_file, maxBytes=10_485_760, backupCount=5, encoding="utf-8"  # 10MB
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(cfg.log_level)
    root_logger.addHandler(file_handler)

    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("aioredis").setLevel(logging.WARNING)

    root_logger.info("Logging system initialized")
    root_logger.info(f"Log level: {cfg.log_level}")
    root_logger.info(f"Log file: {cfg.log_file}")
