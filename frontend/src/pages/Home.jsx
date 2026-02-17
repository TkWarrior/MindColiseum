import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { debateService } from '../services/api';
import { motion } from 'framer-motion';
import { ArrowRight, Cpu } from 'lucide-react';

const Home = () => {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleStart = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setLoading(true);
    try {
      const debate = await debateService.createDebate(topic);
      // Navigate to debate room — the SSE stream endpoint starts the debate
      navigate(`/debate/${debate.id}`);
    } catch (err) {
      console.error("Failed to start debate:", err);
      // Simple error handling for now
      alert("Failed to create debate. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[url('/grid-bg.png')] bg-cover relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-0 left-0 w-full h-full bg-dark-bg/90 backdrop-blur-sm z-0"></div>
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-neon-blue/20 rounded-full blur-[100px] pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-neon-red/20 rounded-full blur-[100px] pointer-events-none"></div>

      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="relative z-10 w-full max-w-2xl px-6"
      >
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <Cpu size={64} className="text-neon-purple animate-pulse" />
          </div>
          <h1 className="text-6xl font-display font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-neon-blue via-neon-purple to-neon-red">
            MIND COLISEUM
          </h1>
          <p className="text-xl text-gray-400 font-light">
            Witness AI Agents Debate the Unimaginable
          </p>
        </div>

        <form onSubmit={handleStart} className="space-y-6">
          <div className="relative group">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter a controversial topic..."
              className="w-full bg-gray-900/80 border-2 border-gray-700 rounded-full py-4 px-8 text-xl text-white outline-none focus:border-neon-blue transition-all duration-300 placeholder:text-gray-600 shadow-2xl group-hover:shadow-[0_0_20px_rgba(0,243,255,0.2)]"
              disabled={loading}
              autoFocus
            />
          </div>

          <button
            type="submit"
            disabled={loading || !topic}
            className="w-full bg-gradient-to-r from-neon-blue to-neon-purple text-black font-bold py-4 rounded-full text-xl hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(191,0,255,0.4)]"
          >
            {loading ? (
              <span className="animate-pulse">Initializing Arena...</span>
            ) : (
              <>
                Enter the Arena <ArrowRight size={24} />
              </>
            )}
          </button>
        </form>
      </motion.div>
    </div>
  );
};

export default Home;
