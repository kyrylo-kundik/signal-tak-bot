import asyncio
import logging
import typing

import config
import cot_formatter
import exceptions
import models


class TakClient:
    def __init__(self, cfg: config.TakConfig):
        """Initialize client for connecting to TAK server and sending CoT messages over TCP.

        Args:
            cfg: TAK server configuration parameters.
        """
        self._cfg = cfg
        self._formatter = cot_formatter.CotFormatter()
        self._logger = logging.getLogger(__name__)
        self._reader: typing.Optional[asyncio.StreamReader] = None
        self._writer: typing.Optional[asyncio.StreamWriter] = None

    async def connect(self):
        retry_count = 0
        
        while retry_count < self._cfg.max_reconnect_attempts:
            self._logger.info(f"Connecting to TAK server at {self._cfg.server_url}:{self._cfg.port}")

            try:
                self._reader, self._writer = await asyncio.wait_for(
                    asyncio.open_connection(
                        host=self._cfg.server_url,
                        port=self._cfg.port
                    ),
                    timeout=self._cfg.connection_timeout
                )
                self._logger.info("Successfully connected to TAK server")
                return

            except (ConnectionError, asyncio.TimeoutError) as e:
                self._logger.error(f"Connection attempt {retry_count} failed: {str(e)}")
            
            retry_count += 1
            
            await asyncio.sleep(2 ** retry_count)
        
        raise exceptions.TakClientError("Failed to connect to TAK server after maximum attempts")

    async def disconnect(self):
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()

            self._logger.info("Disconnected from TAK server")

    async def send_point(self, point: models.GeoLocation):
        """Send GeoLocation to TAK server as a CoT event.

        Args:
            point: GeoLocation to send.

        Raises:
            TakClientError: If connection fails during send operation.
        """
        if not self._writer:
            raise exceptions.TakClientError("No active connection to TAK server")

        event = self._formatter.create_event(point)
        formatted_event = self._formatter.format_event(event)

        try:
            self._writer.write(formatted_event)
            await self._writer.drain()

        except Exception as e:
            self._logger.error(f"Error writing event: {str(e)}")

            raise exceptions.TakClientError(f"Failed to write event: {str(e)}")

        self._logger.debug(f"Sent CoT event: {event.event_id}")

    async def __aenter__(self):
        await self.connect()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


async def main():
    cfg = config.TakConfig(
        server_url="137.184.101.250",
        port=8087
    )

    async with TakClient(cfg) as client:
        point = models.GeoLocation(lat=40.781789, lon=-73.968698, hae=0, ce=0, le=0)
        await client.send_point(point)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
