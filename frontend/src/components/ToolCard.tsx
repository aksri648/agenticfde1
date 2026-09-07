import { Wrench } from 'lucide-react';

interface ToolCardProps {
  toolName: string;
  toolInput: any;
}

export default function ToolCard({ toolName, toolInput }: ToolCardProps) {
  return (
    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-3 my-1">
      <div className="flex items-center gap-2 mb-2 text-gray-400">
        <Wrench size={14} />
        <span className="text-xs font-mono font-bold truncate">{toolName}</span>
      </div>
      <div className="bg-black/50 p-2 rounded text-xs font-mono text-gray-300 overflow-x-auto">
        <pre>{JSON.stringify(toolInput, null, 2)}</pre>
      </div>
    </div>
  );
}
