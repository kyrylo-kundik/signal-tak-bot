# Usage Guide

## Running the Application

### Using Docker Compose

1. Start all services:
```bash
docker-compose up -d
```

2. Check service status:
```bash
docker-compose ps
```

3. View logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f signal-worker
docker-compose logs -f tak-worker
```

4. Stop services:
```bash
docker-compose down
```

### Manual Running

1. Start Redis server:
```bash
redis-server
```

2. Run Signal worker:
```bash
python signal_bot/signal_client.py
```

3. Run TAK worker:
```bash
python signal_bot/pytak_client.py
```

4. Run test application to spam geolocation messages for a while:
```bash
python signal_bot/test_app.py
```

## Message Format

### Signal Message Format
```
<longitude> <latitude> <description>
Example: -74.0060 40.7128 Tank in Manhattan
```

### CoT Protocol

The Cursor on Target (CoT) protocol is an XML-based schema used for sharing tactical information between different systems. It enables real-time situational awareness by defining various event types and their attributes.

#### Event Types
Common event types used in this application:

- `a-f-G-U-C`: Friendly Ground Unit Combat
  - Represents friendly combat units on the ground
  - Used for marking allied forces and vehicles

- `a-h-G`: Hostile Ground
  - Indicates detected or confirmed enemy ground forces
  - Used for marking potential threats

- `a-u-G`: Unknown Ground
  - Represents unidentified ground contacts
  - Used when the affiliation cannot be determined

- `b-a-o-tbl`: Emergency/911 
  - Indicates emergency situations or distress signals
  - High priority events requiring immediate attention

Each event type follows the format: `[a/b]-[f/h/u/n]-[G/A/S/U]-[type]-[subtype]`
- First letter: Atomic (a) or Bit (b)
- Second letter: Affiliation (friendly/hostile/unknown/neutral)
- Third letter: Battle dimension (Ground/Air/Sea/Subsurface)
- Additional qualifiers specify the exact type and subtype

#### Point Attributes
The Point element in CoT defines the geographic location of an event with the following attributes:

- `lat`: Latitude in decimal degrees (-90 to 90)
- `lon`: Longitude in decimal degrees (-180 to 180) 
- `hae`: Height above ellipsoid in meters
- `ce`: Circular error in meters (accuracy)
- `le`: Linear error in meters (vertical accuracy)

## Logging

- Location: `./logs/app.log`
- Rotation: 10MB per file
- Retention: 5 files
