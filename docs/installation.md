# Installation Guide

## Prerequisites

### System Requirements
- Python 3.10+ and Redis 7+ for local development
- Docker and Docker Compose for production and Signal REST API access
- Signal Messenger account
- TAK server access

### Required Accounts
- Signal Messenger account with registered phone number
- Access to TAK server (public or private)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/signal-tak-bot.git
cd signal-tak-bot
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start Signal REST API service:
```bash
docker-compose up -d signal-rest
```

4. Link Signal REST API to your Signal account:
Proceed to the http://localhost:8080/v1/qrcodelink?device_name=signal-api 
and scan the QR code with your Signal account (Settings -> Linked Devices -> Scan QR Code).

> **Note:** If you omit this step, the bot will not be able to send messages to your Signal account.

5. Build and start services:
```bash
docker-compose up -d
```

## Configuration

### Environment Variables

#### Signal Configuration
```env
SIGNAL_PHONE_NUMBER="+1234567890"
SIGNAL_API_URL="https://signal-api.example.com"
SIGNAL_RECIPIENTS="+1987654321,+1234567899"
```

#### TAK Server Configuration
```env
TAK_SERVER_URL="tak-server.example.com"
TAK_SERVER_PORT=8087
```

#### Redis Configuration
```env
REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_PASSWORD=""
REDIS_DB=0
```

#### Logging Configuration
```env
LOG_LEVEL="INFO"
LOG_FILE="./logs/app.log"
```
