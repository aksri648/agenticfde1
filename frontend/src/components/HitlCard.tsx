import { Check, X, AlertTriangle } from 'lucide-react';

interface HitlCardProps {
  plan: string;
  onRespond: (feedback: string) => void;
}

export default function HitlCard({ plan, onRespond }: HitlCardProps) {
  return (
    <div className="bg-yellow-900/20 border border-yellow-700/50 rounded-xl p-4 animate-pulse-border">
      <div className="flex items-center gap-2 mb-3">
        <AlertTriangle size={18} className="text-yellow-500" />
        <h3 className="text-yellow-500 font-bold text-sm">Human Approval Required</h3>
      </div>
      <div className="bg-black/40 rounded-lg p-3 mb-4">
        <p className="text-sm text-gray-300 whitespace-pre-wrap">{plan}</p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => onRespond('Approved. Proceed.')}
          className="flex-1 bg-green-600 hover:bg-green-500 py-2.5 rounded-lg font-semibold flex items-center justify-center gap-2 text-sm transition-colors"
        >
          <Check size={16} />
          Approve
        </button>
        <button
          onClick={() => onRespond('Rejected. Abort.')}
          className="flex-1 bg-red-600 hover:bg-red-500 py-2.5 rounded-lg font-semibold flex items-center justify-center gap-2 text-sm transition-colors"
        >
          <X size={16} />
          Reject
        </button>
      </div>
    </div>
  );
}
