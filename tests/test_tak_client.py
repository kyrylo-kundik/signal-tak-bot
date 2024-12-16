import asyncio
import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from tak_client import TakClient
from exceptions import TakClientError
from fixture import tak_config, sample_geolocation, mock_stream


@pytest_asyncio.fixture
async def tak_client(tak_config):
    client = TakClient(tak_config)
    yield client
    await client.disconnect()


@pytest.mark.asyncio
async def test_connect_success(tak_client, mock_stream):
    reader, writer = mock_stream

    with patch("asyncio.open_connection", return_value=(reader, writer)):
        await tak_client.connect()
        assert tak_client._writer is writer
        assert tak_client._reader is reader


@pytest.mark.asyncio
async def test_connect_failure(tak_client):
    with patch(
        "asyncio.open_connection", side_effect=ConnectionError("Connection failed")
    ):
        with pytest.raises(TakClientError) as exc_info:
            await tak_client.connect()
        assert "Failed to connect to TAK server" in str(exc_info.value)


@pytest.mark.asyncio
async def test_disconnect(tak_client, mock_stream):
    reader, writer = mock_stream

    with patch("asyncio.open_connection", return_value=(reader, writer)):
        await tak_client.connect()
        await tak_client.disconnect()

        writer.close.assert_called_once()
        writer.wait_closed.assert_called_once()


@pytest.mark.asyncio
async def test_send_point_success(tak_client, mock_stream, sample_geolocation):
    reader, writer = mock_stream

    with patch("asyncio.open_connection", return_value=(reader, writer)):
        await tak_client.connect()
        await tak_client.send_point(sample_geolocation)

        writer.write.assert_called_once()
        writer.drain.assert_called_once()
