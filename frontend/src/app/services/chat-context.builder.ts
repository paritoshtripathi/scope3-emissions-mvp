import { Injectable } from '@angular/core';
import { ChatMessage, MessageContext } from './chat.types';

@Injectable({
  providedIn: 'root'
})
export class ContextBuilder {
  private context: MessageContext = {};

  reset(): this {
    this.context = {};
    return this;
  }

  withHistory(messages: ChatMessage[]): this {
    this.context.history = messages
      .filter(msg => !msg.isTourMessage)
      .map(msg => ({
        role: msg.user.toLowerCase(),
        content: msg.text
      }));
    return this;
  }

  withInsights(insights: any[]): this {
    this.context.insights = insights;
    return this;
  }

  withMetadata(metadata: Record<string, any>): this {
    this.context.metadata = {
      ...this.context.metadata,
      ...metadata
    };
    return this;
  }

  private validate(context: MessageContext): MessageContext {
    if (!context.history) {
      context.history = [];
    }
    if (!context.insights) {
      context.insights = [];
    }
    if (!context.metadata) {
      context.metadata = {};
    }
    return context;
  }

  build(): MessageContext {
    return this.validate({ ...this.context });
  }
}