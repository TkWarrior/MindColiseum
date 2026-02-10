import io
import os
import wave
import json
import struct
import urllib.request
from typing import Generator    
from pathlib import Path

# Directory to store downloaded voice models
MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Piper voice models for different agents
# Format: {agent: (model_name, description)}
AGENT_VOICES = {
    "pro": ("en_US-lessac-medium", "Male, confident American"),
    "con": ("en_GB-alba-medium", "Female, articulate British"),
    "judge": ("en_US-ryan-medium", "Male, authoritative American"),
    "summary": ("en_US-amy-medium", "Female, clear narrator"),
}

# Base URL for Piper voice model downloads
PIPER_MODELS_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0"

# Cached PiperVoice instances
_voice_cache = {}


def _download_file(url: str, dest: Path) -> None:
    """Download a file if it doesn't already exist."""
    if dest.exists():
        return
    print(f"  Downloading {dest.name}...")
    urllib.request.urlretrieve(url, str(dest))
    print(f"  Downloaded {dest.name}")


def _ensure_model(model_name: str) -> Path:
    """
    Ensure the voice model files are downloaded.
    Returns the path to the .onnx model file.
    """
    # Parse language and name parts: en_US-lessac-medium
    parts = model_name.split("-")
    lang_code = parts[0]           # en_US
    lang = lang_code.split("_")[0] # en
    voice_name = parts[1]          # lessac
    quality = parts[2]             # medium

    onnx_path = MODELS_DIR / f"{model_name}.onnx"
    json_path = MODELS_DIR / f"{model_name}.onnx.json"

    # Download model files from HuggingFace
    # URL format: .../en/en_US/lessac/medium/en_US-lessac-medium.onnx
    base_url = f"{PIPER_MODELS_URL}/{lang}/{lang_code}/{voice_name}/{quality}"
    _download_file(f"{base_url}/{model_name}.onnx", onnx_path)
    _download_file(f"{base_url}/{model_name}.onnx.json", json_path)

    return onnx_path


def get_voice(agent: str):
    """Get or load a PiperVoice for the given agent."""
    from piper import PiperVoice

    agent = agent.lower()
    if agent in _voice_cache:
        return _voice_cache[agent]

    voice_info = AGENT_VOICES.get(agent, AGENT_VOICES["pro"])
    model_name = voice_info[0]

    print(f"Loading Piper voice for '{agent}': {model_name} ({voice_info[1]})")
    model_path = _ensure_model(model_name)

    voice = PiperVoice.load(str(model_path))
    _voice_cache[agent] = voice
    print(f"Voice loaded for '{agent}'!")
    return voice


def generate_audio_bytes(text: str, agent: str = "pro") -> bytes:
    """
    Generate WAV audio bytes from text using the specified agent's voice.

    Args:
        text: The text to convert to speech
        agent: The agent type (pro, con, judge, summary)

    Returns:
        WAV audio as bytes
    """
    voice = get_voice(agent)

    # synthesize_wav() sets WAV headers from first audio chunk and writes frames
    buffer = io.BytesIO()
    wav_file = wave.open(buffer, "wb")
    voice.synthesize_wav(text, wav_file)
    wav_file.close()

    buffer.seek(0)
    return buffer.read()


def stream_audio_chunks(
    text: str, agent: str = "pro", chunk_size: int = 4096
) -> Generator[bytes, None, None]:
    """
    Stream audio in chunks for FastAPI StreamingResponse.

    Args:
        text: The text to convert to speech
        agent: The agent type (pro, con, judge, summary)
        chunk_size: Size of each audio chunk in bytes

    Yields:
        Audio chunks as bytes
    """
    audio_bytes = generate_audio_bytes(text, agent)

    for i in range(0, len(audio_bytes), chunk_size):
        yield audio_bytes[i : i + chunk_size]
