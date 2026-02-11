from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import tts_service

app = FastAPI(
    title="MindColiseum TTS Service",
    description="Text-to-Speech microservice using Piper TTS for AI debate arguments",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_AGENTS = {"pro", "con", "judge", "summary"}


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "service": "MindColiseum TTS (Piper)",
        "status": "running",
        "docs": "/docs",
        "voices": {
            agent: info[1]
            for agent, info in tts_service.AGENT_VOICES.items()
        },
    }


@app.get("/health")
def health_check():
    """Health check."""
    return {"status": "healthy"}


@app.get("/stream")
def stream_tts(
    text: str = Query(
        ..., min_length=1, max_length=5000, description="Text to convert to speech"
    ),
    agent: str = Query(
        default="pro", description="Agent voice: pro, con, judge, or summary"
    ),
):
    """
    Stream text-to-speech audio for any text.
    Returns WAV audio as a streaming response.
    """
    if agent.lower() not in VALID_AGENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent '{agent}'. Use: {', '.join(VALID_AGENTS)}",
        )

    return StreamingResponse(
        tts_service.stream_audio_chunks(text, agent),
        media_type="audio/wav",
        headers={"Content-Disposition": f"inline; filename=tts_{agent}.wav"},
    )


@app.post("/generate")
def generate_tts(
    text: str = Query(..., min_length=1, max_length=5000),
    agent: str = Query(default="pro"),
):
    """
    Generate TTS audio and return as downloadable file.
    """
    if agent.lower() not in VALID_AGENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent '{agent}'. Use: {', '.join(VALID_AGENTS)}",
        )

    audio_bytes = tts_service.generate_audio_bytes(text, agent)

    return StreamingResponse(
        iter([audio_bytes]),
        media_type="audio/wav",
        headers={"Content-Disposition": f"attachment; filename=tts_{agent}.wav"},
    )
