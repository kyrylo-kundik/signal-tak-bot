import datetime
import uuid
from xml.etree import ElementTree as ET

import pytest

from signal_bot.cot_formatter import CotFormatter
from signal_bot.models import GeoLocation, CotEvent
from .fixture import (
    sample_geolocation_fixed,
    sample_cot_event_fixed,
    fixed_datetime
)


@pytest.fixture
def formatter():
    return CotFormatter()


def test_event_type_mapping(formatter):
    assert formatter._get_event_type("default") == CotFormatter.EVENT_TYPES["default"]
    assert formatter._get_event_type("hostile") == CotFormatter.EVENT_TYPES["hostile"]
    assert formatter._get_event_type("friendly") == CotFormatter.EVENT_TYPES["friendly"]
    assert formatter._get_event_type("unknown") == CotFormatter.EVENT_TYPES["unknown"]
    assert formatter._get_event_type("emergency") == CotFormatter.EVENT_TYPES["emergency"]
    # Test invalid type falls back to default
    assert formatter._get_event_type("invalid") == CotFormatter.EVENT_TYPES["default"]


def test_how_value_mapping(formatter):
    assert formatter._get_how_value("default") == CotFormatter.HOW_VALUES["default"]
    assert formatter._get_how_value("estimated") == CotFormatter.HOW_VALUES["estimated"]
    assert formatter._get_how_value("calculated") == CotFormatter.HOW_VALUES["calculated"]
    # Test invalid value falls back to default
    assert formatter._get_how_value("invalid") == CotFormatter.HOW_VALUES["default"]


def test_datetime_formatting(formatter):
    dt = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    formatted = formatter._format_datetime(dt)
    assert formatted == "2024-01-01T12:00:00.000000Z"


def test_create_event(formatter, sample_geolocation):
    event = formatter.create_event(
        point=sample_geolocation,
        event_type="friendly",
        how="estimated",
        stale_minutes=5
    )

    assert event.event_id.startswith(CotFormatter.UUID_PREFIX)
    assert event.event_type == CotFormatter.EVENT_TYPES["friendly"]
    assert event.how == CotFormatter.HOW_VALUES["estimated"]
    assert event.point == sample_geolocation
    assert event.time == sample_geolocation.timestamp
    assert event.start == sample_geolocation.timestamp
    assert event.stale == sample_geolocation.timestamp + datetime.timedelta(minutes=5)


def test_format_event(formatter, sample_cot_event):
    xml_bytes = formatter.format_event(sample_cot_event)
    
    assert isinstance(xml_bytes, bytes)
    
    xml_str = xml_bytes.decode('utf-8')
    root = ET.fromstring(xml_str)
    
    assert root.tag == "event"
    assert root.get("version") == "2.0"
    assert root.get("type") == sample_cot_event.event_type
    assert root.get("uid") == sample_cot_event.event_id
    assert root.get("how") == sample_cot_event.how
    assert root.get("time") == formatter._format_datetime(sample_cot_event.time)
    assert root.get("start") == formatter._format_datetime(sample_cot_event.start)
    assert root.get("stale") == formatter._format_datetime(sample_cot_event.stale)

    point = root.find("point")
    assert point is not None
    assert float(point.get("lat")) == sample_cot_event.point.lat
    assert float(point.get("lon")) == sample_cot_event.point.lon
    assert float(point.get("hae")) == sample_cot_event.point.hae
    assert float(point.get("ce")) == sample_cot_event.point.ce
    assert float(point.get("le")) == sample_cot_event.point.le

    detail = root.find("detail")
    assert detail is not None
    flow_tags = detail.find("_flow-tags_")
    assert flow_tags is not None
    assert f"{CotFormatter.DEFAULT_HOST_ID}-v1" in flow_tags.attrib


def test_xml_declaration(formatter, sample_cot_event):
    xml_bytes = formatter.format_event(sample_cot_event)
    xml_str = xml_bytes.decode('utf-8')
    
    assert xml_str.startswith('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>')


def test_create_event_defaults(formatter, sample_geolocation):
    event = formatter.create_event(sample_geolocation)
    
    assert event.event_type == CotFormatter.EVENT_TYPES["default"]
    assert event.how == CotFormatter.HOW_VALUES["default"]
    assert (event.stale - event.time) == datetime.timedelta(minutes=2)


@pytest.mark.parametrize("lat,lon", [
    (90.0, 180.0),    # Maximum values
    (-90.0, -180.0),  # Minimum values
    (0.0, 0.0),       # Zero values
    (45.5, -122.5),   # Decimal values
])
def test_coordinate_ranges(formatter, lat, lon):
    point = GeoLocation(
        lat=lat,
        lon=lon,
        timestamp=datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc)
    )
    event = formatter.create_event(point)
    xml_bytes = formatter.format_event(event)
    
    xml_str = xml_bytes.decode('utf-8')
    root = ET.fromstring(xml_str)
    point_elem = root.find("point")
    
    assert float(point_elem.get("lat")) == lat
    assert float(point_elem.get("lon")) == lon 
