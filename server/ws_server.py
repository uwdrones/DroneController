#!/usr/bin/env python3
"""
WebSocket server for telemetry streaming.
Handles client connections and streams drone status data.
"""

import asyncio
import logging
import websockets
from typing import Optional
from mav_interface import MAVInterface
from telemetry import TelemetryStreamer

logger = logging.getLogger(__name__)

class WebSocketServer:
    """WebSocket server for telemetry streaming."""
    
    def __init__(self, mav_interface: MAVInterface, host: str = "0.0.0.0", port: int = 8765):
        self.mav_interface = mav_interface
        self.host = host
        self.port = port
        self.telemetry_streamer = TelemetryStreamer(mav_interface)
        self.server: Optional[websockets.WebSocketServer] = None
        self.running = False
    
    async def start(self):
        """Start the WebSocket server."""
        logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        
        try:
            self.server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            self.running = True
            
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            
            # Keep the server running
            await self.server.wait_closed()
            
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            raise
    
    async def stop(self):
        """Stop the WebSocket server."""
        logger.info("Stopping WebSocket server...")
        self.running = False
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        logger.info("WebSocket server stopped")
    
    async def handle_client(self, websocket):
        """Handle a new WebSocket client connection."""
        client_address = websocket.remote_address
        logger.info(f"New WebSocket client connected from {client_address}")
        
        try:
            # Send welcome message
            welcome_msg = {
                "type": "connection",
                "status": "connected",
                "message": "Telemetry stream started"
            }
            await websocket.send(str(welcome_msg))
            
            # Start telemetry streaming
            await self.telemetry_streamer.telemetry_stream(websocket)
            
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket client {client_address} disconnected normally")
        except Exception as e:
            logger.error(f"Error handling WebSocket client {client_address}: {e}")
        finally:
            logger.info(f"WebSocket client {client_address} disconnected")
    
    def get_client_count(self) -> int:
        """Get the number of connected WebSocket clients."""
        return self.telemetry_streamer.get_client_count()
    
    def is_running(self) -> bool:
        """Check if the WebSocket server is running."""
        return self.running 