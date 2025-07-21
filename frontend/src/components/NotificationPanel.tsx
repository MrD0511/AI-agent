import React, { useState } from 'react';
import { Send, Bell, AlertCircle, CheckCircle } from 'lucide-react';
import { apiService } from '../api';

interface NotificationPanelProps {
  isDark: boolean;
}

export const NotificationPanel: React.FC<NotificationPanelProps> = ({ isDark }) => {
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [statusMessage, setStatusMessage] = useState('');

  const handleSendNotification = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim()) return;
    
    setSending(true);
    setStatus('idle');
    
    try {
      const response = await apiService.sendNotification(message);
      setStatus('success');
      setStatusMessage(response.message || 'Notification sent successfully!');
      setMessage('');
      
      // Clear status after 3 seconds
      setTimeout(() => {
        setStatus('idle');
        setStatusMessage('');
      }, 3000);
    } catch (error) {
      setStatus('error');
      setStatusMessage('Failed to send notification. Please try again.');
      console.error('Notification send error:', error);
      
      // Clear error after 5 seconds
      setTimeout(() => {
        setStatus('idle');
        setStatusMessage('');
      }, 5000);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
        <Bell className="w-5 h-5 mr-2" />
        Send Manual Notification
      </h2>
      
      <form onSubmit={handleSendNotification} className="space-y-4">
        <div>
          <label htmlFor="notification-message" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Notification Message
          </label>
          <textarea
            id="notification-message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Enter your notification message..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white resize-none"
            disabled={sending}
          />
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex-1">
            {status === 'success' && (
              <div className="flex items-center text-green-600 dark:text-green-400">
                <CheckCircle className="w-4 h-4 mr-2" />
                <span className="text-sm">{statusMessage}</span>
              </div>
            )}
            
            {status === 'error' && (
              <div className="flex items-center text-red-600 dark:text-red-400">
                <AlertCircle className="w-4 h-4 mr-2" />
                <span className="text-sm">{statusMessage}</span>
              </div>
            )}
          </div>
          
          <button
            type="submit"
            disabled={!message.trim() || sending}
            className="ml-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-blue-500 dark:hover:bg-blue-600"
          >
            {sending ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                Sending...
              </>
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Send Notification
              </>
            )}
          </button>
        </div>
      </form>
      
      <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
        <p className="text-xs text-gray-600 dark:text-gray-400">
          💡 <strong>Tip:</strong> This will send a system notification that appears in your notification center.
          Make sure your browser allows notifications from this site.
        </p>
      </div>
    </div>
  );
};
