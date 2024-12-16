class SignalBotError(Exception):
    pass


class SignalClientError(SignalBotError):
    pass


class TakClientError(SignalBotError):
    pass


class ConfigurationError(SignalBotError):
    pass


class RedisError(SignalBotError):
    pass


class MessageValidationError(SignalBotError):
    pass
