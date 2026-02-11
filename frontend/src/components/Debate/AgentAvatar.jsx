import { motion } from 'framer-motion';
import clsx from 'clsx';
import { User, Shield, Gavel, Mic } from 'lucide-react';

const AgentAvatar = ({ agent, isSpeaking }) => {
  const isPro = agent === 'pro';
  const isCon = agent === 'con';
  const isJudge = agent === 'judge';

  const borderColor = isPro ? 'border-neon-blue' : isCon ? 'border-neon-red' : 'border-neon-purple';
  const glowClass = isSpeaking 
    ? (isPro ? 'shadow-[0_0_30px_#00f3ff]' : isCon ? 'shadow-[0_0_30px_#ff003c]' : 'shadow-[0_0_30px_#bf00ff]') 
    : '';

  return (
    <div className="flex flex-col items-center gap-4">
      <motion.div 
        animate={{ scale: isSpeaking ? 1.05 : 1 }}
        transition={{ duration: 0.3 }}
        className={clsx(
          "w-32 h-32 rounded-full border-4 flex items-center justify-center bg-gray-900 transition-all duration-300",
          borderColor,
          glowClass
        )}
      >
        {isPro && <User size={48} className="text-neon-blue" />}
        {isCon && <Shield size={48} className="text-neon-red" />}
        {isJudge && <Gavel size={48} className="text-neon-purple" />}
      </motion.div>
      
      <div className="text-center">
        <h3 className={clsx("text-xl font-bold uppercase tracking-widest", 
          isPro ? "text-neon-blue" : isCon ? "text-neon-red" : "text-neon-purple"
        )}>
          {agent.toUpperCase()}
        </h3>
        {isSpeaking && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            className="flex items-center gap-2 justify-center text-sm text-gray-400 mt-1"
          >
            <Mic size={14} className="animate-pulse" /> Speaking...
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default AgentAvatar;
