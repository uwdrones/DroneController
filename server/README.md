# Drone Control Server

Python-based onboard server for drone control, running on Raspberry Pi with Pixhawk flight controller.

## 🏗️ Architecture

```
Ground Station (Go client)
    ⇅ gRPC (commands)
    ⇅ WebSocket (telemetry)
Raspberry Pi (Python server)
    ⇅ MAVLink / MAVSDK
Flight Controller (Pixhawk)
    ⇨ ESCs + motors (actual drone motion)
```

## 📁 Module Structure

- **`main.py`** - Supervisor script that runs all services concurrently
- **`mav_interface.py`** - MAVSDK wrapper for flight controller communication
- **`telemetry.py`** - Telemetry data processing and JSON formatting
- **`ws_server.py`** - WebSocket server for real-time telemetry streaming
- **`rpc_server.py`** - gRPC server for command interface (stub implementation)
- **`scripts/`** - Test scripts for individual components

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python main.py
```

This will start:
- MAVSDK connection (mock for now)
- WebSocket server on port 8765
- gRPC server on port 50051 (stub)

### 3. Test Individual Components

```bash
# Test MAV interface arm/disarm
python scripts/test_arm.py

# Test WebSocket telemetry streaming
python scripts/test_ws.py
```

## 🔧 Development Status

### ✅ Implemented (Stub)
- **MAV Interface**: Mock arm/disarm/get_status functions
- **WebSocket Server**: Real telemetry streaming on port 8765
- **Telemetry**: JSON formatting and client management
- **Main Supervisor**: Concurrent service management

### 🚧 TODO (Real Implementation)
- **MAVSDK Integration**: Replace stubs with actual MAVSDK calls
- **gRPC Server**: Implement actual gRPC service with protobuf
- **Protocol Buffers**: Define drone.proto and generate Python code
- **Error Handling**: Robust error handling and recovery
- **Configuration**: Environment-based configuration

## 📡 Communication Interfaces

### WebSocket Telemetry (Port 8765)
Real-time JSON telemetry stream:
```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "armed": false,
  "flight_mode": "STABILIZED",
  "battery": {"level": 85.5, "unit": "percent"},
  "position": {
    "latitude": 37.7749,
    "longitude": -122.4194,
    "altitude": 0.0,
    "unit": "meters"
  },
  "attitude": {"heading": 0.0, "unit": "degrees"},
  "velocity": {"ground_speed": 0.0, "unit": "m/s"},
  "connection": {"connected": true, "status": "connected"}
}
```

### gRPC Commands (Port 50051)
Command interface (stub):
- `Arm()` - Arm the drone
- `Disarm()` - Disarm the drone  
- `SetMode(mode)` - Set flight mode
- `GetStatus()` - Get current status

## 🧪 Testing

The server includes comprehensive test scripts:

- **`test_arm.py`**: Tests MAV interface arm/disarm functionality
- **`test_ws.py`**: Tests WebSocket telemetry streaming

Run tests to verify components work before integration.

## 🔄 Next Steps

1. **MAVSDK Integration**: Replace mock functions with real MAVSDK calls
2. **gRPC Implementation**: Create protobuf definitions and implement gRPC service
3. **Ground Station Client**: Develop Go client for commands and telemetry
4. **Error Recovery**: Add robust error handling and recovery mechanisms
5. **Configuration**: Add environment-based configuration system

## 📝 Notes

- Currently uses mock/stub implementations for rapid prototyping
- WebSocket telemetry is fully functional with mock data
- gRPC server is a placeholder for future implementation
- All components are designed for easy replacement with real implementations 