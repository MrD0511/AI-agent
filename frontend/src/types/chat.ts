export interface Message {
  id: string;
  role: 'user' | 'bot';
  response: MessageChunk[]; // <-- same for both
  isLoading?: boolean;
  isError?: boolean;
}

export type MessageChunk = {
  node: string; // e.g. "text", "function_call"
  content: string; // e.g. "Hello, how can I help you?"
  type: string; // e.g. "text", "ToolMessage"
};