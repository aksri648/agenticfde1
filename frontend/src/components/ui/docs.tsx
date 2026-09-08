import { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import mermaid from 'mermaid';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
// @ts-ignore
import architectureDocs from '../../../../docs/architecture.md?raw';

mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  securityLevel: 'loose',
});

const Mermaid = ({ chart }: { chart: string }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      mermaid.render(`mermaid-${Math.random().toString(36).substring(2)}`, chart).then(({ svg }) => {
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      });
    }
  }, [chart]);

  return <div ref={containerRef} className="flex justify-center my-8 overflow-x-auto" />;
};

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-black text-white p-8 overflow-y-auto">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <Link to="/" className="inline-flex items-center text-cyan-400 hover:text-cyan-300 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Link>
        </div>
        
        <div className="prose prose-invert prose-cyan max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, inline, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || '');
                const isMermaid = match && match[1] === 'mermaid';
                
                if (!inline && isMermaid) {
                  return <Mermaid chart={String(children).replace(/\n$/, '')} />;
                }
                
                return !inline ? (
                  <div className="bg-white/5 rounded-lg p-4 my-4 overflow-x-auto border border-white/10">
                    <code className={className} {...props}>
                      {children}
                    </code>
                  </div>
                ) : (
                  <code className="bg-white/10 px-1.5 py-0.5 rounded text-cyan-300" {...props}>
                    {children}
                  </code>
                );
              },
              h1: ({node, ...props}) => <h1 className="text-4xl font-bold mb-6 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-orange-400" {...props} />,
              h2: ({node, ...props}) => <h2 className="text-2xl font-semibold mt-12 mb-6 text-white/90 border-b border-white/10 pb-2" {...props} />,
              h3: ({node, ...props}) => <h3 className="text-xl font-medium mt-8 mb-4 text-cyan-200" {...props} />,
              p: ({node, ...props}) => <p className="text-white/70 leading-relaxed mb-6" {...props} />,
              ul: ({node, ...props}) => <ul className="list-disc pl-6 mb-6 text-white/70 space-y-2" {...props} />,
              li: ({node, ...props}) => <li className="text-white/70" {...props} />,
              a: ({node, ...props}) => <a className="text-cyan-400 hover:text-cyan-300 underline underline-offset-4" {...props} />,
            }}
          >
            {architectureDocs}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
