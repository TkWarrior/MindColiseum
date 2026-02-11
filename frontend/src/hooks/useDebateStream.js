import { useState, useEffect, useRef } from 'react';

export const useDebateStream = (debateId) => {
  const [messages, setMessages] = useState([]);
  const [currentSpeaker, setCurrentSpeaker] = useState(null);
  const [status, setStatus] = useState('connecting');
  const [audioQueue, setAudioQueue] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  
  const eventSourceRef = useRef(null);

  useEffect(() => {
    if (!debateId) return;

    // Connect to SSE endpoint
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
      setMessages((prev) => [...prev, { type: 'text', ...data }]);
      setCurrentSpeaker(data.agent);
    });

    eventSource.addEventListener('agent_audio', (e) => {
      const data = JSON.parse(e.data);
      // Add audio chunk to queue
      setAudioQueue((prev) => [...prev, data.audio]);
    });

    eventSource.addEventListener('debate_complete', (e) => {
      setStatus('completed');
      setCurrentSpeaker(null);
      eventSource.close();
    });

    eventSource.onerror = (err) => {
      console.error('SSE Error:', err);
      eventSource.close();
      setStatus('error');
    };

    return () => {
      if (eventSource.readyState !== EventSource.CLOSED) {
          eventSource.close();
      }
    };
  }, [debateId]);

  // Audio Player Logic
  useEffect(() => {
    if (isPlaying || audioQueue.length === 0) return;

    const playNextChunk = async () => {
      setIsPlaying(true);
      const audioBase64 = audioQueue[0];
      
      try {
        const audio = new Audio(`data:audio/wav;base64,${audioBase64}`);
        const playPromise = audio.play();
        
        if (playPromise !== undefined) {
             playPromise.then(() => {
                 // Playback started
             }).catch(error => {
                 console.error("Audio access denied or failed", error);
                 // Skip this chunk if it fails to play (e.g. interaction policy)
                 setAudioQueue((prev) => prev.slice(1));
                 setIsPlaying(false);
             });
        }

        audio.onended = () => {
          setAudioQueue((prev) => prev.slice(1)); // Remove played chunk
          setIsPlaying(false);
        };

        // Handle errors during playback
        audio.onerror = (e) => {
            console.error("Audio playback error", e);
            setAudioQueue((prev) => prev.slice(1));
            setIsPlaying(false);
        }

      } catch (err) {
        console.error("Audio setup error:", err);
        setAudioQueue((prev) => prev.slice(1));
        setIsPlaying(false);
      }
    };

    playNextChunk();
  }, [audioQueue, isPlaying]);

  return { messages, currentSpeaker, status };
};
