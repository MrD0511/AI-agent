import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Calendar, 
  Bell, 
  Clock, 
  AlertCircle, 
  CheckCircle, 
  RefreshCw,
  Play,
  Mail,
  Settings
} from 'lucide-react';
import { apiService, SystemStatus, DetailedStatus, Reminder, Event } from '../api';

interface DashboardProps {
  isDark: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({ isDark }) => {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [detailedStatus, setDetailedStatus] = useState<DetailedStatus | null>(null);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [upcomingEvents, setUpcomingEvents] = useState<Event[]>([]);
  const [ongoingEvents, setOngoingEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [
        statusResponse,
        detailedStatusResponse,
        remindersResponse,
        upcomingEventsResponse,
        ongoingEventsResponse
      ] = await Promise.all([
        apiService.getHealth(),
        apiService.getStatus(),
        apiService.getReminders(),
        apiService.getUpcomingEvents(),
        apiService.getOngoingEvents()
      ]);

      setStatus(statusResponse);
      setDetailedStatus(detailedStatusResponse);
      setReminders(remindersResponse.reminders);
      setUpcomingEvents(upcomingEventsResponse.events);
      setOngoingEvents(ongoingEventsResponse.events);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const triggerAction = async (action: 'email' | 'reminder' | 'deadline') => {
    try {
      let response;
      switch (action) {
        case 'email':
          response = await apiService.triggerEmailCheck();
          break;
        case 'reminder':
          response = await apiService.triggerReminderCheck();
          break;
        case 'deadline':
          response = await apiService.triggerDeadlineCheck();
          break;
      }
      
      // Refresh data after triggering
      fetchData();
      
      // Show success message (you can implement a toast system)
      console.log(`${action} check triggered:`, response.message);
    } catch (err) {
      console.error(`Failed to trigger ${action} check:`, err);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600 dark:text-gray-400">Loading dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <AlertCircle className="w-8 h-8 text-red-500" />
        <span className="ml-2 text-red-600 dark:text-red-400">{error}</span>
        <button 
          onClick={fetchData}
          className="ml-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    );
  }

  const formatTime = (timeString: string) => {
    return new Date(timeString).toLocaleString();
  };

  const getImportanceColor = (level: string) => {
    switch (level) {
      case 'high': return 'text-red-500 bg-red-100 dark:bg-red-900';
      case 'medium': return 'text-yellow-500 bg-yellow-100 dark:bg-yellow-900';
      case 'low': return 'text-green-500 bg-green-100 dark:bg-green-900';
      default: return 'text-gray-500 bg-gray-100 dark:bg-gray-900';
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* System Status */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            System Status
          </h2>
          <button
            onClick={fetchData}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center">
            {status?.scheduler_running ? (
              <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
            )}
            <span className="text-gray-700 dark:text-gray-300">
              Scheduler: {status?.scheduler_running ? 'Running' : 'Stopped'}
            </span>
          </div>
          
          <div className="flex items-center">
            <Settings className="w-5 h-5 text-blue-500 mr-2" />
            <span className="text-gray-700 dark:text-gray-300">
              Active Jobs: {status?.active_jobs}
            </span>
          </div>
          
          <div className="flex items-center">
            <Clock className="w-5 h-5 text-purple-500 mr-2" />
            <span className="text-gray-700 dark:text-gray-300">
              Last Update: {status?.timestamp ? formatTime(status.timestamp) : 'N/A'}
            </span>
          </div>
        </div>
      </div>

      {/* Manual Triggers */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <Play className="w-5 h-5 mr-2" />
          Manual Triggers
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => triggerAction('email')}
            className="flex items-center justify-center p-4 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-lg hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
          >
            <Mail className="w-5 h-5 mr-2" />
            Check Emails
          </button>
          
          <button
            onClick={() => triggerAction('reminder')}
            className="flex items-center justify-center p-4 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-lg hover:bg-green-200 dark:hover:bg-green-800 transition-colors"
          >
            <Bell className="w-5 h-5 mr-2" />
            Check Reminders
          </button>
          
          <button
            onClick={() => triggerAction('deadline')}
            className="flex items-center justify-center p-4 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-lg hover:bg-purple-200 dark:hover:bg-purple-800 transition-colors"
          >
            <Calendar className="w-5 h-5 mr-2" />
            Check Deadlines
          </button>
        </div>
      </div>

      {/* Active Jobs */}
      {detailedStatus?.jobs && detailedStatus.jobs.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Settings className="w-5 h-5 mr-2" />
            Background Jobs
          </h2>
          
          <div className="space-y-3">
            {detailedStatus.jobs.map((job) => (
              <div key={job.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">{job.name}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">ID: {job.id}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Next Run: {job.next_run ? formatTime(job.next_run) : 'Not scheduled'}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">{job.trigger}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reminders */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <Bell className="w-5 h-5 mr-2" />
          Upcoming Reminders ({reminders.length})
        </h2>
        
        {reminders.length > 0 ? (
          <div className="space-y-3">
            {reminders.slice(0, 5).map((reminder) => (
              <div key={reminder.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">{reminder.title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{reminder.notification_message}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {formatTime(reminder.reminder_time)}
                    </p>
                    {reminder.is_notification_sent && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Sent
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 dark:text-gray-400">No upcoming reminders</p>
        )}
      </div>

      {/* Events */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upcoming Events */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Calendar className="w-5 h-5 mr-2" />
            Upcoming Events ({upcomingEvents.length})
          </h2>
          
          {upcomingEvents.length > 0 ? (
            <div className="space-y-3">
              {upcomingEvents.slice(0, 3).map((event) => (
                <div key={event.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">{event.title}</h3>
                      {event.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">{event.description}</p>
                      )}
                    </div>
                    <div className="text-right">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${getImportanceColor(event.importance_level)}`}>
                        {event.importance_level}
                      </span>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {formatTime(event.start_time)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400">No upcoming events</p>
          )}
        </div>

        {/* Ongoing Events */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Ongoing Events ({ongoingEvents.length})
          </h2>
          
          {ongoingEvents.length > 0 ? (
            <div className="space-y-3">
              {ongoingEvents.slice(0, 3).map((event) => (
                <div key={event.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-gray-900 dark:text-white">{event.title}</h3>
                      {event.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">{event.description}</p>
                      )}
                    </div>
                    <div className="text-right">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${getImportanceColor(event.importance_level)}`}>
                        {event.importance_level}
                      </span>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Started: {formatTime(event.start_time)}
                      </p>
                      {event.end_time && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Ends: {formatTime(event.end_time)}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400">No ongoing events</p>
          )}
        </div>
      </div>
    </div>
  );
};
