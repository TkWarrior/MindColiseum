import { motion } from "framer-motion";
import { Flame, Zap, Brain, Globe, Shield, Sparkles } from "lucide-react";

const icons = [Flame, Zap, Brain, Globe, Shield, Sparkles];

const TrendingTopicCard = ({ topic, index, onClick }) => {
    const Icon = icons[index % icons.length];

    return (
        <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 + index * 0.08, duration: 0.4 }}
            whileHover={{ scale: 1.04, y: -2 }}
            whileTap={{ scale: 0.97 }}
            onClick={() => onClick(topic)}
            className="group relative flex items-center gap-3 rounded-xl border border-border bg-card/60 backdrop-blur-sm px-4 py-3 text-left transition-all duration-300 hover:border-primary/50 hover:glow-blue cursor-pointer"
        >
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-muted group-hover:bg-primary/20 transition-colors">
                <Icon size={16} className="text-muted-foreground group-hover:text-primary transition-colors" />
            </div>
            <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors line-clamp-2">
                {topic}
            </span>
        </motion.button>
    );
};

export default TrendingTopicCard;
