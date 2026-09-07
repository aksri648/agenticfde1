import { useState, useEffect, useRef } from 'react';
import { Send, Bot, User } from 'lucide-react';
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
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-800">
        <Send size={18} className="text-blue-400" />
        <h2 className="text-lg font-bold">Agent Chat</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
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
                className={`max-w-[85%] rounded-xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-blue-600/20 border border-blue-700/50'
                    : 'bg-gray-800 border border-gray-700'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {msg.role === 'user' ? (
                    <User size={14} className="text-blue-400" />
                  ) : (
                    <Bot size={14} className="text-green-400" />
                  )}
                  <span className="text-xs font-semibold text-gray-400 uppercase">
                    {msg.role === 'user' ? 'You' : msg.agent || 'Agent'}
                  </span>
                </div>
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
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

      <div className="p-4 border-t border-gray-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Instruct the PM Agent..."
            className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-blue-500 transition-colors"
          />
          <button
            onClick={handleSend}
            className="bg-blue-600 hover:bg-blue-500 px-4 rounded-lg flex items-center transition-colors"
          >
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}
