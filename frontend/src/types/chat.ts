export interface Message {
  id: string;
  role: 'user' | 'bot';
  data: MessageChunk[]; // <-- same for both
  isLoading?: boolean;
  isError?: boolean;
}

export type MessageChunk =
  | { type: 'content'; value: string }
  | { type: 'function_call'; function_call: FunctionCall }
  | { type: 'error'; value: string };
  
export interface FunctionCall {
  name: string;
  arguments: Record<string, any>;
  canExecute?: boolean;
  status?: 'pending' | 'success' | 'error';
  timestamp?: number;
}