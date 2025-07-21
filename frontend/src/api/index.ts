import axios from "axios";

// Define Base API URL
const API_BASE_URL = "http://localhost:8000"; // Replace with your actual API

// Create Axios Instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Generic GET request
export const getData = async <T>(endpoint: string): Promise<T> => {
  const response = await api.get<T>(endpoint);
  return response.data;
};

// Generic POST request
export const postData = async <T>(endpoint: string, data: any): Promise<T> => {
  const response = await api.post<T>(endpoint, data);
  return response.data;
};

// API Types
export interface Reminder {
  id: string;
  title: string;
  notification_message: string;
  reminder_time: string;
  is_notification_sent: boolean;
}

export interface Event {
  id: string;
  title: string;
  start_time: string;
  end_time?: string;
  importance_level: 'low' | 'medium' | 'high';
  description?: string;
}

export interface SystemStatus {
  status: string;
  scheduler_running: boolean;
  active_jobs: number;
  timestamp: string;
}

export interface DetailedStatus {
  scheduler_running: boolean;
  jobs: Array<{
    id: string;
    name: string;
    next_run: string | null;
    trigger: string;
  }>;
  system_time: string;
}

export interface ApiResponse {
  message?: string;
  timestamp?: string;
  [key: string]: any;
}

// API Service Functions
export const apiService = {
  // Health and Status
  getHealth: () => getData<SystemStatus>('/health'),
  getStatus: () => getData<DetailedStatus>('/status'),
  
  // Reminders
  getReminders: () => getData<{ reminders: Reminder[]; count: number }>('/reminders'),
  
  // Events
  getUpcomingEvents: () => getData<{ events: Event[]; count: number }>('/events/upcoming'),
  getOngoingEvents: () => getData<{ events: Event[]; count: number }>('/events/ongoing'),
  
  // Manual Triggers
  triggerEmailCheck: () => postData<ApiResponse>('/trigger/email-check', {}),
  triggerReminderCheck: () => postData<ApiResponse>('/trigger/reminder-check', {}),
  triggerDeadlineCheck: () => postData<ApiResponse>('/trigger/deadline-check', {}),
  
  // Notifications
  sendNotification: (message: string) => 
    postData<ApiResponse>(`/notification/send?message=${encodeURIComponent(message)}`, {}),
  
  // Chat
  chatWithAssistant: (message: string) => 
    postData<{
      message: string;
      responses: Array<{
        node: string;
        content: string;
        type: string;
      }>;
      timestamp: string;
    }>(`/chat?message=${encodeURIComponent(message)}`, {})
};

export const sendQuery = async (
  query: string,
  onMessage: (chunk: any) => void,
  onDone?: () => void,
  onError?: (err: any) => void
) => {
  try {
    const response = await fetch(`http://localhost:8000/chat?message=${encodeURIComponent(query)}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ query }),
    });

    if (!response.body) throw new Error("No response body");

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      
      const parts = buffer.split("\n\n");
      buffer = parts.pop() || ""; // keep incomplete chunk
      
      for (const part of parts) {
        if (part.startsWith("data:")) {
          const jsonStr = part.replace(/^data:\s*/, "");
          // console.log("Received chunk:", jsonStr);
          try {
            const parsed = JSON.parse(jsonStr);
            console.log("Parsed chunk:", parsed.content);
            onMessage(parsed);
          } catch (err) {
            console.error("❌ JSON parse error:", err);
          }
        }
      }
    }

    if (onDone) onDone();
  } catch (err) {
    console.error("❌ Streaming error:", err);
    if (onError) onError(err);
  }
};


export default api;
