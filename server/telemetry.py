#!/usr/bin/env python3
"""
Telemetry streaming module for drone status data.
Handles JSON formatting and streaming to WebSocket clients.
"""

import asyncio
import json
import logging
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
        """Format drone status into JSON-serializable dictionary."""
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
            }
        }
    
    async def telemetry_stream(self, websocket):
        """Stream telemetry data to a specific WebSocket client."""
        self.add_client(websocket)
        
        try:
            while self.mav_interface.is_connected():
                try:
                    # Get current drone status
                    status = await self.mav_interface.get_status()
                    
                    # Format as JSON
                    telemetry_data = self.format_telemetry_data(status)
                    json_data = json.dumps(telemetry_data, separators=(',', ':'))
                    
                    # Send to client
                    await websocket.send(json_data)
                    
                    # Wait before next update
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
            # Get current drone status
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