#!/usr/bin/env python3
"""
Message router for dynamic JSON message routing.
Routes incoming messages from WebSocket, gRPC, or internal modules to registered handlers.
Uses action-based routing with ROUTE_TABLE mapping.
"""

import logging
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger(__name__)

class Router:
    """Simple router for dynamic message routing to registered handlers."""
    
    def __init__(self):
        self.route_table: Dict[str, Callable] = {}
    
    def register(self, action: str, handler: Callable) -> None:
        """Register a handler function for a specific action."""
        self.route_table[action] = handler
        logger.info(f"[ROUTER] Registered handler for action: {action}")
    
    async def route(self, message_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Route a message to the appropriate handler based on action."""
        if not isinstance(message_dict, dict):
            logger.error("[ROUTER] Invalid message format - expected dictionary")
            return {"error": "Invalid message format"}
        
        # Handle different message types
        message_type = message_dict.get("type", "command")
        
        if message_type == "command":
            action = message_dict.get("action")
            if not action:
                logger.error("[ROUTER] No action specified in command message")
                return {"error": "No action specified"}
            params = message_dict.get("params", {})
        elif message_type == "telemetry":
            action = "TELEMETRY"
            params = {"data": message_dict.get("data", {})}
        else:
            logger.error(f"[ROUTER] Unknown message type: {message_type}")
            return {"error": f"Unknown message type: {message_type}"}
        
        if action not in self.route_table:
            logger.warning(f"[ROUTER] Unknown action: {action}")
            return {"error": f"Unknown action: {action}"}
        
        try:
            logger.info(f"[ROUTER] Routing {message_type} '{action}' to handler")
            result = await self.route_table[action](params)
            logger.info(f"[ROUTER] Handler for '{action}' completed successfully")
            return result
        except Exception as e:
            logger.error(f"[ROUTER] Error in handler for action '{action}': {e}")
            return {"error": f"Handler error: {str(e)}"}
    
    def get_registered_actions(self) -> list:
        """Get list of all registered actions."""
        return list(self.route_table.keys())
    
    def is_registered(self, action: str) -> bool:
        """Check if an action is registered."""
        return action in self.route_table
