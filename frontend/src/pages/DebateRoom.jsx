import { useParams } from 'react-router-dom';
import { useDebateStream } from '../hooks/useDebateStream';
import AgentAvatar from '../components/Debate/AgentAvatar';
import Transcript from '../components/Debate/Transcript';
import { ArrowLeft, Volume2, VolumeX } from 'lucide-react';
import { Link } from 'react-router-dom';

const DebateRoom = () => {
    const { id } = useParams();
    const { messages, currentSpeaker, status, audioEnabled, unlockAudio } = useDebateStream(id);

    return (
        <div className="min-h-screen bg-dark-bg text-white p-4 lg:p-8 flex flex-col relative overflow-hidden">
            {/* Background ambience */}
            <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-neon-blue to-transparent opacity-50"></div>

            {/* Header */}
            <header className="flex items-center justify-between mb-12 z-10 relative">
                <Link to="/" className="text-gray-400 hover:text-white flex items-center gap-2 transition-colors">
                    <ArrowLeft size={20} /> Exit Arena
                </Link>
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-4 bg-gray-900/80 px-4 py-2 rounded-full border border-gray-700">
                        <div className={`w-3 h-3 rounded-full ${status === 'live' ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
                        <span className="text-sm font-mono uppercase tracking-widest text-gray-300">
                            {status === 'connecting' ? 'Connecting satellite...' : status === 'live' ? 'LIVE TRANSMISSION' : 'SESSION ENDED'}
                        </span>
                    </div>
                    <button
                        onClick={unlockAudio}
                        className={`flex items-center gap-2 px-4 py-2 rounded-full border transition-all duration-300 ${audioEnabled
                                ? 'bg-green-900/40 border-green-500/50 text-green-400'
                                : 'bg-amber-900/40 border-amber-500/50 text-amber-400 animate-pulse cursor-pointer hover:bg-amber-900/60'
                            }`}
                        disabled={audioEnabled}
                        title={audioEnabled ? 'Audio enabled' : 'Click to enable audio playback'}
                    >
                        {audioEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
                        <span className="text-xs font-mono uppercase tracking-wider">
                            {audioEnabled ? 'Audio On' : 'Enable Audio'}
                        </span>
                    </button>
                </div>
            </header>

            {/* Main Arena */}
            <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-8 z-10 relative max-w-7xl mx-auto w-full h-full">

                {/* Left Agent (PRO) */}
                <div className="lg:col-span-3 flex flex-col justify-center items-center">
                    <AgentAvatar agent="pro" isSpeaking={currentSpeaker === 'pro'} />
                </div>

                {/* Center Stage (Judge + Transcript) */}
                <div className="lg:col-span-6 flex flex-col gap-6">
                    <div className="flex justify-center mb-4">
                        <AgentAvatar agent="judge" isSpeaking={currentSpeaker === 'judge'} />
                    </div>

                    <div className="flex-1 relative">
                        {/* Perspective decoration lines */}
                        <div className="absolute -inset-1 bg-gradient-to-b from-gray-800 to-transparent opacity-30 blur-sm rounded-lg pointer-events-none"></div>
                        <Transcript messages={messages} />
                    </div>
                </div>

                {/* Right Agent (CON) */}
                <div className="lg:col-span-3 flex flex-col justify-center items-center">
                    <AgentAvatar agent="con" isSpeaking={currentSpeaker === 'con'} />
                </div>

            </main>
        </div>
    );
};

export default DebateRoom;
