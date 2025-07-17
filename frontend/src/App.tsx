import { Menu, Bot, Sun, Moon, Wrench, Send, Paperclip, Zap, X } from "lucide-react"
import { useEffect, useState, useRef } from "react"
import { Message, MessageChunk } from "./types/chat"
import { ChatMessage } from "./components/ChatMessages"
import "./App.css"
import { sendQuery } from "./api"

function App() {
  const [isDark, setIsDark] = useState<boolean>(() => {
    const savedMode = localStorage.getItem("isDarkMode");
    return savedMode ? savedMode === "true" : true;
  });
  const [input, setInput] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [showSettings, setShowSettings] = useState<boolean>(false);
  
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);  

  useEffect(() => {
    if(isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem("isDarkMode", isDark.toString());
  }, [isDark]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const newHeight = Math.min(textareaRef.current.scrollHeight, 150); // Max height of 150px
      textareaRef.current.style.height = `${newHeight}px`;
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    adjustTextareaHeight();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if(!input.trim() || isSubmitting) return;
    
    setIsSubmitting(true);
    
    const userMessageChunk : MessageChunk = {
      type: "content", value: input
    }
    const message: Message = {
      id: Date.now().toString(),
      role: 'user',
      data: [userMessageChunk],
    };

    setMessages((prev) => [...prev, message]);
    setInput('');
    
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    
    try {
      // Add a loading message first
      const loadingId = Date.now().toString() + "-loading";
      const loadingMessage: Message = {
        id: loadingId,
        role: 'bot',
        data: [{type: "content", value: "Thinking..."}],
        isLoading: true
      };
      
      setMessages((prev) => [...prev, loadingMessage]);

      await sendQuery(input, (chunk) => {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          
          if(chunk.type == "end"){
            return prev
          }
          
          var newMessageChunk : MessageChunk = chunk.type == "function_call" ? {
            type: chunk.type,
            function_call: chunk.data
          } : {
            type: chunk.type,
            value: chunk.data
          }
          
          if(last.isLoading){
            const updated = {
              ...last,
              isLoading: false,
              data: [newMessageChunk],
            };
            return [...prev.slice(0, -1), updated];
          }else{
            const updated = {
              ...last,
              isLoading: false,
              data: [...last.data, newMessageChunk]
            };
            return [...prev.slice(0, -1), updated];
          }
          
        });
      });
      
      // const response = await chatMutation.mutateAsync(input);
      
      // Remove the loading message and add the real response
    } catch (error) {
      console.error("Error fetching answer:", error);
      // Remove loading message and add error message
      setMessages((prev) => {
        const filtered = prev.filter(msg => !msg.isLoading);
        const errorMessage: Message = {
          id: Date.now().toString() + "-error",
          role: 'bot',
          data: [{type: "error", value: "Sorry, I couldn't process your request. Please try again."}],
          isError: true
        };
        return [...filtered, errorMessage];
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-gray-50 dark:bg-gray-900 w-full h-screen flex flex-col">
      {/* Header */}
      <header className="flex p-3 bg-white dark:bg-gray-800 shadow-sm backdrop-blur-lg items-center justify-between sticky top-0 z-10">
        <div className="flex gap-3 items-center">
          <button 
            className="h-8 w-8 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center justify-center transition-colors"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Menu className="h-5 w-5 text-gray-700 dark:text-gray-300" />
          </button>
          <div className="p-2 bg-primary/90 dark:bg-primary-dark/90 rounded-full text-white flex items-center justify-center">
            <Bot className="h-5 w-5"/>
          </div>
          <span className="font-medium text-gray-800 dark:text-gray-200">AI Assistant</span>
        </div>
        <div className="flex gap-2 items-center">
          <button 
            onClick={() => setIsDark(!isDark)} 
            className="h-8 w-8 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center justify-center transition-colors"
          >
            {isDark ? 
              <Sun className="h-5 w-5 text-gray-700 dark:text-gray-300"/> : 
              <Moon className="h-5 w-5 text-gray-700 dark:text-gray-300"/>
            }
          </button>
        </div>
      </header>

      {/* Settings panel (slide in from left) */}
      {showSettings && (
        <div className="fixed inset-0 z-20 bg-black bg-opacity-50" onClick={() => setShowSettings(false)}>
          <div 
            className="w-64 h-full bg-white dark:bg-gray-800 p-4 animate-slide-in shadow-lg"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">Settings</h2>
              <button onClick={() => setShowSettings(false)}>
                <X className="h-5 w-5 text-gray-700 dark:text-gray-300" />
              </button>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-700 dark:text-gray-300">Dark Mode</span>
                <button 
                  onClick={() => setIsDark(!isDark)}
                  className={`w-12 h-6 rounded-full p-1 transition-colors ${isDark ? 'bg-primary' : 'bg-gray-300'}`}
                >
                  <div 
                    className={`w-4 h-4 rounded-full bg-white transform transition-transform ${isDark ? 'translate-x-6' : 'translate-x-0'}`} 
                  />
                </button>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <button className="flex items-center gap-2 text-gray-700 dark:text-gray-300 hover:text-primary dark:hover:text-primary-dark">
                  <Wrench className="h-4 w-4" />
                  <span>Advanced Settings</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chat content */}
      <main className="flex-1 overflow-hidden relative">
        {messages.length === 0 ? (
          // Empty state with prompt suggestions
          <div className="h-full flex flex-col items-center justify-center p-4">
            <div className="text-center mb-8">
              <div className="inline-block p-3 bg-primary/10 dark:bg-primary-dark/20 rounded-full mb-4">
                <Bot className="h-8 w-8 text-primary dark:text-primary-dark" />
              </div>
              <h1 className="text-2xl font-medium text-gray-900 dark:text-white mb-2">How can I help you today?</h1>
              <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
                Ask me anything, from creative writing to coding help, or try one of the suggestions below.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
              <button 
                onClick={() => setInput("Write a short story about a space explorer discovering a new planet.")}
                className="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md text-left border border-gray-200 dark:border-gray-700 transition-shadow"
              >
                <h3 className="font-medium text-gray-900 dark:text-white mb-1">📝 Creative Writing</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Write a short story about space exploration</p>
              </button>
              
              <button 
                onClick={() => setInput("Explain quantum computing like I'm five years old.")}
                className="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md text-left border border-gray-200 dark:border-gray-700 transition-shadow"
              >
                <h3 className="font-medium text-gray-900 dark:text-white mb-1">🧠 Simple Explanation</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Explain quantum computing like I'm five</p>
              </button>
              
              <button 
                onClick={() => setInput("Help me debug this React code that's not updating state correctly.")}
                className="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md text-left border border-gray-200 dark:border-gray-700 transition-shadow"
              >
                <h3 className="font-medium text-gray-900 dark:text-white mb-1">💻 Code Help</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Help with debugging React code</p>
              </button>
              
              <button 
                onClick={() => setInput("Give me a healthy meal plan for the week with grocery list.")}
                className="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md text-left border border-gray-200 dark:border-gray-700 transition-shadow"
              >
                <h3 className="font-medium text-gray-900 dark:text-white mb-1">🥗 Meal Planning</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Create a healthy weekly meal plan</p>
              </button>
            </div>
            
            {/* Input form for empty state */}
            <form className="w-full max-w-2xl mt-8" onSubmit={handleSubmit}>
              <div className="relative w-full">
                <textarea
                  ref={textareaRef}
                  placeholder="Type your message here..."
                  className="w-full px-4 py-3 pr-16 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary dark:focus:ring-primary-dark resize-none min-h-[50px] text-gray-800 dark:text-gray-200 placeholder-gray-500 dark:placeholder-gray-400 shadow-sm"
                  value={input}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  rows={1}
                />
                <div className="absolute right-2 bottom-3 flex gap-2">
                  <button 
                    type="button"
                    className="p-2 text-gray-500 hover:text-primary dark:hover:text-primary-dark transition-colors"
                  >
                    <Paperclip className="h-5 w-5" />
                  </button>
                  <button 
                    type="submit"
                    disabled={!input.trim() || isSubmitting}
                    className={`p-2 rounded-full ${isSubmitting || !input.trim() ? 'bg-gray-400 dark:bg-gray-700 cursor-not-allowed' : 'bg-primary dark:bg-primary-dark hover:bg-primary/90 dark:hover:bg-primary-dark/90'} text-white transition-colors`}
                  >
                    {isSubmitting ? 
                      <div className="h-5 w-5 border-t-2 border-white rounded-full animate-spin"></div> : 
                      <Send className="h-5 w-5" />
                    }
                  </button>
                </div>
              </div>
            </form>
          </div>
        ) : (
          // Chat messages view with input at bottom
          <div className="flex flex-col h-full">
            <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700">
              {messages.map(message => (
                <ChatMessage key={message.id} message={message} />
              ))}
              <div ref={endOfMessagesRef} />
            </div>
            
            {/* Fixed input at bottom */}
            <div className="bg-gradient-to-t from-gray-50 via-gray-50 to-transparent dark:from-gray-900 dark:via-gray-900 dark:to-transparent pt-4 pb-4 px-4 sticky bottom-0">
              <form className="w-full max-w-2xl mx-auto" onSubmit={handleSubmit}>
                <div className="relative w-full">
                  <textarea
                    ref={textareaRef}
                    placeholder="Type your message here..."
                    className="w-full px-4 py-3 pr-16 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary dark:focus:ring-primary-dark resize-none min-h-[50px] max-h-[150px] overflow-y-auto text-gray-800 dark:text-gray-200 placeholder-gray-500 dark:placeholder-gray-400 shadow-sm"
                    value={input}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    rows={1}
                  />
                  <div className="absolute right-2 bottom-3 flex gap-2">
                    <button 
                      type="button"
                      className="p-2 text-gray-500 hover:text-primary dark:hover:text-primary-dark transition-colors"
                    >
                      <Paperclip className="h-5 w-5" />
                    </button>
                    <button 
                      type="button"
                      className="p-2 text-gray-500 hover:text-primary dark:hover:text-primary-dark transition-colors"
                    >
                      <Zap className="h-5 w-5" />
                    </button>
                    <button 
                      type="submit"
                      disabled={!input.trim() || isSubmitting}
                      className={`p-2 rounded-full ${isSubmitting || !input.trim() ? 'bg-gray-400 dark:bg-gray-700 cursor-not-allowed' : 'bg-primary dark:bg-primary-dark hover:bg-primary/90 dark:hover:bg-primary-dark/90'} text-white transition-colors`}
                    >
                      {isSubmitting ? 
                        <div className="h-5 w-5 border-t-2 border-white rounded-full animate-spin"></div> : 
                        <Send className="h-5 w-5" />
                      }
                    </button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;