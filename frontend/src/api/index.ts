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

export const sendQuery = async (
  query: string,
  onMessage: (chunk: any) => void,
  onDone?: () => void,
  onError?: (err: any) => void
) => {
  try {
    const response = await fetch("http://localhost:8000/chat", {
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
          try {
            const parsed = JSON.parse(jsonStr);
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
