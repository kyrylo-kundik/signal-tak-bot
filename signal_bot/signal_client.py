import asyncio
import logging
import typing

import aiohttp

import config
import exceptions
import models
import redis_client


class SignalClient:
    def __init__(self, config: config.SignalConfig):
        """Initialize Client for interacting with Signal Messenger REST API"""
        self._config = config
        self._session: typing.Optional[aiohttp.ClientSession] = None
        self._logger = logging.getLogger(__name__)

    async def connect(self):
        self._session = aiohttp.ClientSession(
            base_url=self._config.api_url, headers={"Content-Type": "application/json"}
        )
        self._logger.info("Successfully connected to Signal API")

    async def disconnect(self):
        if self._session:
            await self._session.close()

            self._logger.info("Disconnected from Signal API")

    async def send_message(self, message: models.SignalMessage):
        """Send GeoLocation through Signal Messenger REST API.

        Args:
            message: GeoLocation to send.

        Raises:
            SignalClientError: If connection fails during send operation.
        """
        if not self._session:
            raise exceptions.SignalClientError("Client not properly connected")

        while message.retry_count < self._config.max_reconnect_attempts:
            try:
                async with self._session.post(
                    "/v2/send",
                    json={
                        "recipients": self._config.recipients,
                        "number": self._config.phone_number,
                        "message": message.content,
                    },
                ) as response:
                    if 200 <= response.status < 300:
                        message.status = "sent"

                        self._logger.info(
                            f"Message {message.message_id} sent successfully"
                        )

                        return

            except aiohttp.ClientError as e:
                self._logger.error(
                    f"Error sending message {message.message_id}: {str(e)}"
                )

            message.retry_count += 1

            await asyncio.sleep(2**message.retry_count)  # Exponential backoff

        message.status = "failed"

        raise exceptions.SignalClientError(
            f"Failed to send message after {self._config.max_reconnect_attempts} attempts"
        )

    async def __aenter__(self):
        await self.connect()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


async def main():
    cfg = config.load_config()

    redis = redis_client.RedisClient(cfg.redis)

    await redis.connect()

    try:
        while True:
            message = await redis.dequeue_signal_message()

            if not message:
                continue

            async with SignalClient(cfg.signal) as client:
                await client.send_message(message)

    except KeyboardInterrupt:
        pass

    finally:
        await redis.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
