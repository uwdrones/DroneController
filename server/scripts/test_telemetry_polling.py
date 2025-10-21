#!/usr/bin/env python3
"""
Test script for telemetry polling and schema validation.
Demonstrates periodic telemetry broadcasting via router.
Tests schema message encoding/decoding functionality.
"""

import asyncio
import sys
import os
import logging

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from router import Router
from handlers import register_all
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

async def test_telemetry_polling():
    """Test telemetry polling functionality."""
    print("[INFO] Testing Telemetry Polling System")
    print("=" * 50)
    
    # Create router and register handlers
    router = Router()
    register_all(router)
    
    print(f"[INFO] Registered actions: {router.get_registered_actions()}")
    print()
    
    # Test schema message creation
    print("[INFO] Testing Schema Message Creation")
    print("-" * 30)
    
    # Create command message
    cmd_msg = create_command_message("STATUS", {"source": "test"})
    print(f"[INFO] Command message: {encode_message(cmd_msg)}")
    
    # Create telemetry message
    telemetry_data = {"battery": 93.4, "altitude": 12.3}
    tel_msg = create_telemetry_message(telemetry_data)
    print(f"[INFO] Telemetry message: {encode_message(tel_msg)}")
    
    # Create response message
    resp_msg = create_response_message("success", "completed", {"result": "ok"})
    print(f"[INFO] Response message: {encode_message(resp_msg)}")
    
    print()
    print("[INFO] Testing Message Validation")
    print("-" * 30)
    
    # Test message validation
    valid_cmd = {"type": "command", "action": "ARM", "params": {}}
    valid_tel = {"type": "telemetry", "data": {"battery": 85.0}}
    invalid_msg = {"type": "unknown", "data": {}}
    
    print(f"[INFO] Valid command: {validate_message(valid_cmd)}")
    print(f"[INFO] Valid telemetry: {validate_message(valid_tel)}")
    print(f"[INFO] Invalid message: {validate_message(invalid_msg)}")
    
    print()
    print("[INFO] Testing Router with Schema Messages")
    print("-" * 30)
    
    # Test command routing
    cmd_result = await router.route(valid_cmd)
    print(f"[INFO] Command result: {cmd_result}")
    
    # Test telemetry routing
    tel_result = await router.route(valid_tel)
    print(f"[INFO] Telemetry result: {tel_result}")
    
    print()
    print("[INFO] Starting Telemetry Polling (5 seconds)...")
    print("-" * 30)
    
    # Start telemetry polling for 5 seconds
    try:
        await asyncio.wait_for(poll_telemetry(router), timeout=5.0)
    except asyncio.TimeoutError:
        print("[INFO] Telemetry polling test completed (timeout reached)")
    
    print("[INFO] Telemetry polling test completed successfully!")

async def main():
    """Main test function."""
    try:
        await test_telemetry_polling()
        return 0
    except Exception as e:
        print(f"[ERROR] Telemetry polling test failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
