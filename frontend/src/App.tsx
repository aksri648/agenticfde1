import { useSocket } from './hooks/useSocket';
import ChatPanel from './components/ChatPanel';
import LogsPanel from './components/LogsPanel';
import DaytonaPreview from './components/DaytonaPreview';

const AGENTS = [
  { id: 'pm', label: 'PM Agent', color: 'bg-purple-600' },
  { id: 'developer', label: 'Developer', color: 'bg-green-600' },
  { id: 'deployer', label: 'Deployer', color: 'bg-orange-600' },
  { id: 'maintainer', label: 'Maintainer', color: 'bg-cyan-600' },
  { id: 'llm_deployer', label: 'LLM Deployer', color: 'bg-pink-600' },
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
    <div className="flex flex-col h-screen bg-gray-950 text-white">
      {/* Top Bar */}
      <header className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-gray-950">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold">
            5-Agent <span className="text-blue-400">System</span>
          </h1>
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
        </div>
        <div className="flex gap-2">
          {AGENTS.map(a => (
            <button
              key={a.id}
              onClick={() => {}}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeAgent === a.id
                  ? `${a.color} text-white shadow-lg`
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              {a.label}
            </button>
          ))}
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Pane: Chat */}
        <div className="w-1/3 border-r border-gray-800">
          <ChatPanel
            messages={messages}
            hitlPlan={hitlPlan}
            onSend={handleSend}
            onHitlRespond={respondHitl}
          />
        </div>

        {/* Middle Pane: Logs */}
        <div className={`${daytonaUrl ? 'w-1/3 border-r border-gray-800' : 'w-2/3'}`}>
          <LogsPanel logs={logs} />
        </div>

        {/* Right Pane: Daytona Preview */}
        {daytonaUrl && (
          <div className="w-1/3 bg-gray-900">
            <DaytonaPreview url={daytonaUrl} />
          </div>
        )}
      </div>
    </div>
  );
}
