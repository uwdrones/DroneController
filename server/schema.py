#!/usr/bin/env python3
"""
Message schema definitions for unified message format.
Defines dataclasses and validation helpers for WebSocket and gRPC interfaces.
Provides consistent message structure across all communication channels.
"""

import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Union

@dataclass
class CommandMessage:
    """Command message structure for drone control actions."""
    type: str
    action: str
    params: dict
    timestamp: float
    
    def __post_init__(self):
        """Validate command message structure."""
        if self.type != "command":
            raise ValueError("Command message type must be 'command'")
        if not self.action:
            raise ValueError("Command message must have an action")
        if not isinstance(self.params, dict):
            raise ValueError("Command message params must be a dictionary")

@dataclass
class TelemetryMessage:
    """Telemetry message structure for drone status data."""
    type: str
    data: dict
    timestamp: float
    
    def __post_init__(self):
        """Validate telemetry message structure."""
        if self.type != "telemetry":
            raise ValueError("Telemetry message type must be 'telemetry'")
        if not isinstance(self.data, dict):
            raise ValueError("Telemetry message data must be a dictionary")

@dataclass
class ResponseMessage:
    """Response message structure for command results."""
    type: str
    result: str
    status: str
    data: Optional[dict] = None
    timestamp: float = None
    
    def __post_init__(self):
        """Validate response message structure."""
        if self.type != "response":
            raise ValueError("Response message type must be 'response'")
        if not self.result:
            raise ValueError("Response message must have a result")
        if not self.status:
            raise ValueError("Response message must have a status")
        if self.timestamp is None:
            self.timestamp = time.time()

def encode_message(obj: Union[CommandMessage, TelemetryMessage, ResponseMessage, dict]) -> str:
    """Encode a message object to JSON string."""
    if isinstance(obj, dict):
        # If it's already a dict, just encode it
        return json.dumps(obj, separators=(',', ':'))
    else:
        # Convert dataclass to dict and encode
        return json.dumps(asdict(obj), separators=(',', ':'))

def decode_message(json_str: str) -> dict:
    """Decode a JSON string to message dictionary."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")

def create_command_message(action: str, params: dict = None) -> CommandMessage:
    """Create a command message with current timestamp."""
    return CommandMessage(
        type="command",
        action=action,
        params=params or {},
        timestamp=time.time()
    )

def create_telemetry_message(data: dict) -> TelemetryMessage:
    """Create a telemetry message with current timestamp."""
    return TelemetryMessage(
        type="telemetry",
        data=data,
        timestamp=time.time()
    )

def create_response_message(result: str, status: str, data: dict = None) -> ResponseMessage:
    """Create a response message with current timestamp."""
    return ResponseMessage(
        type="response",
        result=result,
        status=status,
        data=data,
        timestamp=time.time()
    )

def validate_message(message_dict: dict) -> bool:
    """Validate that a message dictionary has required fields."""
    if not isinstance(message_dict, dict):
        return False
    
    message_type = message_dict.get("type")
    if message_type not in ["command", "telemetry", "response"]:
        return False
    
    if message_type == "command":
        return "action" in message_dict and "params" in message_dict
    elif message_type == "telemetry":
        return "data" in message_dict
    elif message_type == "response":
        return "result" in message_dict and "status" in message_dict
    
    return False
