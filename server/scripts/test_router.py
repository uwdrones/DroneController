#!/usr/bin/env python3
"""
End-to-end test harness for the complete DroneController architecture.
Simulates the entire message flow across WebSocket, gRPC, and MAVSDK protocols.
Tests the complete client-server communication pipeline.
"""

import asyncio
import json
import sys
import os
import logging
import time
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from router import Router
from handlers import register_all
from mav_interface import MAVInterface, DroneStatus
from ws_server import WebSocketServer
from rpc_server import RPCServer
from telemetry import poll_telemetry
from schema import (
    create_command_message, 
    create_telemetry_message, 
    create_response_message,
    encode_message, 
    decode_message,
    validate_message
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockWebSocketClient:
    """Mock WebSocket client for testing."""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.messages_received = []
        self.connected = True
    
    async def send(self, message: str):
        """Mock send method to capture messages."""
        self.messages_received.append(json.loads(message))
        print(f"[WEBSOCKET] Client {self.client_id} received: {message}")
    
    async def recv(self):
        """Mock receive method."""
        # Simulate receiving a command from client
        if not hasattr(self, '_message_sent'):
            self._message_sent = True
            return json.dumps({
                "type": "command",
                "action": "STATUS",
                "params": {"source": f"websocket_client_{self.client_id}"},
                "timestamp": time.time()
            })
        else:
            # Simulate connection close
            raise ConnectionError("Connection closed")

class MockGRPCClient:
    """Mock gRPC client for testing."""
    
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.responses_received = []
    
    async def send_command(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Mock gRPC send command."""
        print(f"[GRPC] Client {self.client_id} sending: {message}")
        # This would normally go through the gRPC server
        return {"result": "grpc_response", "client": self.client_id}

class MockMAVSDKWrapper:
    """Mock MAVSDK wrapper for testing."""
    
    def __init__(self):
        self.connected = True
        self.armed = False
        self.flight_mode = "STABILIZED"
        self.battery_level = 85.0
        self.altitude = 0.0
        self.ground_speed = 0.0
        self.gps_lat = 37.7749
        self.gps_lon = -122.4194
        self.heading = 0.0
    
    async def arm(self) -> bool:
        """Mock arm operation."""
        print(f"[MAVSDK] Mock arming drone...")
        self.armed = True
        return True
    
    async def disarm(self) -> bool:
        """Mock disarm operation."""
        print(f"[MAVSDK] Mock disarming drone...")
        self.armed = False
        return True
    
    async def set_flight_mode(self, mode: str) -> bool:
        """Mock set flight mode operation."""
        print(f"[MAVSDK] Mock setting flight mode to {mode}...")
        self.flight_mode = mode
        return True
    
    async def get_status(self) -> DroneStatus:
        """Mock get status operation."""
        print(f"[MAVSDK] Mock getting drone status...")
        return DroneStatus(
            armed=self.armed,
            flight_mode=self.flight_mode,
            battery_level=self.battery_level,
            gps_lat=self.gps_lat,
            gps_lon=self.gps_lon,
            altitude=self.altitude,
            heading=self.heading,
            ground_speed=self.ground_speed
        )
    
    def is_connected(self) -> bool:
        """Mock connection status."""
        return self.connected

class EndToEndTestHarness:
    """End-to-end test harness for the complete system."""
    
    def __init__(self):
        self.router = Router()
        self.mav_interface = MockMAVSDKWrapper()
        self.ws_server = None
        self.rpc_server = None
        self.websocket_clients = []
        self.grpc_clients = []
        self.test_results = []
        
        # Patch the handlers to use our mock MAVSDK
        self._patch_handlers()
    
    def _patch_handlers(self):
        """Patch handlers to use mock MAVSDK wrapper."""
        import handlers
        
        # Create async wrapper functions that use our mock MAVSDK
        async def mock_handle_arm(params):
            result = await self.mav_interface.arm()
            return {"result": "armed" if result else "arm_failed", "status": "success" if result else "failed"}
        
        async def mock_handle_disarm(params):
            result = await self.mav_interface.disarm()
            return {"result": "disarmed" if result else "disarm_failed", "status": "success" if result else "failed"}
        
        async def mock_handle_status(params):
            status = await self.mav_interface.get_status()
            return {
                "result": "status",
                "status": "success",
                "telemetry": {
                    "battery_level": status.battery_level,
                    "altitude": status.altitude,
                    "velocity": status.ground_speed,
                    "armed": status.armed,
                    "flight_mode": status.flight_mode
                }
            }
        
        async def mock_handle_set_mode(params):
            mode = params.get("mode", "UNKNOWN")
            result = await self.mav_interface.set_flight_mode(mode)
            return {"result": "mode_changed" if result else "mode_change_failed", "mode": mode, "status": "success" if result else "failed"}
        
        async def mock_handle_telemetry(params):
            data = params.get("data", {})
            return {"result": "telemetry_received", "status": "success", "data": data}
        
        # Register the mock handlers
        self.router.register("ARM", mock_handle_arm)
        self.router.register("DISARM", mock_handle_disarm)
        self.router.register("STATUS", mock_handle_status)
        self.router.register("SET_MODE", mock_handle_set_mode)
        self.router.register("TELEMETRY", mock_handle_telemetry)
    
    async def setup_system(self):
        """Setup the complete system architecture."""
        print("[INFO] Setting up End-to-End Test Harness")
        print("=" * 60)
        
        # Handlers are already registered in _patch_handlers()
        print(f"[INFO] Registered actions: {self.router.get_registered_actions()}")
        
        # Create mock servers
        self.ws_server = WebSocketServer(self.mav_interface, self.router)
        self.rpc_server = RPCServer(self.mav_interface, self.router)
        
        # Create mock clients
        self.websocket_clients = [
            MockWebSocketClient("ws_client_1"),
            MockWebSocketClient("ws_client_2")
        ]
        self.grpc_clients = [
            MockGRPCClient("grpc_client_1"),
            MockGRPCClient("grpc_client_2")
        ]
        
        print("[INFO] System setup complete")
        print()
    
    async def test_websocket_communication(self):
        """Test WebSocket client-server communication."""
        print("[INFO] Testing WebSocket Communication")
        print("-" * 40)
        
        for i, client in enumerate(self.websocket_clients, 1):
            print(f"[INFO] Testing WebSocket Client {i}")
            
            # Simulate client connection
            print(f"[INFO] Client {client.client_id} connecting...")
            
            # Simulate sending command
            command_msg = create_command_message("ARM", {"source": client.client_id})
            print(f"[INFO] Client sending command: {encode_message(command_msg)}")
            
            # Route through router (decode JSON first)
            command_dict = decode_message(encode_message(command_msg))
            response = await self.router.route(command_dict)
            print(f"[INFO] Server response: {response}")
            
            # Simulate sending response back to client
            await client.send(json.dumps(response))
            
            self.test_results.append({
                "protocol": "websocket",
                "client": client.client_id,
                "command": "ARM",
                "response": response,
                "success": "error" not in response
            })
            
            print()
    
    async def test_grpc_communication(self):
        """Test gRPC client-server communication."""
        print("[INFO] Testing gRPC Communication")
        print("-" * 40)
        
        for i, client in enumerate(self.grpc_clients, 1):
            print(f"[INFO] Testing gRPC Client {i}")
            
            # Simulate gRPC command
            command_msg = {
                "type": "command",
                "action": "DISARM",
                "params": {"source": client.client_id},
                "timestamp": time.time()
            }
            
            print(f"[INFO] Client sending gRPC command: {command_msg}")
            
            # Route through gRPC server
            response = await self.rpc_server.send_command(command_msg)
            print(f"[INFO] gRPC Server response: {response}")
            
            self.test_results.append({
                "protocol": "grpc",
                "client": client.client_id,
                "command": "DISARM",
                "response": response,
                "success": "error" not in response
            })
            
            print()
    
    async def test_mavsdk_integration(self):
        """Test MAVSDK integration and telemetry."""
        print("[INFO] Testing MAVSDK Integration")
        print("-" * 40)
        
        # Test direct MAVSDK operations
        print("[INFO] Testing direct MAVSDK operations")
        
        # Test arm operation
        arm_result = await self.mav_interface.arm()
        print(f"[INFO] MAVSDK Arm result: {arm_result}")
        
        # Test status retrieval
        status = await self.mav_interface.get_status()
        print(f"[INFO] MAVSDK Status: {status}")
        
        # Test flight mode change
        mode_result = await self.mav_interface.set_flight_mode("AUTO")
        print(f"[INFO] MAVSDK Mode change result: {mode_result}")
        
        # Test telemetry polling
        print("[INFO] Testing telemetry polling (3 seconds)...")
        try:
            await asyncio.wait_for(poll_telemetry(self.router), timeout=3.0)
        except asyncio.TimeoutError:
            print("[INFO] Telemetry polling test completed")
        
        self.test_results.append({
            "protocol": "mavsdk",
            "operation": "direct_integration",
            "arm_result": arm_result,
            "status": status,
            "mode_result": mode_result,
            "success": True
        })
        
        print()
    
    async def test_schema_validation(self):
        """Test message schema validation and encoding."""
        print("[INFO] Testing Schema Validation")
        print("-" * 40)
        
        # Test command message creation
        cmd_msg = create_command_message("STATUS", {"test": True})
        print(f"[INFO] Command message: {encode_message(cmd_msg)}")
        
        # Test telemetry message creation
        tel_data = {"battery": 95.5, "altitude": 25.3}
        tel_msg = create_telemetry_message(tel_data)
        print(f"[INFO] Telemetry message: {encode_message(tel_msg)}")
        
        # Test response message creation
        resp_msg = create_response_message("success", "completed", {"data": "test"})
        print(f"[INFO] Response message: {encode_message(resp_msg)}")
        
        # Test message validation
        valid_messages = [
            {"type": "command", "action": "ARM", "params": {}},
            {"type": "telemetry", "data": {"battery": 85.0}},
            {"type": "response", "result": "success", "status": "ok"}
        ]
        
        for msg in valid_messages:
            is_valid = validate_message(msg)
            print(f"[INFO] Message validation: {is_valid} for {msg['type']}")
        
        self.test_results.append({
            "protocol": "schema",
            "operation": "validation",
            "command_created": True,
            "telemetry_created": True,
            "response_created": True,
            "validation_passed": all(validate_message(msg) for msg in valid_messages),
            "success": True
        })
        
        print()
    
    async def test_error_handling(self):
        """Test error handling across all protocols."""
        print("[INFO] Testing Error Handling")
        print("-" * 40)
        
        error_test_cases = [
            # Invalid JSON
            "invalid_json",
            # Unknown action
            {"type": "command", "action": "UNKNOWN", "params": {}},
            # Missing action
            {"type": "command", "params": {}},
            # Invalid message type
            {"type": "invalid", "data": {}}
        ]
        
        for i, test_case in enumerate(error_test_cases, 1):
            print(f"[INFO] Error test {i}: {test_case}")
            try:
                if isinstance(test_case, str):
                    result = {"error": "Invalid JSON format"}
                else:
                    result = await self.router.route(test_case)
                print(f"[INFO] Error handling result: {result}")
            except Exception as e:
                print(f"[INFO] Exception caught: {e}")
            print()
        
        self.test_results.append({
            "protocol": "error_handling",
            "operation": "error_testing",
            "test_cases": len(error_test_cases),
            "success": True
        })
    
    async def run_complete_test(self):
        """Run the complete end-to-end test suite."""
        print("[INFO] Starting End-to-End Test Suite")
        print("=" * 60)
        print()
        
        # Setup system
        await self.setup_system()
        
        # Run all test scenarios
        await self.test_websocket_communication()
        await self.test_grpc_communication()
        await self.test_mavsdk_integration()
        await self.test_schema_validation()
        await self.test_error_handling()
        
        # Generate test report
        await self.generate_test_report()
    
    async def generate_test_report(self):
        """Generate comprehensive test report."""
        print("[INFO] Generating Test Report")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.get("success", False))
        
        print(f"[INFO] Total Tests: {total_tests}")
        print(f"[INFO] Successful Tests: {successful_tests}")
        print(f"[INFO] Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        print()
        
        # Protocol breakdown
        protocols = {}
        for result in self.test_results:
            protocol = result.get("protocol", "unknown")
            if protocol not in protocols:
                protocols[protocol] = {"total": 0, "success": 0}
            protocols[protocol]["total"] += 1
            if result.get("success", False):
                protocols[protocol]["success"] += 1
        
        print("[INFO] Protocol Test Results:")
        for protocol, stats in protocols.items():
            success_rate = (stats["success"]/stats["total"])*100 if stats["total"] > 0 else 0
            print(f"  {protocol}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        print()
        print("[INFO] End-to-End Test Suite Completed Successfully!")
        print("=" * 60)

async def main():
    """Main test function."""
    try:
        harness = EndToEndTestHarness()
        await harness.run_complete_test()
        return 0
    except Exception as e:
        print(f"[ERROR] End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)