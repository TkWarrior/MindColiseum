import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * useDebateStream — SSE + Web Audio API with synchronized text/audio playback.
 *
 * Sync strategy:
 *   - Backend sends pairs: agent_text → (TTS delay) → agent_audio
 *   - We buffer incoming text+audio into a "pending" queue
 *   - Text is only displayed when its paired audio STARTS playing
 *   - This keeps text and voice perfectly in sync
 *   - If audio is missing (TTS failed), text is shown immediately
 */
export const useDebateStream = (debateId) => {
  const [messages, setMessages] = useState([]);           // displayed messages
  const [currentSpeaker, setCurrentSpeaker] = useState(null);
  const [status, setStatus] = useState('connecting');
  const [audioEnabled, setAudioEnabled] = useState(false);

  const eventSourceRef = useRef(null);
  const audioCtxRef = useRef(null);

  // Pending queue: items waiting for audio or waiting to be played
  // Each item: { agent, round, text, audio: base64|null, ready: bool }
  const pendingRef = useRef([]);
  const isPlayingRef = useRef(false);

  // ── Initialize AudioContext ─────────────────────────────────────
  useEffect(() => {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) {
      audioCtxRef.current = new AudioContext();
    }
    return () => {
      if (audioCtxRef.current) {
        audioCtxRef.current.close();
      }
    };
  }, []);

  // ── Unlock audio (must be called from user click) ───────────────
  const unlockAudio = useCallback(async () => {
    const ctx = audioCtxRef.current;
    if (!ctx) return;
    if (ctx.state === 'suspended') {
      await ctx.resume();
    }
    setAudioEnabled(true);
  }, []);

  // ── Process queue: show text + play audio in sync ───────────────
  const processQueue = useCallback(async () => {
    const ctx = audioCtxRef.current;
    if (isPlayingRef.current) return;
    if (pendingRef.current.length === 0) return;

    const item = pendingRef.current[0];

    // If audio isn't ready yet and item isn't timed-out, wait
    if (!item.ready) return;

    isPlayingRef.current = true;
    pendingRef.current.shift();

    // Show the text message NOW (synced with audio start)
    setMessages((prev) => [...prev, { type: 'text', agent: item.agent, round: item.round, text: item.text }]);
    setCurrentSpeaker(item.agent);

    // Play the audio if available
    if (item.audio && ctx && ctx.state === 'running') {
      try {
        const binaryString = atob(item.audio);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }

        const audioBuffer = await ctx.decodeAudioData(bytes.buffer);
        const source = ctx.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(ctx.destination);

        source.onended = () => {
          isPlayingRef.current = false;
          processQueue(); // play next
        };

        source.start(0);
        return; // wait for onended
      } catch (err) {
        console.error('Audio decode/playback error:', err);
      }
    }

    // No audio or audio failed — move to next immediately
    isPlayingRef.current = false;
    processQueue();
  }, []);

  // ── SSE connection ──────────────────────────────────────────────
  useEffect(() => {
    if (!debateId) return;

    const url = `http://localhost:8000/debates/${debateId}/stream`;
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setStatus('live');
      console.log('SSE Connected');
    };

    eventSource.addEventListener('debate_started', (e) => {
      const data = JSON.parse(e.data);
      console.log('Debate Started:', data);
    });

    eventSource.addEventListener('agent_text', (e) => {
      const data = JSON.parse(e.data);
      // Buffer the text — don't display yet, wait for audio
      pendingRef.current.push({
        agent: data.agent,
        round: data.round,
        text: data.text,
        audio: null,
        ready: false,
      });

      // Safety timeout: if audio doesn't arrive within 30s, show text anyway
      const itemIndex = pendingRef.current.length - 1;
      setTimeout(() => {
        const item = pendingRef.current[itemIndex];
        if (item && !item.ready) {
          item.ready = true;
          processQueue();
        }
      }, 30000);
    });

    eventSource.addEventListener('agent_audio', (e) => {
      const data = JSON.parse(e.data);
      // Find the first pending item that doesn't have audio yet
      const pending = pendingRef.current.find((p) => !p.audio && !p.ready);
      if (pending) {
        pending.audio = data.audio;
        pending.ready = true;
      }
      processQueue();
    });

    eventSource.addEventListener('debate_complete', (e) => {
      // Flush any remaining pending items without audio
      pendingRef.current.forEach((item) => {
        if (!item.ready) {
          item.ready = true;
        }
      });
      processQueue();

      // Set status after a short delay to let queue drain
      setTimeout(() => {
        setStatus('completed');
        setCurrentSpeaker(null);
      }, 500);
      eventSource.close();
    });

    eventSource.onerror = (err) => {
      console.error('SSE Error:', err);
      // Flush pending items on error
      pendingRef.current.forEach((item) => {
        if (!item.ready) {
          item.ready = true;
        }
      });
      processQueue();
      eventSource.close();
      setStatus('error');
    };

    return () => {
      if (eventSource.readyState !== EventSource.CLOSED) {
        eventSource.close();
      }
    };
  }, [debateId, processQueue]);

  return { messages, currentSpeaker, status, audioEnabled, unlockAudio };
};
