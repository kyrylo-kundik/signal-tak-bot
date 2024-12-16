import asyncio
import random

import config
import cot_formatter
import models
import redis_client


def generate_geolocation(n=10):
    for _ in range(n):
        yield models.GeoLocation(
            lat=random.uniform(-90, 90),
            lon=random.uniform(-180, 180),
            description=random.choice(
                ["Tank", "Helycopter", "Car", "Bicycle", "Person"]
            ),
        )


async def main():
    cfg = config.load_config()

    formatter = cot_formatter.CotFormatter()

    async with redis_client.RedisClient(cfg.redis) as redis:
        for geolocation in generate_geolocation():
            await redis.enqueue_tak_events(formatter.create_event(geolocation))

            # await redis.enqueue_signal_messages(
            # models.SignalMessage(geolocation=geolocation)
            # )

            await asyncio.sleep(random.uniform(0.1, 5.0))


if __name__ == "__main__":
    asyncio.run(main())
