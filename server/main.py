#!/usr/bin/env python3
"""
Main supervisor script for the drone control server.
Runs MAVSDK connection, gRPC server, and WebSocket server concurrently.
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

# Import local modules
from mav_interface import MAVInterface
from rpc_server import RPCServer
from ws_server import WebSocketServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DroneServer:
    def __init__(self):
        self.mav_interface: Optional[MAVInterface] = None
        self.rpc_server: Optional[RPCServer] = None
        self.ws_server: Optional[WebSocketServer] = None
        self.running = False
        
    async def start(self):
        """Start all services concurrently."""
        logger.info("Starting drone control server...")
        
        try:
            # Initialize components
            self.mav_interface = MAVInterface()
            self.rpc_server = RPCServer(self.mav_interface)
            self.ws_server = WebSocketServer(self.mav_interface)
            
            # Start all services concurrently
            await asyncio.gather(
                self.mav_interface.connect(),
                self.rpc_server.start(),
                self.ws_server.start()
            )
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            await self.shutdown()
            sys.exit(1)
    
    async def shutdown(self):
        """Gracefully shutdown all services."""
        logger.info("Shutting down drone control server...")
        self.running = False
        
        if self.ws_server:
            await self.ws_server.stop()
        if self.rpc_server:
            await self.rpc_server.stop()
        if self.mav_interface:
            await self.mav_interface.disconnect()
        
        logger.info("Server shutdown complete.")

async def main():
    """Main entry point."""
    server = DroneServer()
    
    # Handle graceful shutdown
    def signal_handler():
        logger.info("Received shutdown signal")
        asyncio.create_task(server.shutdown())
    
    # Register signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda s, f: signal_handler())
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        await server.shutdown()

if __name__ == "__main__":
    asyncio.run(main()) 