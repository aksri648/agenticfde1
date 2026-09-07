import { Wrench } from 'lucide-react';

interface ToolCardProps {
  toolName: string;
  toolInput: any;
}

export default function ToolCard({ toolName, toolInput }: ToolCardProps) {
  return (
    <div className="bg-muted/50 border border-border rounded-lg p-3 my-1">
      <div className="flex items-center gap-2 mb-2 text-muted-foreground">
        <Wrench size={14} />
        <span className="text-xs font-mono font-bold truncate">{toolName}</span>
      </div>
      <div className="bg-background/80 p-2 rounded text-xs font-mono text-foreground overflow-x-auto">
        <pre>{JSON.stringify(toolInput, null, 2)}</pre>
      </div>
    </div>
  );
}
