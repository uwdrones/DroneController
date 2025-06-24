#!/usr/bin/env python3
"""
Test script for WebSocket telemetry streaming.
Tests the WebSocket server and telemetry streaming functionality.
"""

import asyncio
import json
import sys
import os
import websockets
import logging

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mav_interface import MAVInterface
from ws_server import WebSocketServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_client():
    """Test WebSocket client connection and telemetry reception."""
    print("🌐 Testing WebSocket Client Connection")
    print("=" * 50)
    
    try:
        # Connect to WebSocket server
        uri = "ws://localhost:8765"
        print(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket server")
            
            # Receive welcome message
            welcome_msg = await websocket.recv()
            print(f"📨 Welcome message: {welcome_msg}")
            
            # Receive telemetry data for 10 seconds
            print("\n📡 Receiving telemetry data...")
            start_time = asyncio.get_event_loop().time()
            
            message_count = 0
            while asyncio.get_event_loop().time() - start_time < 10:
                try:
                    # Wait for telemetry message with timeout
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    message_count += 1
                    
                    # Parse JSON telemetry data
                    telemetry = json.loads(message)
                    
                    print(f"   Message {message_count}:")
                    print(f"     Timestamp: {telemetry.get('timestamp', 'N/A')}")
                    print(f"     Armed: {telemetry.get('armed', 'N/A')}")
                    print(f"     Flight Mode: {telemetry.get('flight_mode', 'N/A')}")
                    print(f"     Battery: {telemetry.get('battery', {}).get('level', 'N/A')}%")
                    print(f"     Position: {telemetry.get('position', {}).get('latitude', 'N/A')}, "
                          f"{telemetry.get('position', {}).get('longitude', 'N/A')}")
                    print(f"     Altitude: {telemetry.get('position', {}).get('altitude', 'N/A')}m")
                    print()
                    
                except asyncio.TimeoutError:
                    print("   ⏰ Timeout waiting for telemetry data")
                    break
                except json.JSONDecodeError as e:
                    print(f"   ❌ Failed to parse JSON: {e}")
                    break
            
            print(f"✅ Received {message_count} telemetry messages")
            
    except ConnectionRefusedError:
        print("❌ Failed to connect to WebSocket server. Is it running?")
        return False
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False
    
    return True

async def test_websocket_server():
    """Test WebSocket server functionality."""
    print("🖥️ Testing WebSocket Server")
    print("=" * 50)
    
    # Create MAV interface and WebSocket server
    mav = MAVInterface()
    ws_server = WebSocketServer(mav)
    
    try:
        # Start MAV interface
        print("1. Starting MAV interface...")
        await mav.connect()
        print("   ✅ MAV interface connected")
        
        # Start WebSocket server in background
        print("2. Starting WebSocket server...")
        server_task = asyncio.create_task(ws_server.start())
        
        # Give server time to start
        await asyncio.sleep(1)
        
        if ws_server.is_running():
            print("   ✅ WebSocket server is running")
        else:
            print("   ❌ WebSocket server failed to start")
            return False
        
        # Test client connection
        print("3. Testing client connection...")
        client_result = await test_websocket_client()
        
        if client_result:
            print("   ✅ WebSocket client test passed")
        else:
            print("   ❌ WebSocket client test failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ WebSocket server test failed: {e}")
        return False
    
    finally:
        # Cleanup
        print("4. Cleaning up...")
        await ws_server.stop()
        await mav.disconnect()
        print("   ✅ Cleanup completed")

async def main():
    """Main test function."""
    print("🌐 WebSocket Telemetry Test")
    print("=" * 50)
    
    # Run WebSocket server test
    server_test_passed = await test_websocket_server()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   WebSocket Server Test: {'✅ PASSED' if server_test_passed else '❌ FAILED'}")
    
    if server_test_passed:
        print("\n🎉 WebSocket test passed! Telemetry streaming is working correctly.")
        return 0
    else:
        print("\n❌ WebSocket test failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 