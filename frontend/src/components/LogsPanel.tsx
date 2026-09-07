import { useRef, useEffect } from 'react';
import { Terminal } from 'lucide-react';
import { Log } from '../hooks/useSocket';

interface LogsPanelProps {
  logs: Log[];
}

export default function LogsPanel({ logs }: LogsPanelProps) {
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const agentColor = (agent: string) => {
    if (agent === 'System') return 'text-blue-400';
    if (agent.includes('Error')) return 'text-red-400';
    if (agent === 'PM_Agent') return 'text-purple-400';
    if (agent === 'AppDeveloper_Agent') return 'text-green-400';
    if (agent === 'AppDeployer_Agent') return 'text-orange-400';
    if (agent === 'AppMaintainer_Agent') return 'text-cyan-400';
    if (agent === 'LLMDeployer_Agent') return 'text-pink-400';
    if (agent === 'User') return 'text-yellow-400';
    return 'text-gray-400';
  };

  return (
    <div className="flex flex-col h-full bg-background min-h-0">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-border bg-card">
        <Terminal size={18} className="text-muted-foreground" />
        <h2 className="text-lg font-bold text-foreground">System Logs</h2>
      </div>
      <div className="flex-1 bg-black/90 p-4 font-mono text-xs overflow-y-auto">
        {logs.length === 0 && (
          <p className="text-muted-foreground italic">Waiting for activity...</p>
        )}
        {logs.map((log, idx) => (
          <div key={idx} className="mb-1.5 leading-relaxed">
            <span className="text-gray-500">
              [{new Date(log.timestamp).toLocaleTimeString()}]
            </span>{' '}
            <span className={`font-bold ${agentColor(log.agent)}`}>
              {log.agent}:
            </span>{' '}
            <span className="text-gray-300">{log.message}</span>
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
}
