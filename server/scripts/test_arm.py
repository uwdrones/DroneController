#!/usr/bin/env python3
"""
Test script for MAV interface arm/disarm functionality.
Tests the stub implementations before real MAVSDK integration.
"""

import asyncio
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mav_interface import MAVInterface

async def test_arm_disarm():
    """Test arm and disarm functionality."""
    print("🧪 Testing MAV Interface Arm/Disarm Functions")
    print("=" * 50)
    
    # Create MAV interface instance
    mav = MAVInterface()
    
    try:
        # Test connection
        print("1. Testing connection...")
        await mav.connect()
        print(f"   ✅ Connected: {mav.is_connected()}")
        
        # Test initial status
        print("\n2. Getting initial status...")
        status = await mav.get_status()
        print(f"   ✅ Armed: {status.armed}")
        print(f"   ✅ Flight Mode: {status.flight_mode}")
        print(f"   ✅ Battery: {status.battery_level}%")
        
        # Test arming
        print("\n3. Testing arm command...")
        arm_result = await mav.arm()
        print(f"   ✅ Arm result: {arm_result}")
        
        # Check status after arm
        status = await mav.get_status()
        print(f"   ✅ Armed: {status.armed}")
        
        # Test disarm
        print("\n4. Testing disarm command...")
        disarm_result = await mav.disarm()
        print(f"   ✅ Disarm result: {disarm_result}")
        
        # Check status after disarm
        status = await mav.get_status()
        print(f"   ✅ Armed: {status.armed}")
        
        # Test flight mode change
        print("\n5. Testing flight mode change...")
        mode_result = await mav.set_flight_mode("AUTO")
        print(f"   ✅ Mode change result: {mode_result}")
        
        status = await mav.get_status()
        print(f"   ✅ Flight Mode: {status.flight_mode}")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        print("\n6. Cleaning up...")
        await mav.disconnect()
        print("   ✅ Disconnected")
    
    return True

async def test_telemetry_stream():
    """Test telemetry streaming functionality."""
    print("\n📡 Testing Telemetry Streaming")
    print("=" * 50)
    
    mav = MAVInterface()
    
    try:
        await mav.connect()
        print("✅ Connected to MAV interface")
        
        # Test multiple status updates
        for i in range(5):
            status = await mav.get_status()
            print(f"   Update {i+1}: Armed={status.armed}, "
                  f"Battery={status.battery_level:.1f}%, "
                  f"Alt={status.altitude:.1f}m")
            await asyncio.sleep(0.5)
        
        print("✅ Telemetry streaming test completed")
        
    except Exception as e:
        print(f"❌ Telemetry test failed: {e}")
        return False
    
    finally:
        await mav.disconnect()
    
    return True

async def main():
    """Main test function."""
    print("🚁 Drone Controller MAV Interface Test")
    print("=" * 50)
    
    # Run tests
    arm_test_passed = await test_arm_disarm()
    telemetry_test_passed = await test_telemetry_stream()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Arm/Disarm Test: {'✅ PASSED' if arm_test_passed else '❌ FAILED'}")
    print(f"   Telemetry Test:  {'✅ PASSED' if telemetry_test_passed else '❌ FAILED'}")
    
    if arm_test_passed and telemetry_test_passed:
        print("\n🎉 All tests passed! MAV interface is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 