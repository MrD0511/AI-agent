import { Menu, Bot, Sun, Moon, Wrench, Send, Paperclip, Zap, X, BarChart3, Bell } from "lucide-react"
import { useEffect, useState, useRef } from "react"
import { Message, MessageChunk } from "./types/chat"
import { ChatMessage } from "./components/ChatMessages"
import { Dashboard } from "./components/Dashboard"
import { NotificationPanel } from "./components/NotificationPanel"
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
  const [activeTab, setActiveTab] = useState<'chat' | 'dashboard' | 'notifications'>('chat');
  
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
      node: "user", content: input, type: "text"
    }
    const message: Message = {
      id: Date.now().toString(),
      role: 'user',
      response: [userMessageChunk],
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
        response: [{node: "bot", content: "Thinking...", type: "text"}],
        isLoading: true
      };
      
      setMessages((prev) => [...prev, loadingMessage]);

      await sendQuery(input, (chunk) => {
        // Update the last message with the new chunk
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          
          if(chunk.type == "end"){
            return prev
          }
          const newMessageChunk: MessageChunk = {
            node: chunk.node,
            content: chunk.content,
            type: chunk.type
          };
          console.log("New message chunk:", newMessageChunk);
          
          if(last.isLoading){
            const updated = {
              ...last,
              isLoading: false,
              response: [newMessageChunk],
            };
            return [...prev.slice(0, -1), updated];
          }else{
            const updated = {
              ...last,
              isLoading: false,
              response: [...last.response, newMessageChunk]
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
          response: [{node: "bot", content: "Sorry, I couldn't process your request. Please try again.", type: "error"}],
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
          <span className="font-medium text-gray-800 dark:text-gray-200">AI Personal Manager</span>
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

      {/* Tab Navigation */}
      <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4">
        <div className="flex space-x-8">
          <button
            onClick={() => setActiveTab('chat')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'chat'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <div className="flex items-center">
              <Bot className="w-4 h-4 mr-2" />
              Chat
            </div>
          </button>
          
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'dashboard'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <div className="flex items-center">
              <BarChart3 className="w-4 h-4 mr-2" />
              Dashboard
            </div>
          </button>
          
          <button
            onClick={() => setActiveTab('notifications')}
            className={`py-4 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'notifications'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
          >
            <div className="flex items-center">
              <Bell className="w-4 h-4 mr-2" />
              Notifications
            </div>
          </button>
        </div>
      </nav>

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

      {/* Tab Content */}
      <main className="flex-1 overflow-hidden">
        {activeTab === 'chat' && (
          <div className="h-full">
            {messages.length === 0 ? (
              // Empty state with prompt suggestions
              <div className="h-full flex flex-col items-center justify-center p-4">
                <div className="text-center mb-8">
                  <div className="inline-block p-3 bg-primary/10 dark:bg-primary-dark/20 rounded-full mb-4">
                    <Bot className="h-8 w-8 text-primary dark:text-primary-dark" />
                  </div>
                  <h1 className="text-2xl font-medium text-gray-900 dark:text-white mb-2">How can I help you today?</h1>
                  <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
                    Ask me anything, from managing your emails to scheduling events, or try one of the suggestions below.
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                  <button 
                    onClick={() => setInput("Check my emails and summarize any important ones.")}
                    className="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md text-left border border-gray-200 dark:border-gray-700 transition-shadow"
                  >
                    <h3 className="font-medium text-gray-900 dark:text-white mb-1">� Email Management</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Check and summarize important emails</p>
                  </button>
                  
                  <button 
                    onClick={() => setInput("Create a reminder for my meeting tomorrow at 2 PM.")}
                    className="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md text-left border border-gray-200 dark:border-gray-700 transition-shadow"
                  >
                    <h3 className="font-medium text-gray-900 dark:text-white mb-1">⏰ Reminders</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Set up reminders for important events</p>
                  </button>
                  
                  <button 
                    onClick={() => setInput("What events do I have coming up this week?")}
                    className="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md text-left border border-gray-200 dark:border-gray-700 transition-shadow"
                  >
                    <h3 className="font-medium text-gray-900 dark:text-white mb-1">� Schedule</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Check upcoming events and schedule</p>
                  </button>
                  
                  <button 
                    onClick={() => setInput("Send me a notification when it's time for lunch.")}
                    className="p-3 bg-white dark:bg-gray-800 rounded-xl shadow-sm hover:shadow-md text-left border border-gray-200 dark:border-gray-700 transition-shadow"
                  >
                    <h3 className="font-medium text-gray-900 dark:text-white mb-1">🔔 Notifications</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Set up custom notifications</p>
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
          </div>
        )}

        {activeTab === 'dashboard' && (
          <div className="h-full overflow-y-auto">
            <Dashboard isDark={isDark} />
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="h-full overflow-y-auto p-6">
            <NotificationPanel isDark={isDark} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;