import { Message } from '../types/chat';
import { Bot, User, RefreshCw, ChevronDown, ChevronUp, Code2, Settings } from 'lucide-react';
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import SyntaxHighlighter from "react-syntax-highlighter/dist/esm/prism";
import { dracula } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { clsx } from "clsx";
import { useState } from "react";

interface ChatMessageProps {
  message: Message;
}

// Component for individual message chunks
function MessageChunkComponent({ chunk, index }: { chunk: any, index: number }) {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Check if this is a tool message
  const isToolMessage = chunk.type === 'ToolMessage' || chunk.node.includes('_agent') || chunk.content.includes('tool_code');
  
  // Get agent display name
  const getAgentName = (node: string) => {
    switch (node) {
      case 'user':
        return 'You';
      case 'event_schedular_agent':
        return 'Event Scheduler';
      case 'email_agent':
        return 'Email Manager';
      case 'notification_agent':
        return 'Notification Service';
      case 'background_email_agent':
        return 'Email Background Service';
      case 'supervisor_agent':
        return 'Supervisor';
      default:
        return node.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  };

  // Get agent icon
  const getAgentIcon = (node: string) => {
    if (node === 'user') return <User className="w-3 h-3" />;
    if (node.includes('_agent') || isToolMessage) return <Settings className="w-3 h-3" />;
    return <Bot className="w-3 h-3" />;
  };

  // Get agent color
  const getAgentColor = (node: string) => {
    switch (node) {
      case 'user':
        return 'bg-gray-700 dark:bg-gray-600';
      case 'event_schedular_agent':
        return 'bg-blue-500 dark:bg-blue-600';
      case 'email_agent':
        return 'bg-green-500 dark:bg-green-600';
      case 'notification_agent':
        return 'bg-purple-500 dark:bg-purple-600';
      case 'background_email_agent':
        return 'bg-orange-500 dark:bg-orange-600';
      case 'supervisor_agent':
        return 'bg-red-500 dark:bg-red-600';
      default:
        return 'bg-primary dark:bg-primary-dark';
    }
  };

  // Truncate content for tool messages
  const getTruncatedContent = (content: string, maxLength: number = 100) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  return (
    <div className={clsx(
      'mb-3 last:mb-0',
      isToolMessage && 'bg-gray-50 dark:bg-gray-800/30 rounded-lg p-3 border border-gray-200 dark:border-gray-700'
    )}>
      {/* Agent header */}
      <div className="flex items-center gap-2 mb-2">
        <div className={clsx(
          'w-5 h-5 rounded-full flex items-center justify-center text-white',
          getAgentColor(chunk.node)
        )}>
          {getAgentIcon(chunk.node)}
        </div>
        <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
          {getAgentName(chunk.node)}
        </span>
        {isToolMessage && (
          <div className="flex items-center gap-1 ml-auto">
            <Code2 className="w-3 h-3 text-gray-400" />
            <span className="text-xs text-gray-400">Tool Output</span>
          </div>
        )}
      </div>

      {/* Content */}
      {isToolMessage ? (
        <div>
          {/* Collapsed view */}
          <div 
            className="cursor-pointer select-none"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            <div className="flex items-center justify-between p-2 bg-gray-100 dark:bg-gray-700 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {isExpanded ? 'Hide' : 'Show'} tool execution details
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  ({chunk.content.length} characters)
                </span>
              </div>
              {isExpanded ? 
                <ChevronUp className="w-4 h-4 text-gray-500" /> : 
                <ChevronDown className="w-4 h-4 text-gray-500" />
              }
            </div>
          </div>

          {/* Preview when collapsed */}
          {!isExpanded && (
            <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs font-mono text-gray-600 dark:text-gray-400 overflow-hidden">
              {getTruncatedContent(chunk.content)}
            </div>
          )}

          {/* Full content when expanded */}
          {isExpanded && (
            <div className="mt-2">
              <div className="prose prose-gray dark:prose-invert prose-p:leading-relaxed prose-pre:p-0 prose-pre:rounded-lg prose-pre:bg-transparent max-w-none text-gray-700 dark:text-gray-300 text-sm">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ node, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || "");
                      
                      return match ? (
                        <div className="rounded-lg overflow-hidden bg-gray-900 my-2">
                          <div className="flex items-center justify-between bg-gray-800 px-3 py-1.5 text-gray-400">
                            <span className="text-xs font-medium">{match[1]}</span>
                            <button className="text-xs hover:text-white transition-colors" onClick={() => {
                              navigator.clipboard.writeText(String(children).replace(/\n$/, ""))
                            }}>
                              Copy
                            </button>
                          </div>
                          <SyntaxHighlighter
                            {...props}
                            style={dracula}
                            language={match[1]}
                            PreTag="div"
                            customStyle={{
                              margin: 0,
                              paddingTop: '0.75em',
                              paddingBottom: '0.75em',
                              borderRadius: 0,
                              fontSize: '0.8rem'
                            }}
                          >
                            {String(children).replace(/\n$/, "")}
                          </SyntaxHighlighter>
                        </div>
                      ) : (
                        <code className="bg-gray-100 dark:bg-gray-800 text-red-600 dark:text-red-400 px-1.5 py-0.5 rounded text-xs font-mono" {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {chunk.content}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Regular message content */
        <div className="prose prose-gray dark:prose-invert prose-p:leading-relaxed prose-pre:p-0 prose-pre:rounded-lg prose-pre:bg-transparent max-w-none text-gray-700 dark:text-gray-300 break-words">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || "");
                
                return match ? (
                  <div className="rounded-lg overflow-hidden bg-gray-900 my-4">
                    <div className="flex items-center justify-between bg-gray-800 px-4 py-2 text-gray-400">
                      <span className="text-xs font-medium">{match[1]}</span>
                      <button className="text-xs hover:text-white transition-colors" onClick={() => {
                        navigator.clipboard.writeText(String(children).replace(/\n$/, ""))
                      }}>
                        Copy
                      </button>
                    </div>
                    <SyntaxHighlighter
                      {...props}
                      style={dracula}
                      language={match[1]}
                      PreTag="div"
                      customStyle={{
                        margin: 0,
                        paddingTop: '1em',
                        paddingBottom: '1em',
                        borderRadius: 0
                      }}
                    >
                      {String(children).replace(/\n$/, "")}
                    </SyntaxHighlighter>
                  </div>
                ) : (
                  <code className="bg-gray-100 dark:bg-gray-800 text-red-600 dark:text-red-400 px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                    {children}
                  </code>
                );
              },
              a: ({ node, ...props }) => (
                <a 
                  {...props} 
                  className="text-primary dark:text-primary-dark hover:underline break-all"
                  target="_blank"
                  rel="noopener noreferrer"
                />
              ),
              p: ({ node, ...props }) => (
                <p {...props} className="my-2 break-words" />
              ),
              ul: ({ node, ...props }) => (
                <ul {...props} className="list-disc pl-6 my-3" />
              ),
              ol: ({ node, ...props }) => (
                <ol {...props} className="list-decimal pl-6 my-3" />
              ),
              li: ({ node, ...props }) => (
                <li {...props} className="my-1 break-words" />
              ),
              h1: ({ node, ...props }) => (
                <h1 {...props} className="text-2xl font-bold mt-6 mb-4 break-words" />
              ),
              h2: ({ node, ...props }) => (
                <h2 {...props} className="text-xl font-bold mt-5 mb-3 break-words" />
              ),
              h3: ({ node, ...props }) => (
                <h3 {...props} className="text-lg font-bold mt-4 mb-2 break-words" />
              ),
              blockquote: ({ node, ...props }) => (
                <blockquote {...props} className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic my-4 text-gray-700 dark:text-gray-300 break-words" />
              ),
              table: ({ node, ...props }) => (
                <div className="overflow-x-auto my-4">
                  <table {...props} className="border-collapse w-full text-sm" />
                </div>
              ),
              th: ({ node, ...props }) => (
                <th {...props} className="border border-gray-300 dark:border-gray-700 px-4 py-2 text-left bg-gray-100 dark:bg-gray-800 break-words" />
              ),
              td: ({ node, ...props }) => (
                <td {...props} className="border border-gray-300 dark:border-gray-700 px-4 py-2 break-words" />
              ),
            }}
          >
            {chunk.content}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isAssistant = message.role != 'user';
  const isLoading = message.isLoading === true;
  
  // Group chunks by node to show them together
  const groupedChunks = message.response?.reduce((acc, chunk, index) => {
    const key = chunk.node;
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push({ ...chunk, originalIndex: index });
    return acc;
  }, {} as Record<string, any[]>) || {};

  return (
    <div className={clsx(
      'py-6 px-4 md:px-6 transition-colors duration-200',
      isAssistant ? 'bg-gray-50 dark:bg-gray-800/50' : 'bg-white dark:bg-gray-900',
      isLoading && 'animate-pulse'
    )}>
      <div className="max-w-4xl mx-auto">
        {/* Loading State */}
        {isLoading ? (
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 rounded-full bg-primary dark:bg-primary-dark flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="flex items-center gap-2 text-gray-500 dark:text-white">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Thinking...</span>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Render each group of chunks */}
            {Object.entries(groupedChunks).map(([node, chunks]) => (
              <div key={node} className="space-y-2">
                {chunks.map((chunk, index) => (
                  <MessageChunkComponent 
                    key={`${node}-${chunk.originalIndex || index}`} 
                    chunk={chunk} 
                    index={chunk.originalIndex || index} 
                  />
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}