import { Message } from '../types/chat';
import { Bot, User, RefreshCw } from 'lucide-react';
import FunctionCallItem from './FunctionCall';
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import SyntaxHighlighter from "react-syntax-highlighter/dist/esm/prism";
import { dracula } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { clsx } from "clsx";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isAssistant = message.role === 'bot';
  const isLoading = message.isLoading === true;

  return (
    <div className={clsx(
      'py-6 px-4 md:px-6 transition-colors duration-200',
      isAssistant ? 'bg-gray-50 dark:bg-gray-800/50' : 'bg-white dark:bg-gray-900',
      isLoading && 'animate-pulse'
    )}>
      <div className="max-w-2xl mx-auto flex gap-4">
        {/* Avatar Section */}
        <div className={clsx(
          'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
          isAssistant 
            ? 'bg-primary dark:bg-primary-dark' 
            : 'bg-gray-700 dark:bg-gray-600'
        )}>
          {isAssistant 
            ? <Bot className="w-4 h-4 text-white" /> 
            : <User className="w-4 h-4 text-white" />}
        </div>

        {/* Message Content */}
        <div className="flex-1">
          <div className="font-medium text-sm mb-1 text-gray-700 dark:text-white">
            {isAssistant ? 'AI Assistant' : 'You'}
          </div>

          {/* Loading State */}
          {isLoading ? (
            <div className="flex items-center gap-2 text-gray-500 dark:text-white">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Thinking...</span>
            </div>
          ) : (
            <>
              {/* Function Calls if available */}
              {  
                message.data && message.data.map((messageChunk, index) => (
                  
                  messageChunk.type == "function_call" ?
                  
                  <div className="mb-4" key={index}>
                    <FunctionCallItem key={messageChunk.function_call.name} functionCall={messageChunk.function_call} />
                  </div> :

                  <div key={index} className="prose prose-gray dark:prose-invert prose-p:leading-relaxed prose-pre:p-0 prose-pre:rounded-lg prose-pre:bg-transparent max-w-none text-gray-500 dark:text-gray-300">
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
                          className="text-primary dark:text-primary-dark hover:underline"
                          target="_blank"
                          rel="noopener noreferrer"
                        />
                      ),
                      p: ({ node, ...props }) => (
                        <p {...props} className="my-2" />
                      ),
                      ul: ({ node, ...props }) => (
                        <ul {...props} className="list-disc pl-6 my-3" />
                      ),
                      ol: ({ node, ...props }) => (
                        <ol {...props} className="list-decimal pl-6 my-3" />
                      ),
                      li: ({ node, ...props }) => (
                        <li {...props} className="my-1" />
                      ),
                      h1: ({ node, ...props }) => (
                        <h1 {...props} className="text-2xl font-bold mt-6 mb-4" />
                      ),
                      h2: ({ node, ...props }) => (
                        <h2 {...props} className="text-xl font-bold mt-5 mb-3" />
                      ),
                      h3: ({ node, ...props }) => (
                        <h3 {...props} className="text-lg font-bold mt-4 mb-2" />
                      ),
                      blockquote: ({ node, ...props }) => (
                        <blockquote {...props} className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic my-4 text-gray-700 dark:text-gray-300" />
                      ),
                      table: ({ node, ...props }) => (
                        <div className="overflow-x-auto my-4">
                          <table {...props} className="border-collapse w-full text-sm" />
                        </div>
                      ),
                      th: ({ node, ...props }) => (
                        <th {...props} className="border border-gray-300 dark:border-gray-700 px-4 py-2 text-left bg-gray-100 dark:bg-gray-800" />
                      ),
                      td: ({ node, ...props }) => (
                        <td {...props} className="border border-gray-300 dark:border-gray-700 px-4 py-2" />
                      ),
                    }}
                  >
                    {messageChunk.value}
                  </ReactMarkdown>
                  </div>
                ))
              }
            </>
          )}
        </div>
      </div>
    </div>
  );
}