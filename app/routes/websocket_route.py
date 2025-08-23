from fastapi import APIRouter, WebSocket
import logging
import base64
import json

logging.basicConfig(level=logging.INFO)
router = APIRouter()

# The /ws/audio endpoint is not needed and will be removed.
