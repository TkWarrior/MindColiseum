"""
End-to-End Test: Debate Streaming Pipeline
===========================================
Tests the full flow: Create debate → SSE stream → verify text & audio events.

Prerequisites:
    1. Backend running: uvicorn backend.main:app --port 8000 --reload  
    2. TTS miniservice running: cd tts_miniservice && uvicorn main:app --port 8001 --reload
    3. PostgreSQL running (docker-compose up -d)

Usage:
    python tests/test_e2e_stream.py
"""

import sys
import json
import time
import base64
import requests
import sseclient  # pip install sseclient-py

sys.path.insert(0, ".")

BACKEND_URL = "http://localhost:8000"
TTS_URL = "http://localhost:8001"

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
INFO = "\033[94mℹ\033[0m"


def check_services():
    """Verify backend and TTS services are reachable."""
    print(f"\n{'='*60}")
    print("PRE-FLIGHT CHECKS")
    print(f"{'='*60}")

    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=3)
        r.raise_for_status()
        print(f"  {PASS} Backend is running on :8000")
    except Exception as e:
        print(f"  {FAIL} Backend is NOT running: {e}")
        return False

    try:
        r = requests.get(f"{TTS_URL}/health", timeout=3)
        r.raise_for_status()
        print(f"  {PASS} TTS miniservice is running on :8001")
    except Exception as e:
        print(f"  {FAIL} TTS miniservice is NOT running: {e}")
        print(f"  {INFO} Start it: cd tts_miniservice && uvicorn main:app --port 8001")
        return False

    return True


def create_debate(topic="Is AI beneficial for education?", max_rounds=1):
    """Create a new pending debate."""
    print(f"\n{'='*60}")
    print("STEP 1: CREATE DEBATE")
    print(f"{'='*60}")

    r = requests.post(
        f"{BACKEND_URL}/debates",
        json={"topic": topic, "max_rounds": max_rounds},
    )
    r.raise_for_status()
    debate = r.json()
    debate_id = debate["id"]
    print(f"  {PASS} Created debate #{debate_id}: '{topic}' (max_rounds={max_rounds})")
    print(f"  {INFO} Status: {debate['status']}")
    return debate_id


def stream_debate(debate_id):
    """
    Connect to SSE stream and collect all events.
    Verifies event ordering, text/audio pairing, and audio validity.
    """
    print(f"\n{'='*60}")
    print(f"STEP 2: STREAM DEBATE #{debate_id}")
    print(f"{'='*60}")

    url = f"{BACKEND_URL}/debates/{debate_id}/stream"
    print(f"  {INFO} Connecting to {url}")

    response = requests.get(url, stream=True, timeout=300)
    client = sseclient.SSEClient(response)

    events = []
    text_events = []
    audio_events = []
    event_timeline = []

    start_time = time.time()

    for event in client.events():
        elapsed = time.time() - start_time
        event_data = json.loads(event.data) if event.data else {}
        event_record = {
            "type": event.event,
            "data": event_data,
            "elapsed_sec": round(elapsed, 2),
        }
        events.append(event_record)
        event_timeline.append(event_record)

        if event.event == "debate_started":
            print(f"  [{elapsed:6.2f}s] {PASS} debate_started — topic: {event_data.get('topic', '?')}")

        elif event.event == "agent_text":
            text_events.append(event_record)
            agent = event_data.get("agent", "?")
            rnd = event_data.get("round", "?")
            text_preview = event_data.get("text", "")[:80]
            print(f"  [{elapsed:6.2f}s] {PASS} agent_text    — [{agent}] round {rnd}: \"{text_preview}...\"")

        elif event.event == "agent_audio":
            audio_events.append(event_record)
            agent = event_data.get("agent", "?")
            rnd = event_data.get("round", "?")
            audio_b64 = event_data.get("audio", "")
            audio_size = len(base64.b64decode(audio_b64)) if audio_b64 else 0
            print(f"  [{elapsed:6.2f}s] {PASS} agent_audio   — [{agent}] round {rnd}: {audio_size:,} bytes WAV")

        elif event.event == "round_complete":
            rnd = event_data.get("round", "?")
            scores = event_data.get("scores", {})
            print(f"  [{elapsed:6.2f}s] {PASS} round_complete — round {rnd}, scores: {scores}")

        elif event.event == "debate_complete":
            print(f"  [{elapsed:6.2f}s] {PASS} debate_complete — pro:{event_data.get('pro_score')}, con:{event_data.get('con_score')}")
            break

        elif event.event == "error":
            print(f"  [{elapsed:6.2f}s] {FAIL} ERROR — {event_data.get('message', '?')}")
            break

    total_time = time.time() - start_time
    return events, text_events, audio_events, event_timeline, total_time


def analyze_sync(text_events, audio_events, event_timeline):
    """Analyze text/audio pairing and timing sync."""
    print(f"\n{'='*60}")
    print("STEP 3: SYNC ANALYSIS")
    print(f"{'='*60}")

    # Check text/audio pairing
    print(f"\n  Text events: {len(text_events)}")
    print(f"  Audio events: {len(audio_events)}")

    if len(text_events) != len(audio_events):
        print(f"  {FAIL} MISMATCH: {len(text_events)} text events vs {len(audio_events)} audio events")
        if len(audio_events) == 0:
            print(f"  {FAIL} NO AUDIO EVENTS — TTS miniservice may not be generating audio")
    else:
        print(f"  {PASS} Text and audio events are paired (1:1)")

    # Analyze timing gaps between text→audio for each pair
    print(f"\n  Per-agent timing (text → audio gap):")
    for i in range(min(len(text_events), len(audio_events))):
        text_t = text_events[i]["elapsed_sec"]
        audio_t = audio_events[i]["elapsed_sec"]
        gap = round(audio_t - text_t, 2)
        agent = text_events[i]["data"].get("agent", "?")
        rnd = text_events[i]["data"].get("round", "?")
        status = PASS if gap < 10 else FAIL
        print(f"    {status} [{agent}] round {rnd}: text@{text_t}s → audio@{audio_t}s (gap: {gap}s)")

    # Check event ordering (should be: text → audio → text → audio ...)
    print(f"\n  Event ordering:")
    ta_sequence = []
    for evt in event_timeline:
        if evt["type"] == "agent_text":
            ta_sequence.append("T")
        elif evt["type"] == "agent_audio":
            ta_sequence.append("A")

    expected_pattern = "TA" * min(len(text_events), len(audio_events))
    actual_pattern = "".join(ta_sequence)
    if actual_pattern == expected_pattern:
        print(f"    {PASS} Correct: {actual_pattern}")
    else:
        print(f"    {FAIL} Expected: {expected_pattern}")
        print(f"    {FAIL} Got:      {actual_pattern}")

    # Estimate audio durations (WAV file sizes)
    print(f"\n  Audio chunk sizes:")
    for i, ae in enumerate(audio_events):
        audio_b64 = ae["data"].get("audio", "")
        if audio_b64:
            audio_bytes = base64.b64decode(audio_b64)
            # WAV at 16kHz 16-bit mono ≈ 32KB/sec
            est_duration = len(audio_bytes) / 32000
            agent = ae["data"].get("agent", "?")
            print(f"    {INFO} [{agent}]: {len(audio_bytes):,} bytes ≈ {est_duration:.1f}s of audio")


def verify_audio_validity(audio_events):
    """Verify audio data is valid WAV."""
    print(f"\n{'='*60}")
    print("STEP 4: AUDIO VALIDITY")
    print(f"{'='*60}")

    for i, ae in enumerate(audio_events):
        audio_b64 = ae["data"].get("audio", "")
        if not audio_b64:
            print(f"  {FAIL} Audio event {i}: empty audio data")
            continue

        audio_bytes = base64.b64decode(audio_b64)
        
        # Check WAV header (RIFF....WAVE)
        if len(audio_bytes) < 44:
            print(f"  {FAIL} Audio event {i}: too small ({len(audio_bytes)} bytes)")
            continue

        riff = audio_bytes[:4]
        wave = audio_bytes[8:12]
        if riff == b"RIFF" and wave == b"WAVE":
            agent = ae["data"].get("agent", "?")
            print(f"  {PASS} [{agent}]: Valid WAV, {len(audio_bytes):,} bytes")
        else:
            print(f"  {FAIL} Audio event {i}: invalid WAV header (got {riff} {wave})")


def main():
    print("\n" + "=" * 60)
    print("  MindColiseum E2E Stream Test")
    print("=" * 60)

    if not check_services():
        print(f"\n{FAIL} Pre-flight checks failed. Please start all services first.")
        sys.exit(1)

    debate_id = create_debate(
        topic="Is AI beneficial for education?",
        max_rounds=1,  # Keep it short for testing
    )

    events, text_events, audio_events, timeline, total_time = stream_debate(debate_id)

    analyze_sync(text_events, audio_events, timeline)
    verify_audio_validity(audio_events)

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"  Total events: {len(events)}")
    print(f"  Total time:   {total_time:.1f}s")
    print(f"  Text events:  {len(text_events)}")
    print(f"  Audio events: {len(audio_events)}")

    if len(audio_events) == 0:
        print(f"\n  {FAIL} NO AUDIO — Frontend will have nothing to play!")
    elif len(text_events) == len(audio_events):
        print(f"\n  {PASS} Backend pipeline is healthy — text and audio are paired correctly")
    else:
        print(f"\n  {FAIL} Text/audio count mismatch — investigate backend logs")

    print()


if __name__ == "__main__":
    main()
