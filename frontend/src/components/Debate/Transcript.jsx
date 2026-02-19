import { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const Transcript = ({ messages }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="h-[400px] overflow-y-auto p-4 bg-gray-900/50 rounded-lg border border-gray-800 backdrop-blur-sm custom-scrollbar" ref={scrollRef}>
      <div className="flex flex-col gap-4">
        <AnimatePresence>
          {messages.map((msg, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={clsx(
                "p-4 rounded-lg max-w-[80%] border-l-4",
                msg.agent === 'pro' && "self-start bg-blue-900/20 border-neon-blue",
                msg.agent === 'con' && "self-end bg-red-900/20 border-neon-red",
                msg.agent === 'judge' && "self-center bg-purple-900/20 border-neon-purple w-full text-center",
                msg.agent === 'summary' && "self-center bg-gray-800 border-gray-500 w-full text-center italic"
              )}
            >
              <span className={clsx("text-xs font-bold uppercase mb-1 block",
                 msg.agent === 'pro' && "text-neon-blue",
                 msg.agent === 'con' && "text-neon-red",
                 msg.agent === 'judge' && "text-neon-purple",
              )}>
                {msg.agent}
              </span>
              <p className="text-gray-200 leading-relaxed font-body">
                {msg.text}
              </p>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Transcript;
