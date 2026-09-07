import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export interface Log {
  timestamp: string;
  agent: string;
  message: string;
}

export interface Message {
  role: 'user' | 'agent' | 'tool';
  agent?: string;
  content: string;
  toolName?: string;
  toolInput?: any;
}

export interface HitlRequest {
  plan: string;
}

export function useSocket() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [logs, setLogs] = useState<Log[]>([]);
  const [hitlPlan, setHitlPlan] = useState<string | null>(null);
  const [daytonaUrl, setDaytonaUrl] = useState<string | null>(null);
  const [activeAgent, setActiveAgent] = useState<string>('pm');

  useEffect(() => {
    const s = io('http://localhost:3000');
    setSocket(s);

    s.on('connect', () => setConnected(true));
    s.on('disconnect', () => setConnected(false));

    s.on('log', (log: Log) => setLogs(prev => [...prev, log]));

    s.on('message', (msg: Message) => setMessages(prev => [...prev, msg]));

    s.on('message_stream', (msg: Message) => {
      setMessages(prev => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.role === 'agent' && last.agent === msg.agent) {
          last.content = msg.content;
        } else {
          updated.push(msg);
        }
        return updated;
      });
    });

    s.on('tool_use', (data: { tool: string; input: any; agent: string }) => {
      setMessages(prev => [
        ...prev,
        { role: 'tool', agent: data.agent, content: '', toolName: data.tool, toolInput: data.input }
      ]);
    });

    s.on('hitl_request', (data: HitlRequest) => setHitlPlan(data.plan));

    s.on('daytona_preview', (url: string) => setDaytonaUrl(url));

    s.on('task_complete', () => setHitlPlan(null));

    return () => { s.close(); };
  }, []);

  const startTask = (prompt: string, agent: string) => {
    if (!socket || !prompt.trim()) return;
    socket.emit('start_task', { prompt, agent });
    setMessages(prev => [...prev, { role: 'user', content: prompt }]);
    setActiveAgent(agent);
  };

  const respondHitl = (feedback: string) => {
    if (!socket) return;
    socket.emit('hitl_response', { feedback });
    setHitlPlan(null);
  };

  return {
    connected,
    messages,
    logs,
    hitlPlan,
    daytonaUrl,
    activeAgent,
    startTask,
    respondHitl,
    setDaytonaUrl,
  };
}
