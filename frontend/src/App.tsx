import { useSocket } from './hooks/useSocket';
import ChatPanel from './components/ChatPanel';
import LogsPanel from './components/LogsPanel';
import DaytonaPreview from './components/DaytonaPreview';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './components/ui/tabs';
import { ModeToggle } from './components/ModeToggle';

import { MonitorPlay } from 'lucide-react';

const AGENTS = [
  { id: 'pm', label: 'PM Agent', color: 'bg-purple-600 dark:bg-purple-700' },
  { id: 'developer', label: 'Developer', color: 'bg-green-600 dark:bg-green-700' },
  { id: 'deployer', label: 'Deployer', color: 'bg-orange-600 dark:bg-orange-700' },
  { id: 'maintainer', label: 'Maintainer', color: 'bg-cyan-600 dark:bg-cyan-700' },
  { id: 'llm_deployer', label: 'LLM Deployer', color: 'bg-pink-600 dark:bg-pink-700' },
];

export default function App() {
  const {
    connected,
    messages,
    logs,
    hitlPlan,
    daytonaUrl,
    activeAgent,
    startTask,
    respondHitl,
  } = useSocket();

  const handleSend = (prompt: string) => {
    startTask(prompt, activeAgent);
  };

  return (
    <div className="flex flex-col h-screen bg-background text-foreground transition-colors overflow-hidden">
      {/* Top Bar */}
      <header className="flex items-center justify-between px-6 py-3 border-b border-border bg-card">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold">
            5-Agent <span className="text-blue-500">System</span>
          </h1>
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
        </div>
        <div className="flex items-center gap-4">
          <div className="flex gap-2">
            {AGENTS.map(a => (
              <button
                key={a.id}
                onClick={() => {}}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeAgent === a.id
                    ? `${a.color} text-white shadow-md`
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                }`}
              >
                {a.label}
              </button>
            ))}
          </div>
          <ModeToggle />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden min-h-0">
        {/* Left Pane: Chat */}
        <div className="w-[45%] border-r border-border flex flex-col bg-card/50 min-h-0">
          <ChatPanel
            messages={messages}
            hitlPlan={hitlPlan}
            onSend={handleSend}
            onHitlRespond={respondHitl}
          />
        </div>

        {/* Right Pane: Tabs */}
        <div className="w-[55%] flex flex-col bg-background min-h-0">
          <Tabs defaultValue="logs" className="w-full h-full flex flex-col min-h-0">
            <div className="border-b border-border px-4 py-2 flex-shrink-0 bg-card">
              <TabsList className="bg-muted border border-border">
                <TabsTrigger value="logs">Agent Logs</TabsTrigger>
                <TabsTrigger value="preview">Live Preview</TabsTrigger>
              </TabsList>
            </div>
            
            <TabsContent value="logs" className="flex-1 overflow-hidden m-0 border-none p-0 outline-none data-[state=active]:flex flex-col min-h-0">
              <LogsPanel logs={logs} />
            </TabsContent>
            
            <TabsContent value="preview" className="flex-1 overflow-hidden m-0 border-none p-0 outline-none data-[state=active]:flex flex-col min-h-0">
              {daytonaUrl ? (
                <DaytonaPreview url={daytonaUrl} />
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-muted-foreground bg-black/90 p-8 text-center flex-1">
                  <MonitorPlay size={48} className="mb-4 opacity-50 text-blue-500" />
                  <p className="text-lg font-mono">Sandbox not started.</p>
                  <p className="text-sm opacity-70 mt-2 font-mono">
                    The live preview will appear here once the App Developer agent provisions the Daytona environment.
                  </p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
