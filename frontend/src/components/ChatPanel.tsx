import { useState, useEffect, useRef } from 'react';
import { Send, Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Message } from '../hooks/useSocket';
import HitlCard from './HitlCard';
import ToolCard from './ToolCard';

interface ChatPanelProps {
  messages: Message[];
  hitlPlan: string | null;
  onSend: (prompt: string) => void;
  onHitlRespond: (feedback: string) => void;
}

export default function ChatPanel({ messages, hitlPlan, onSend, onHitlRespond }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, hitlPlan]);

  const handleSend = () => {
    if (!input.trim()) return;
    onSend(input);
    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-background min-h-0 w-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-card">
        <Send size={18} className="text-blue-500" />
        <h2 className="text-lg font-bold">Agent Chat</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => {
          if (msg.role === 'tool') {
            return (
              <div key={idx} className="flex justify-start">
                <div className="w-[85%]">
                  <ToolCard toolName={msg.toolName || 'Unknown Tool'} toolInput={msg.toolInput} />
                </div>
              </div>
            );
          }

          return (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-xl px-4 py-3 shadow-sm border ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground border-primary/20'
                    : 'bg-muted/50 border-border'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  {msg.role === 'user' ? (
                    <User size={14} className="text-primary-foreground/70" />
                  ) : (
                    <Bot size={14} className="text-green-500 dark:text-green-400" />
                  )}
                  <span className={`text-xs font-semibold uppercase ${msg.role === 'user' ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
                    {msg.role === 'user' ? 'You' : msg.agent || 'Agent'}
                  </span>
                </div>
                <div className="text-sm prose prose-sm max-w-none break-words dark:prose-invert">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      {hitlPlan && (
        <div className="px-4 pb-3">
          <HitlCard plan={hitlPlan} onRespond={onHitlRespond} />
        </div>
      )}

      <div className="p-4 border-t border-border bg-card">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Instruct the PM Agent..."
            className="flex-1 bg-background border border-input rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring transition-all"
          />
          <button
            onClick={handleSend}
            className="bg-primary text-primary-foreground hover:opacity-90 px-4 rounded-lg flex items-center transition-opacity"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
