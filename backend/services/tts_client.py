"""
TTS Client Service
===================
HTTP client that calls the TTS microservice (localhost:8001) to generate 
speech audio from text. This keeps TTS concerns isolated from the main backend.

Data Flow:
    debate_stream_service.py → tts_client.py → TTS miniservice (:8001)
    
The TTS miniservice runs Piper TTS and returns WAV audio bytes.
Each debate agent (pro, con, judge, summary) maps to a distinct voice.
"""

import base64
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# TTS microservice base URL — runs on port 8001
TTS_SERVICE_URL = "http://localhost:8001"

# Map LangGraph node names → TTS agent voice names
# LangGraph uses "pro_agent", "conn_agent", etc.
# TTS service expects "pro", "con", "judge", "summary"
NODE_TO_VOICE = {
    "pro_agent": "pro",
    "conn_agent": "con",
    "judge_agent": "judge",
    "summary_agent": "summary",
}


async def get_audio_bytes(text: str, agent_node: str) -> Optional[bytes]:
    """
    Call TTS miniservice to generate WAV audio from text.
    
    Args:
        text: The argument/comment text to convert to speech.
        agent_node: LangGraph node name (e.g., "pro_agent").
        
    Returns:
        WAV audio as raw bytes, or None if TTS service is unavailable.
        
    Note:
        Returns None (instead of raising) if TTS is down, so the debate
        can continue streaming text even without audio.
    """
    voice = NODE_TO_VOICE.get(agent_node, "pro")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{TTS_SERVICE_URL}/stream",
                params={"text": text, "agent": voice},
                timeout=60.0,  # TTS generation can take time for long text
            )
            response.raise_for_status()
            return response.content
            
    except httpx.ConnectError:
        logger.warning("TTS service is not running on %s", TTS_SERVICE_URL)
        return None
    except httpx.TimeoutException:
        logger.warning("TTS service timed out for agent=%s", voice)
        return None
    except Exception as e:
        logger.error("TTS service error: %s", str(e))
        return None


async def get_audio_base64(text: str, agent_node: str) -> Optional[str]:
    """
    Generate audio and return as base64-encoded string for SSE transport.
    
    Base64 encoding is needed because SSE only supports text data.
    The frontend decodes this back to binary WAV for playback.
    
    Args:
        text: The argument/comment text to convert to speech.
        agent_node: LangGraph node name (e.g., "pro_agent").
        
    Returns:
        Base64-encoded WAV audio string, or None if TTS unavailable.
    """
    audio_bytes = await get_audio_bytes(text, agent_node)
    if audio_bytes:
        return base64.b64encode(audio_bytes).decode("utf-8")
    return None
