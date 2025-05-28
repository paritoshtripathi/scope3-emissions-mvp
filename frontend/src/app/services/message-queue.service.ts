import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { ChatMessage, MessageStatus, ChatError } from './chat.types';

@Injectable({
  providedIn: 'root'
})
export class MessageQueueService {
  private queue: ChatMessage[] = [];
  private processing = false;
  private messageProcessor!: (message: ChatMessage) => Promise<void>;
  private queueStatus = new BehaviorSubject<MessageStatus>(MessageStatus.PENDING);

  setMessageProcessor(processor: (message: ChatMessage) => Promise<void>): void {
    this.messageProcessor = processor;
  }

  getStatus(): Observable<MessageStatus> {
    return this.queueStatus.asObservable();
  }

  async addMessage(message: ChatMessage): Promise<void> {
    this.queue.push(message);
    if (!this.processing) {
      await this.processQueue();
    }
  }

  private async processQueue(): Promise<void> {
    if (!this.messageProcessor) {
      throw new ChatError(
        'PROCESSOR_NOT_SET',
        'Message processor not set',
        false
      );
    }

    this.processing = true;
    this.queueStatus.next(MessageStatus.PENDING);

    while (this.queue.length > 0) {
      const message = this.queue[0];
      try {
        await this.messageProcessor(message);
        this.queue.shift(); // Remove processed message
        this.queueStatus.next(MessageStatus.SENT);
      } catch (error) {
        this.queueStatus.next(MessageStatus.ERROR);
        if (error instanceof ChatError && error.retry) {
          // Move to end of queue for retry
          this.queue.push(this.queue.shift()!);
        } else {
          // Remove failed message
          this.queue.shift();
        }
      }
    }

    this.processing = false;
  }

  clearQueue(): void {
    this.queue = [];
    this.processing = false;
    this.queueStatus.next(MessageStatus.PENDING);
  }
}