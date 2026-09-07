import { MonitorPlay, ExternalLink } from 'lucide-react';

interface DaytonaPreviewProps {
  url: string | null;
}

export default function DaytonaPreview({ url }: DaytonaPreviewProps) {
  if (!url) return null;

  return (
    <div className="flex flex-col h-full min-h-0 w-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-card">
        <div className="flex items-center gap-2">
          <MonitorPlay size={18} className="text-blue-500" />
          <h2 className="text-lg font-bold text-blue-500">Daytona Preview</h2>
        </div>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-muted-foreground hover:text-foreground transition-colors"
        >
          <ExternalLink size={16} />
        </a>
      </div>
      <div className="flex-1 relative bg-black">
        <iframe
          src={url}
          title="Daytona Sandbox"
          className="w-full h-full bg-white"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
        />
        <div className="absolute top-3 right-3 bg-black/70 px-3 py-1.5 rounded-full text-xs flex items-center text-green-400 border border-green-900">
          <span className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-ping" />
          Live Environment
        </div>
      </div>
    </div>
  );
}
