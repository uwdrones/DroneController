#!/usr/bin/env python3
"""
MAVSDK interface wrapper for drone control.
Connects to Pixhawk via MAVSDK for state queries and optional command mirroring.
Uses MAVLink port 14540 for flight controller communication.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DroneStatus:
    """Data class for drone status information."""
    armed: bool
    flight_mode: str
    battery_level: float
    gps_lat: float
    gps_lon: float
    altitude: float
    heading: float
    ground_speed: float

class MAVInterface:
    """Interface to MAVSDK for drone control operations."""
    
    def __init__(self):
        self.connected = False
        self.drone = None
        
    async def connect(self):
        """Connect to the flight controller via MAVSDK."""
        logger.info("Connecting to flight controller via MAVSDK...")
        
        try:
            from mavsdk import System
            self.drone = System()
            await self.drone.connect(system_address="udp://:14540")
            
            # Wait for system to be ready
            await asyncio.sleep(2)
            
            self.connected = True
            logger.info("Connected to flight controller via MAVSDK")
            
        except ImportError:
            logger.warning("MAVSDK not available, using mock mode")
            self.connected = True
        except Exception as e:
            logger.error(f"Failed to connect to flight controller: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the flight controller."""
        logger.info("Disconnecting from flight controller...")
        self.connected = False
        if self.drone:
            await self.drone.close()
        logger.info("Disconnected from flight controller")
    
    async def arm(self) -> bool:
        """Arm the drone motors (optional - QGC may handle this)."""
        if not self.connected or not self.drone:
            raise RuntimeError("Not connected to flight controller")
        
        logger.info("Arming drone via MAVSDK...")
        try:
            await self.drone.action.arm()
            logger.info("Drone armed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to arm drone: {e}")
            return False
    
    async def disarm(self) -> bool:
        """Disarm the drone motors (optional - QGC may handle this)."""
        if not self.connected or not self.drone:
            raise RuntimeError("Not connected to flight controller")
        
        logger.info("Disarming drone via MAVSDK...")
        try:
            await self.drone.action.disarm()
            logger.info("Drone disarmed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to disarm drone: {e}")
            return False
    
    async def set_flight_mode(self, mode: str) -> bool:
        """Set the flight mode (optional - QGC may handle this)."""
        if not self.connected or not self.drone:
            raise RuntimeError("Not connected to flight controller")
        
        logger.info(f"Setting flight mode to: {mode}")
        try:
            await self.drone.action.set_flight_mode(mode)
            logger.info(f"Flight mode set to: {mode}")
            return True
        except Exception as e:
            logger.error(f"Failed to set flight mode: {e}")
            return False
    
    async def get_status(self) -> DroneStatus:
        """Get current drone status via MAVSDK telemetry."""
        if not self.connected:
            raise RuntimeError("Not connected to flight controller")
        
        if not self.drone:
            # Fallback to mock data if MAVSDK unavailable
            return DroneStatus(
                armed=False,
                flight_mode="UNKNOWN",
                battery_level=0.0,
                gps_lat=0.0,
                gps_lon=0.0,
                altitude=0.0,
                heading=0.0,
                ground_speed=0.0
            )
        
        try:
            # Fetch telemetry data
            health = await self.drone.telemetry.health()
            position = await self.drone.telemetry.position()
            battery = await self.drone.telemetry.battery()
            flight_mode = await self.drone.telemetry.flight_mode()
            
            return DroneStatus(
                armed=health.is_armable,
                flight_mode=flight_mode.name,
                battery_level=battery.remaining_percent * 100,
                gps_lat=position.latitude_deg,
                gps_lon=position.longitude_deg,
                altitude=position.absolute_altitude_m,
                heading=position.heading_deg,
                ground_speed=0.0  # TODO: Add velocity telemetry
            )
            
        except Exception as e:
            logger.error(f"Failed to get drone status: {e}")
            # Return safe defaults on error
            return DroneStatus(
                armed=False,
                flight_mode="ERROR",
                battery_level=0.0,
                gps_lat=0.0,
                gps_lon=0.0,
                altitude=0.0,
                heading=0.0,
                ground_speed=0.0
            )
    
    def is_connected(self) -> bool:
        """Check if connected to flight controller."""
        return self.connected 