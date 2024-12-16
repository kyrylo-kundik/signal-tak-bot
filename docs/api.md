# API Documentation

## Data Models

### GeoLocation
```python
class GeoLocation(BaseModel):
    lat: float
    lon: float
    hae: Optional[float]
    ce: Optional[float]
    le: Optional[float]
    description: Optional[str]
    timestamp: datetime
```

### SignalMessage
```python
class SignalMessage(BaseModel):
    geolocation: GeoLocation
    message_id: UUID
    timestamp: datetime
    status: str
    retry_count: int
```

### CotEvent
```python
class CotEvent(BaseModel):
    event_id: str
    event_type: str
    time: datetime
    start: datetime
    stale: datetime
    how: str
    point: GeoLocation
    status: str
``` 

## Signal Client API

### Class: SignalClient

#### Constructor
```python
def __init__(self, config: SignalConfig)
```
- **Parameters:**
  - `config`: SignalConfig object containing configuration
- **Returns:** SignalClient instance

#### Connect
```python
async def connect()
```
- **Description:** Establishes connection to Signal API
- **Raises:** SignalClientError if connection fails

#### Send Message
```python
async def send_message(message: SignalMessage)
```
- **Parameters:**
  - `message`: object containing message data to send
- **Raises:** SignalClientError if sending fails

## TAK Client API

### Class: TakClient

#### Constructor
```python
def __init__(self, config: TakConfig)
```
- **Parameters:**
  - `config`: TakConfig object containing configuration
- **Returns:** TakClient instance

#### Connect
```python
async def connect()
```
- **Description:** Establishes connection to TAK server
- **Raises:** TakClientError if connection fails

#### Send Point
```python
async def send_point(point: GeoLocation)
```
- **Parameters:**
  - `point`: GeoLocation object containing coordinates to send
- **Raises:** TakClientError if sending fails
