import { motion } from 'framer-motion';
import clsx from 'clsx';
import { Mic } from 'lucide-react';
import GlassOrb from './GlassOrb';

const AGENT_GLOW = {
  pro: { idle: '0 0 20px rgba(4, 0, 255, 0.41)', speaking: '0 0 40px rgba(38, 0, 255, 0.3), 0 0 80px rgba(0,136,255,0.2)' },
  con: { idle: '0 0 20px rgba(255,0,60,0.15)', speaking: '0 0 40px rgba(255,0,60,0.4), 0 0 80px rgba(255,68,68,0.2)' },
  judge: { idle: '0 0 20px rgba(0,255,136,0.15)', speaking: '0 0 40px rgba(0,255,136,0.4), 0 0 80px rgba(0,204,102,0.2)' },
};

const AGENT_TEXT_COLOR = {
  pro: 'text-neon-blue',
  con: 'text-neon-red',
  judge: 'text-neon-green',
};

const AgentAvatar = ({ agent, isSpeaking }) => {
  const glow = AGENT_GLOW[agent] || AGENT_GLOW.pro;
  const textColor = AGENT_TEXT_COLOR[agent] || AGENT_TEXT_COLOR.pro;

  return (
    <div className="flex flex-col items-center gap-4">
      {/* Orb with ambient glow */}
      <motion.div
        animate={{ scale: isSpeaking ? 1.05 : 1 }}
        transition={{ duration: 0.4, ease: 'easeInOut' }}
        style={{
          borderRadius: '50%',
          boxShadow: isSpeaking ? glow.speaking : glow.idle,
          transition: 'box-shadow 0.5s ease',
        }}
      >
        <GlassOrb agent={agent} isSpeaking={isSpeaking} size={128} />
      </motion.div>

      {/* Label + Speaking indicator */}
      <div className="text-center">
        <h3 className={clsx("text-xl font-bold uppercase tracking-widest", textColor)}>
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
