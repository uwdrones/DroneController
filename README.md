# DroneController

Service router architecture for drone microservices with hardware and software integration.

## Architecture

DroneController implements a service router pattern for drone control microservices:

- **Service Router**: Central message routing for all drone operations
- **Protocol Interfaces**: WebSocket (8765), gRPC (50051), MAVLink (14540)
- **Hardware Integration**: MAVSDK wrapper for flight controller communication
- **Software Services**: Telemetry streaming, command processing, status monitoring

## Service Components

```
DroneController/
├── server/                 # Onboard service router
│   ├── main.py           # Service supervisor
│   ├── router.py         # Message routing engine
│   ├── handlers.py       # Service handlers
│   ├── schema.py         # Message schemas
│   ├── mav_interface.py  # Hardware service (MAVLink)
│   ├── ws_server.py      # WebSocket service (8765)
│   ├── rpc_server.py     # gRPC service (50051)
│   ├── telemetry.py      # Telemetry service
│   └── scripts/          # Service tests
├── client/               # Ground station client
└── config/              # Service configuration
```

## Service Router

The router handles message routing between services:

- **Command Messages**: ARM, DISARM, STATUS, SET_MODE
- **Telemetry Messages**: Periodic status broadcasting
- **Response Messages**: Service operation results
- **Error Handling**: Unknown actions, invalid formats

## Quickstart

```bash
cd server
pip install -r requirements.txt
python main.py
```

Services started:
- WebSocket service (port 8765)
- gRPC service (port 50051)
- MAVLink service (port 14540)
- Telemetry service (1Hz polling)

## Message Format

Unified message schema across all services:

```json
{
  "type": "command|telemetry|response",
  "action": "ARM|DISARM|STATUS|SET_MODE",
  "params": {},
  "data": {},
  "timestamp": 1761037019.558207
}
```

## Service Testing

```bash
# End-to-end service test
python scripts/test_router.py

# Individual service tests
python scripts/test_ws.py
python scripts/test_arm.py
python scripts/test_telemetry_polling.py
```

## Development Status

- **Implemented**: Service router, WebSocket/gRPC services, telemetry streaming
- **TODO**: Real MAVSDK integration, Go client, production deployment