import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
import asyncio

from signal_bot.config import SignalConfig, TakConfig, RedisConfig
from signal_bot.models import GeoLocation, SignalMessage, CotEvent


@pytest.fixture
def signal_config():
    """Signal client configuration fixture"""
    return SignalConfig(
        phone_number="+1234567890",
        api_url="https://signal-api.example.com",
        recipients=["+1987654321", "+1234567899"],
        max_reconnect_attempts=3
    )


@pytest.fixture
def tak_config():
    """TAK client configuration fixture"""
    return TakConfig(
        server_url="tak-server.example.com",
        port=8087,
        max_reconnect_attempts=3
    )


@pytest.fixture
def redis_config():
    """Redis client configuration fixture"""
    return RedisConfig(
        host="localhost",
        port=6379,
        db=0,
        password=None
    )


@pytest.fixture
def sample_geolocation():
    """Sample geolocation data fixture"""
    return GeoLocation(
        lat=40.7128,
        lon=-74.0060,
        hae=100.0,
        ce=45.0,
        le=45.0,
        description="Test Location",
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )


@pytest.fixture
def sample_signal_message(sample_geolocation):
    """Sample Signal message fixture"""
    return SignalMessage(
        geolocation=sample_geolocation
    )


@pytest.fixture
def sample_cot_event(sample_geolocation):
    """Sample CoT event fixture"""
    return CotEvent(
        event_id="test-event-id",
        event_type="a-f-G-U-C",
        time=sample_geolocation.timestamp,
        start=sample_geolocation.timestamp,
        stale=sample_geolocation.timestamp + datetime.timedelta(minutes=5),
        how="m-g",
        point=sample_geolocation,
        status="pending"
    )


@pytest.fixture
def mock_session():
    """Mock aiohttp ClientSession fixture"""
    session = AsyncMock()
    session.post = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_stream():
    """Mock asyncio StreamReader/StreamWriter fixture"""
    reader = AsyncMock(spec=asyncio.StreamReader)
    writer = AsyncMock(spec=asyncio.StreamWriter)
    writer.drain = AsyncMock()
    writer.write = MagicMock()
    writer.close = MagicMock()
    writer.wait_closed = AsyncMock()
    return reader, writer


@pytest.fixture
def mock_redis():
    """Mock Redis client fixture"""
    redis = AsyncMock()
    redis.ping = AsyncMock()
    redis.lpush = AsyncMock()
    redis.rpop = AsyncMock()
    redis.close = AsyncMock()
    return redis


@pytest.fixture
def fixed_datetime():
    """Fixed datetime for consistent testing"""
    return datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)


@pytest.fixture
def sample_geolocation_fixed(fixed_datetime):
    """Sample geolocation with fixed datetime for consistent testing"""
    return GeoLocation(
        lat=40.7128,
        lon=-74.0060,
        hae=100.0,
        ce=45.0,
        le=45.0,
        description="Test Location",
        timestamp=fixed_datetime
    )


@pytest.fixture
def sample_signal_message_fixed(sample_geolocation_fixed):
    """Sample Signal message with fixed datetime for consistent testing"""
    return SignalMessage(
        geolocation=sample_geolocation_fixed
    )


@pytest.fixture
def sample_cot_event_fixed(sample_geolocation_fixed, fixed_datetime):
    """Sample CoT event with fixed datetime for consistent testing"""
    return CotEvent(
        event_id="test-event-id",
        event_type="a-f-G-U-C",
        time=fixed_datetime,
        start=fixed_datetime,
        stale=fixed_datetime + datetime.timedelta(minutes=5),
        how="m-g",
        point=sample_geolocation_fixed,
        status="pending"
    ) 