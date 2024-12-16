import asyncio
import datetime
import json
import logging
import typing

import aioredis
import aioredis.exceptions

import config
import cot_formatter
import exceptions
import models


class RedisClient:
    SIGNAL_QUEUE = "signal:messages"
    TAK_QUEUE = "tak:events"
    DEAD_LETTER_QUEUE = "dead:letter:messages"

    def __init__(self, config: config.RedisConfig):
        """Initialize Redis client for message queuing"""
        self._config = config
        self._redis: typing.Optional[aioredis.Redis] = None
        self._logger = logging.getLogger(__name__)

    async def connect(self):
        try:
            self._redis = await aioredis.from_url(
                f"redis://{self._config.host}:{self._config.port}",
                password=self._config.password,
                db=self._config.db,
                encoding="utf-8",
                decode_responses=True,
            )

            await self._redis.ping()

            self._logger.info("Successfully connected to Redis")

        except aioredis.exceptions.RedisError as e:
            raise exceptions.RedisError(f"Failed to connect to Redis: {str(e)}") from e

    async def disconnect(self):
        if self._redis:
            await self._redis.close()

            self._logger.info("Disconnected from Redis")

    async def enqueue_signal_messages(self, message: models.SignalMessage):
        await self._enqueue_model(message, self.SIGNAL_QUEUE)

    async def enqueue_tak_events(self, event: models.CotEvent):
        await self._enqueue_model(event, self.TAK_QUEUE)

    async def dequeue_signal_message(self) -> typing.Optional[models.SignalMessage]:
        return await self._dequeue_model(models.SignalMessage, self.SIGNAL_QUEUE)

    async def dequeue_tak_event(self) -> typing.Optional[models.CotEvent]:
        return await self._dequeue_model(models.CotEvent, self.TAK_QUEUE)

    async def _dequeue_model(
        self,
        model: type[typing.Union[models.SignalMessage, models.CotEvent]],
        queue: str,
    ) -> typing.Optional[typing.Union[models.SignalMessage, models.CotEvent]]:
        try:
            if data := await self._redis.rpop(queue):
                return model(**json.loads(data))

            return None

        except aioredis.exceptions.RedisError as e:
            self._logger.error(f"Failed to dequeue {queue}: {str(e)}")

            raise exceptions.RedisError(f"Failed to dequeue {queue}: {str(e)}") from e

    async def _enqueue_model(
        self, model: typing.Union[models.SignalMessage, models.CotEvent], queue: str
    ):
        try:
            await self._redis.lpush(queue, model.model_dump_json())

            self._logger.info(f"Enqueued {model} to {queue}")

        except aioredis.exceptions.RedisError as e:
            self._logger.error(f"Failed to enqueue {model} to {queue}: {str(e)}")

            await self._on_failed_enqueuing(model, queue)

    async def _on_failed_enqueuing(
        self, model: typing.Union[models.SignalMessage, models.CotEvent], queue: str
    ):
        dead_letter = {
            "model": model.model_dump(),
            "queue": queue,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

        try:
            await self._redis.lpush(self.DEAD_LETTER_QUEUE, json.dumps(dead_letter))

        except aioredis.exceptions.RedisError as e:
            raise exceptions.RedisError(
                f"Failed to handle dead letter: {str(e)}"
            ) from e

    async def __aenter__(self):
        await self.connect()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


async def main():
    point = models.GeoLocation(lat=48.8566, lon=2.3522, description="Paris")
    cfg = config.RedisConfig(
        host="localhost",
        port=6379,
        db=1,
    )
    message = models.SignalMessage(geolocation=point)
    event = cot_formatter.CotFormatter().create_event(point)

    async with RedisClient(cfg) as redis:
        await redis.enqueue_signal_messages(message)
        await redis.enqueue_tak_events(event)

        message = await redis.dequeue_signal_message()
        event = await redis.dequeue_tak_event()

        print(message)
        print(event)


if __name__ == "__main__":
    asyncio.run(main())
