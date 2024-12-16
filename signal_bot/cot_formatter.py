import xml.etree.ElementTree as ET
import datetime
import uuid

import models


class CotFormatter:
    EVENT_TYPES = {
        "default": "a-u-G",       # Default: Unknown Ground
        "hostile": "a-h-G",       # Hostile Ground
        "friendly": "a-f-G",      # Friendly Ground
        "unknown": "a-u-G",       # Unknown Ground
        "emergency": "b-a-o-tbl", # Emergency/911
    }
    HOW_VALUES = {
        "default": "m-g",         # GPS
        "estimated": "h-e",       # Human Entry
        "calculated": "h-c",      # Human Calculated
    }
    DEFAULT_XML_DECLARATION = b'<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
    DEFAULT_HOST_ID = "signal-bot"
    UUID_PREFIX = "signal:atak:bot"

    def __init__(self):
        """Initialize CoT formatter"""

    def format_event(self, event: models.CotEvent) -> bytes:
        """Format CoT event into XML bytes"""

        lat = str(event.point.lat or "0.0")
        lon = str(event.point.lon or "0.0")
        ce = str(event.point.ce or "9999999.0")
        hae = str(event.point.hae or "9999999.0")
        le = str(event.point.le or "9999999.0")

        xml = ET.Element("event")
        xml.set("version", "2.0")
        xml.set("type", event.event_type)
        xml.set("uid", event.event_id)
        xml.set("how", event.how)
        xml.set("time", self._format_datetime(event.time))
        xml.set("start", self._format_datetime(event.start))
        xml.set("stale", self._format_datetime(event.stale))

        point = ET.Element("point")
        point.set("lat", lat)
        point.set("lon", lon)
        point.set("le", le)
        point.set("hae", hae)
        point.set("ce", ce)

        flow_tags = ET.Element("_flow-tags_")
        _ft_tag: str = f"{self.DEFAULT_HOST_ID}-v1"
        flow_tags.set(_ft_tag, self._format_datetime(event.time))

        detail = ET.Element("detail")
        detail.append(flow_tags)

        xml.append(point)
        xml.append(detail)

        return b"\n".join([self.DEFAULT_XML_DECLARATION, ET.tostring(xml)])

    def create_event(
        self,
        point: models.GeoLocation,
        event_type: str = "default",
        how: str = "default",
        stale_minutes: int = 2,
    ) -> models.CotEvent:
        return models.CotEvent(
            event_id=self.UUID_PREFIX + str(uuid.uuid4()),
            event_type=self._get_event_type(event_type),
            time=point.timestamp,
            start=point.timestamp,
            stale=point.timestamp + datetime.timedelta(minutes=stale_minutes),
            how=self._get_how_value(how),
            point=point,
        )

    def _get_event_type(self, type_key: str) -> str:
        return self.EVENT_TYPES.get(type_key, self.EVENT_TYPES["default"])

    def _get_how_value(self, how_key: str) -> str:
        return self.HOW_VALUES.get(how_key, self.HOW_VALUES["default"])

    def _format_datetime(self, dt: datetime.datetime) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

if __name__ == "__main__":
    formatter = CotFormatter()
    event = formatter.create_event(
        models.GeoLocation(
            lat=40.7128, lon=-74.0060, hae=100, ce=100, le=100
        )
    )
    print(formatter.format_event(event))
