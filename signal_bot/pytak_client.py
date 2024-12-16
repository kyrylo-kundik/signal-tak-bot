import asyncio

import pytak

import config
import cot_formatter
import models
import redis_client


class PytakWorker(pytak.QueueWorker):
    def __init__(
        self, tx_queue: asyncio.Queue, cfg: dict, redis: redis_client.RedisClient
    ):
        super().__init__(tx_queue, cfg)

        self._redis = redis

    async def handle_event(self, event: models.CotEvent):
        formatter = cot_formatter.CotFormatter()

        await self.put_queue(formatter.format_event(event))

    async def run(self):
        while True:
            event = await self._redis.dequeue_tak_event()

            if event:
                await self.handle_event(event)


async def main():
    cfg = config.load_config()

    redis = redis_client.RedisClient(cfg.redis)

    pytak_cfg = {"COT_URL": f"tcp://{cfg.tak.server_url}:{cfg.tak.port}"}

    clitool = pytak.CLITool(pytak_cfg)

    await clitool.setup()

    await redis.connect()

    clitool.add_tasks({PytakWorker(clitool.tx_queue, pytak_cfg, redis)})

    try:
        await clitool.run()

    except KeyboardInterrupt:
        pass

    finally:
        await redis.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
