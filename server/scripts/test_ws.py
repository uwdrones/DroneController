#!/usr/bin/env python3
"""
Manual test script for WebSocket telemetry streaming.
Connects to WebSocket server and prints received telemetry messages.
Tests WebSocket server on port 8765.
"""

import asyncio
import json
import sys
import os
import websockets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_telemetry():
    """Test WebSocket telemetry streaming by connecting and receiving messages."""
    print("[INFO] Manual WebSocket Telemetry Test")
    print("=" * 50)
    
    try:
        # Connect to WebSocket server
        uri = "ws://localhost:8765"
        print(f"[INFO] Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("[INFO] Connected to WebSocket server")
            
            # Receive welcome message
            welcome_msg = await websocket.recv()
            print(f"[INFO] Welcome: {welcome_msg}")
            
            # Receive 5 telemetry messages
            print("\n[INFO] Receiving telemetry data...")
            for i in range(5):
                try:
                    # Wait for telemetry message
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    
                    # Parse JSON telemetry data
                    telemetry = json.loads(message)
                    
                    print(f"\n[INFO] Message {i+1}:")
                    print(f"   Timestamp: {telemetry.get('timestamp', 'N/A')}")
                    print(f"   Armed: {telemetry.get('armed', 'N/A')}")
                    print(f"   Flight Mode: {telemetry.get('flight_mode', 'N/A')}")
                    print(f"   Battery: {telemetry.get('battery', {}).get('level', 'N/A')}%")
                    print(f"   Position: {telemetry.get('position', {}).get('latitude', 'N/A')}, "
                          f"{telemetry.get('position', {}).get('longitude', 'N/A')}")
                    print(f"   Altitude: {telemetry.get('position', {}).get('altitude', 'N/A')}m")
                    print(f"   Heading: {telemetry.get('attitude', {}).get('heading', 'N/A')}°")
                    print(f"   Source: {telemetry.get('source', 'N/A')}")
                    
                except asyncio.TimeoutError:
                    print(f"   [WARN] Timeout waiting for message {i+1}")
                    break
                except json.JSONDecodeError as e:
                    print(f"   [ERROR] Failed to parse JSON: {e}")
                    break
            
            print(f"\n[INFO] Received {min(5, i+1)} telemetry messages")
            
    except ConnectionRefusedError:
        print("[ERROR] Failed to connect to WebSocket server. Is it running?")
        print("   [INFO] Start the server with: python main.py")
        return False
    except Exception as e:
        print(f"[ERROR] WebSocket test failed: {e}")
        return False
    
    return True

async def main():
    """Main test function."""
    success = await test_websocket_telemetry()
    
    if success:
        print("\n[INFO] WebSocket telemetry test completed successfully!")
        return 0
    else:
        print("\n[ERROR] WebSocket telemetry test failed.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 