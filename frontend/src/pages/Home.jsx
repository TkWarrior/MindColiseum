// import { useState } from 'react';
// import { useNavigate } from 'react-router-dom';
// import { debateService } from '../services/api';
// import { motion } from 'framer-motion';
// import { ArrowRight, Cpu } from 'lucide-react';

// const Home = () => {
//   const [topic, setTopic] = useState('');
//   const [loading, setLoading] = useState(false);
//   const navigate = useNavigate();

//   const handleStart = async (e) => {
//     e.preventDefault();
//     if (!topic.trim()) return;

//     setLoading(true);
//     try {
//       const debate = await debateService.createDebate(topic);
//       // Navigate to debate room — the SSE stream endpoint starts the debate
//       navigate(`/debate/${debate.id}`);
//     } catch (err) {
//       console.error("Failed to start debate:", err);
//       // Simple error handling for now
//       alert("Failed to create debate. Ensure backend is running.");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="min-h-screen flex items-center justify-center bg-[url('/grid-bg.png')] bg-cover relative overflow-hidden">
//       {/* Background glow effects */}
//       <div className="absolute top-0 left-0 w-full h-full bg-dark-bg/90 backdrop-blur-sm z-0"></div>
//       <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-neon-blue/20 rounded-full blur-[100px] pointer-events-none"></div>
//       <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-neon-red/20 rounded-full blur-[100px] pointer-events-none"></div>

//       <motion.div
//         initial={{ opacity: 0, scale: 0.9 }}
//         animate={{ opacity: 1, scale: 1 }}
//         className="relative z-10 w-full max-w-2xl px-6"
//       >
//         <div className="text-center mb-16">
//           <div className="flex justify-center mb-6">
//             <Cpu size={64} className="text-neon-purple animate-pulse" />
//           </div>
//           <h1 className="text-6xl font-display font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-neon-blue via-neon-purple to-neon-red">
//             MIND COLISEUM
//           </h1>
//           <p className="text-xl text-gray-400 font-light">
//             Witness AI Agents Debate the Unimaginable
//           </p>
//         </div>

//         <form onSubmit={handleStart} className="space-y-6">
//           <div className="relative group">
//             <input
//               type="text"
//               value={topic}
//               onChange={(e) => setTopic(e.target.value)}
//               placeholder="Enter a controversial topic..."
//               className="w-full bg-gray-900/80 border-2 border-gray-700 rounded-full py-4 px-8 text-xl text-white outline-none focus:border-neon-blue transition-all duration-300 placeholder:text-gray-600 shadow-2xl group-hover:shadow-[0_0_20px_rgba(0,243,255,0.2)]"
//               disabled={loading}
//               autoFocus
//             />
//           </div>

//           <button
//             type="submit"
//             disabled={loading || !topic}
//             className="w-full bg-gradient-to-r from-neon-blue to-neon-purple text-black font-bold py-4 rounded-full text-xl hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(191,0,255,0.4)]"
//           >
//             {loading ? (
//               <span className="animate-pulse">Initializing Arena...</span>
//             ) : (
//               <>
//                 Enter the Arena <ArrowRight size={24} />
//               </>
//             )}
//           </button>
//         </form>
//       </motion.div>
//     </div>
//   );
// };

// export default Home;


import { useState } from "react";
import { useNavigate } from "react-router-dom"; // Added import
import { motion } from "framer-motion";
import { ArrowRight, Cpu } from "lucide-react";
import TrendingTopicCard from "../components/Debate/TrendingTopicCads";
import { debateService } from "../services/api"; // Added import

const TRENDING_TOPICS = [
  "Should AI have legal rights?",
  "Is universal basic income inevitable?",
  "Will humans colonize Mars by 2050?",
  "Should social media be regulated like tobacco?",
  "Is consciousness just computation?",
  "Can democracy survive in the age of AI?",
  "Should gene editing in humans be allowed?",
  "Is privacy dead in the digital age?",
];

const Home = () => {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); // Added hook

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

  const handleTopicClick = (selectedTopic) => {
    setTopic(selectedTopic);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-[url('/grid-bg.png')] bg-cover bg-center relative overflow-hidden">
      {/* Overlay */}
      <div className="absolute inset-0 bg-background/90 backdrop-blur-sm z-0" />

      {/* Glow orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-neon-blue/10 rounded-full blur-[120px] pointer-events-none animate-glow-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-neon-purple/10 rounded-full blur-[120px] pointer-events-none animate-glow-pulse [animation-delay:1.5s]" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-neon-red/5 rounded-full blur-[150px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, scale: 0.92 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-10 w-full max-w-2xl px-6 py-12"
      >
        {/* Header */}
        <div className="text-center mb-12">
          <motion.div
            className="flex justify-center mb-6"
            animate={{ y: [0, -8, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
          >
            <div className="relative">
              <Cpu size={56} className="text-neon-purple" />
              <div className="absolute inset-0 blur-xl bg-neon-purple/30 rounded-full" />
            </div>
          </motion.div>

          <h1 className="text-5xl md:text-6xl font-display font-bold mb-4 text-gradient-neon tracking-wider">
            MIND COLISEUM
          </h1>
          <p className="text-lg text-muted-foreground font-light tracking-wide">
            Witness AI Agents Debate the Unimaginable
          </p>
        </div>

        {/* Input Form */}
        <form onSubmit={handleStart} className="space-y-5 mb-12">
          <div className="relative group">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter a controversial topic..."
              className="w-full bg-card/80 border-2 border-border rounded-full py-4 px-8 text-lg text-foreground outline-none focus:border-primary transition-all duration-300 placeholder:text-muted-foreground/50 shadow-2xl group-hover:glow-blue focus:glow-blue backdrop-blur-sm"
              disabled={loading}
              autoFocus
            />
          </div>

          <button
            type="submit"
            disabled={loading || !topic.trim()}
            className="w-full bg-gradient-neon text-primary-foreground font-display font-bold py-4 rounded-full text-lg hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-3 glow-purple tracking-wider"
          >
            {loading ? (
              <span className="animate-pulse">Initializing Arena...</span>
            ) : (
              <>
                Enter the Arena <ArrowRight size={22} />
              </>
            )}
          </button>
        </form>

        {/* Trending Topics */}
        <div>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-sm font-display text-muted-foreground tracking-widest uppercase text-center mb-5"
          >
            🔥 Trending Debates
          </motion.p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {TRENDING_TOPICS.map((t, i) => (
              <TrendingTopicCard
                key={t}
                topic={t}
                index={i}
                onClick={handleTopicClick}
              />
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Home;
