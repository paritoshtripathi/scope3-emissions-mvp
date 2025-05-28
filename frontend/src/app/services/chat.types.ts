import { InjectionToken } from '@angular/core';

export enum MessageType {
  USER = 'User',
  BOT = 'Bot',
  AVATAR = 'Avatar',
  SYSTEM = 'System'
}

export enum MessageStatus {
  PENDING = 'PENDING',
  SENT = 'SENT',
  ERROR = 'ERROR',
  LOADING = 'LOADING'
}

export interface ChatMessage {
  id: string;
  user: MessageType;  // Changed from type to user to match template
  text: string;
  timestamp: Date;
  isLoading?: boolean;
  isTourMessage?: boolean;
  metadata?: Record<string, any>;
  status: MessageStatus;
}

export interface MessageContext {
  history?: Array<{
    role: string;
    content: string;
  }>;
  insights?: any[];
  metadata?: Record<string, any>;
}

export interface ChatState {
  messages: ChatMessage[];
  isTourMode: boolean;
  currentContext: MessageContext;
}

export interface ChatConfig {
  ragApiUrl: string;
  maxHistory: number;
  retryAttempts: number;
  messageTimeout: number;
}

export const CHAT_CONFIG = new InjectionToken<ChatConfig>('CHAT_CONFIG');

export class ChatError extends Error {
  constructor(
    public code: string,
    message: string,
    public retry: boolean = false,
    public metadata?: Record<string, any>
  ) {
    super(message);
    this.name = 'ChatError';
  }
}