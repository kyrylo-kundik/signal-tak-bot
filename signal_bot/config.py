import dataclasses
import os
import typing

import dotenv

import exceptions


@dataclasses.dataclass
class SignalConfig:
    phone_number: str
    api_url: str
    recipients: typing.List[str]
    max_reconnect_attempts: int = 3


@dataclasses.dataclass
class TakConfig:
    server_url: str
    port: int
    max_reconnect_attempts: int = 3
    connection_timeout: int = 10


@dataclasses.dataclass
class RedisConfig:
    host: str
    port: int
    db: int
    password: typing.Optional[str] = None


@dataclasses.dataclass
class AppConfig:
    signal: SignalConfig
    tak: TakConfig
    redis: RedisConfig
    log_level: str
    log_file: str


def load_config() -> AppConfig:
    dotenv.load_dotenv()

    try:
        signal_config = SignalConfig(
            phone_number=os.environ["SIGNAL_PHONE_NUMBER"],
            api_url=os.environ["SIGNAL_API_URL"],
            recipients=os.environ["SIGNAL_RECIPIENTS"].split(","),
        )

        tak_config = TakConfig(
            server_url=os.environ["TAK_SERVER_URL"],
            port=int(os.environ["TAK_SERVER_PORT"]),
        )

        redis_config = RedisConfig(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            password=os.environ.get("REDIS_PASSWORD"),
            db=int(os.environ.get("REDIS_DB", "0")),
        )

        return AppConfig(
            signal=signal_config,
            tak=tak_config,
            redis=redis_config,
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
            log_file=os.environ.get("LOG_FILE", "./logs/app.log"),
        )

    except KeyError as e:
        raise exceptions.ConfigurationError(
            f"Missing required environment variable: {e}"
        )

    except ValueError as e:
        raise exceptions.ConfigurationError(f"Invalid configuration value: {e}")
