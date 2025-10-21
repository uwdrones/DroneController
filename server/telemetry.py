#!/usr/bin/env python3
"""
Telemetry streaming module for drone status data.
Handles JSON formatting and streaming to WebSocket clients.
Processes MAVSDK telemetry data and formats for real-time streaming.
"""

import asyncio
import json
import logging
import random
import time
from typing import Dict, Any
from datetime import datetime
from mav_interface import MAVInterface, DroneStatus

logger = logging.getLogger(__name__)

class TelemetryStreamer:
    """Handles telemetry data streaming to WebSocket clients."""
    
    def __init__(self, mav_interface: MAVInterface):
        self.mav_interface = mav_interface
        self.clients = set()
        self.streaming = False
    
    def add_client(self, websocket):
        """Add a new WebSocket client to the stream."""
        self.clients.add(websocket)
        logger.info(f"Added telemetry client. Total clients: {len(self.clients)}")
    
    def remove_client(self, websocket):
        """Remove a WebSocket client from the stream."""
        self.clients.discard(websocket)
        logger.info(f"Removed telemetry client. Total clients: {len(self.clients)}")
    
    def format_telemetry_data(self, status: DroneStatus) -> Dict[str, Any]:
        """Format drone status into enriched JSON-serializable dictionary."""
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "armed": status.armed,
            "flight_mode": status.flight_mode,
            "battery": {
                "level": round(status.battery_level, 2),
                "unit": "percent"
            },
            "position": {
                "latitude": round(status.gps_lat, 6),
                "longitude": round(status.gps_lon, 6),
                "altitude": round(status.altitude, 2),
                "unit": "meters"
            },
            "attitude": {
                "heading": round(status.heading, 1),
                "unit": "degrees"
            },
            "velocity": {
                "ground_speed": round(status.ground_speed, 2),
                "unit": "m/s"
            },
            "connection": {
                "connected": self.mav_interface.is_connected(),
                "status": "connected" if self.mav_interface.is_connected() else "disconnected"
            },
            "source": "mavsdk_telemetry"
        }
    
    async def telemetry_stream(self, websocket):
        """Stream enriched telemetry data to a specific WebSocket client."""
        self.add_client(websocket)
        
        try:
            while self.mav_interface.is_connected():
                try:
                    # Get current drone status via MAVSDK
                    status = await self.mav_interface.get_status()
                    
                    # Format as enriched JSON
                    telemetry_data = self.format_telemetry_data(status)
                    json_data = json.dumps(telemetry_data, separators=(',', ':'))
                    
                    # Send to client
                    await websocket.send(json_data)
                    
                    # Wait before next update (1 second interval)
                    await asyncio.sleep(1.0)
                    
                except Exception as e:
                    logger.error(f"Error streaming telemetry: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self.remove_client(websocket)
    
    async def broadcast_telemetry(self):
        """Broadcast telemetry to all connected clients."""
        if not self.clients:
            return
        
        try:
            # Get current drone status via MAVSDK
            status = await self.mav_interface.get_status()
            telemetry_data = self.format_telemetry_data(status)
            json_data = json.dumps(telemetry_data, separators=(',', ':'))
            
            # Send to all clients
            disconnected_clients = set()
            for client in self.clients:
                try:
                    await client.send(json_data)
                except Exception as e:
                    logger.warning(f"Failed to send to client: {e}")
                    disconnected_clients.add(client)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                self.remove_client(client)
                
        except Exception as e:
            logger.error(f"Error broadcasting telemetry: {e}")
    
    def get_client_count(self) -> int:
        """Get the number of connected clients."""
        return len(self.clients)

async def poll_telemetry(router):
    """Simulate periodic telemetry polling and broadcast via router."""
    logger.info("[ROUTER] Starting telemetry polling...")
    
    while True:
        try:
            # Generate mock telemetry data
            telemetry_data = {
                "battery": round(random.uniform(85.0, 100.0), 1),
                "altitude": round(random.uniform(0.0, 50.0), 1),
                "velocity": round(random.uniform(0.0, 15.0), 1),
                "armed": random.choice([True, False]),
                "flight_mode": random.choice(["STABILIZED", "AUTO", "MANUAL"]),
                "gps_lat": round(random.uniform(37.7, 37.8), 6),
                "gps_lon": round(random.uniform(-122.5, -122.4), 6),
                "heading": round(random.uniform(0.0, 360.0), 1)
            }
            
            # Create telemetry message
            telemetry_message = {
                "type": "telemetry",
                "data": telemetry_data,
                "timestamp": time.time()
            }
            
            # Broadcast via router
            print(f"[ROUTER] Broadcasting telemetry: {json.dumps(telemetry_message, indent=2)}")
            await router.route(telemetry_message)
            
            # Wait 1 second before next poll
            await asyncio.sleep(1.0)
            
        except Exception as e:
            logger.error(f"[ROUTER] Error in telemetry polling: {e}")
            await asyncio.sleep(1.0) 