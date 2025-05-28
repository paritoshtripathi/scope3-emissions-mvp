import { Inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, firstValueFrom } from 'rxjs';
import { AiMlService } from './ai-ml.service';
import { AvatarService } from './avatar.service';
import { 
  ChatMessage, 
  MessageType, 
  MessageStatus, 
  ChatState, 
  ChatConfig, 
  CHAT_CONFIG,
  ChatError 
} from './chat.types';
import { ContextBuilder } from './chat-context.builder';
import { MessageQueueService } from './message-queue.service';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private state = new BehaviorSubject<ChatState>({
    messages: [],
    isTourMode: true,
    currentContext: {}
  });

  constructor(
    private http: HttpClient,
    private aiMlService: AiMlService,
    private avatarService: AvatarService,
    private contextBuilder: ContextBuilder,
    private messageQueue: MessageQueueService,
    @Inject(CHAT_CONFIG) private config: ChatConfig
  ) {
    console.log('ChatService initialized with config:', config);
    
    this.messageQueue.setMessageProcessor(this.processMessage.bind(this));

    this.avatarService.getTourStatus().subscribe((isComplete: boolean) => {
      const currentState = this.state.value;
      this.state.next({
        ...currentState,
        isTourMode: !isComplete
      });
    });

    this.messageQueue.getStatus().subscribe(status => {
      if (status === MessageStatus.ERROR) {
        this.handleError(new ChatError('QUEUE_ERROR', 'Message processing failed'));
      }
    });
  }

  getState(): Observable<ChatState> {
    return this.state.asObservable();
  }

  async addTourMessage(text: string): Promise<void> {
    const tourMessage: ChatMessage = {
      id: Date.now().toString(),
      user: MessageType.AVATAR,
      text,
      timestamp: new Date(),
      isTourMessage: true,
      status: MessageStatus.PENDING
    };
    
    await this.addMessage(tourMessage);

    try {
      const explanation = await firstValueFrom(
        this.avatarService.generateExplanation({ message: text })
      );
      if (explanation) {
        const insightMessage: ChatMessage = {
          id: Date.now().toString(),
          user: MessageType.AVATAR,
          text: explanation,
          timestamp: new Date(),
          isTourMessage: true,
          status: MessageStatus.PENDING
        };
        await this.addMessage(insightMessage);
      }
    } catch (error) {
      console.error('Error generating tour insight:', error);
    }
  }

  async sendMessage(text: string): Promise<void> {
    console.log('Sending message:', text);
    if (!text.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      user: MessageType.USER,
      text,
      timestamp: new Date(),
      status: MessageStatus.PENDING
    };

    await this.addMessage(userMessage);
  }

  private async addMessage(message: ChatMessage): Promise<void> {
    console.log('Adding message to state:', message);
    const currentState = this.state.value;
    this.state.next({
      ...currentState,
      messages: [...currentState.messages, message]
    });
    await this.messageQueue.addMessage(message);
  }

  private async processMessage(message: ChatMessage): Promise<void> {
    console.log('Processing message:', message);
    try {
      if (message.user === MessageType.USER) {
        await this.processUserMessage(message);
      } else if (message.user === MessageType.AVATAR) {
        await this.processAvatarMessage(message);
      }
    } catch (error) {
      console.error('Error processing message:', error);
      throw new ChatError(
        'PROCESS_ERROR',
        'Failed to process message',
        true,
        { messageId: message.id }
      );
    }
  }

  private async processUserMessage(message: ChatMessage): Promise<void> {
    console.log('Processing user message:', message);
    const currentState = this.state.value;
    
    // Add loading message
    const loadingMessage: ChatMessage = {
      id: Date.now().toString(),
      user: MessageType.BOT,
      text: '',
      timestamp: new Date(),
      status: MessageStatus.LOADING,
      isLoading: true
    };
    
    this.state.next({
      ...currentState,
      messages: [...currentState.messages, loadingMessage]
    });

    try {
      // Get insights for context
      console.log('Fetching insights...');
      const insights = await firstValueFrom(this.avatarService.getInsights());
      console.log('Insights received:', insights);
      
      // Build context
      console.log('Building context...');
      const context = this.contextBuilder
        .reset()
        .withHistory(currentState.messages)
        .withInsights(insights)
        .withMetadata({ messageId: message.id })
        .build();
      console.log('Context built:', context);

      // Call RAG API with MOE routing
      console.log('Calling RAG API with MOE...', this.config.ragApiUrl);
      let response;
      try {
        response = await firstValueFrom(
          this.http.post<any>(`${this.config.ragApiUrl}/query`, {
            text: message.text,
            context: {
              ...context,
              query: message.text,
              history: context.history,
              insights: context.insights
            },
            options: {
              use_moe: true,
              max_tokens: 250,
              temperature: 0.2
            }
          })
        );
      } catch (error: any) {
        console.error('RAG API Error:', error);
        throw new ChatError(
          'RAG_API_ERROR',
          `Failed to get response from RAG API: ${error.message || 'Unknown error'}`,
          true,
          { messageId: message.id, statusCode: error.status }
        );
      }
      console.log('MOE API response:', response);

      let finalResponse: string;
      if (response.error) {
        finalResponse = "I'm not able to process that request right now. Could you try asking something about scope 3 emissions or the dashboard?";
      } else {
        // Use the combined expert responses
        const expertResponses = response.expert_responses || {};
        const analysis = response.analysis || {};
        
        if (Object.keys(expertResponses).length === 0) {
          finalResponse = "I specialize in scope 3 emissions and dashboard analysis. While I can engage in general conversation, I can provide the most value when discussing these topics. What would you like to know about emissions or the dashboard?";
        } else {
          finalResponse = response.response || expertResponses.narrative || analysis.scope3?.summary;
        }
      }

      // Update bot response
      const botMessage: ChatMessage = {
        id: loadingMessage.id,
        user: MessageType.BOT,
        text: finalResponse,
        timestamp: new Date(),
        status: MessageStatus.SENT,
        metadata: {
          experts_used: response.metadata?.experts_used || [],
          confidence: response.confidence || 0
        }
      };

      // Update state
      this.state.next({
        ...this.state.value,
        messages: this.state.value.messages.map(msg =>
          msg.id === loadingMessage.id ? botMessage : msg
        ),
        currentContext: context
      });

    } catch (error) {
      console.error('Error in processUserMessage:', error);
      this.handleError(error);
    }
  }

  private async processAvatarMessage(message: ChatMessage): Promise<void> {
    console.log('Processing avatar message:', message);
    const currentState = this.state.value;
    this.state.next({
      ...currentState,
      messages: currentState.messages.map(msg =>
        msg.id === message.id ? { ...msg, status: MessageStatus.SENT } : msg
      )
    });
  }

  private handleError(error: any): void {
    console.error('Chat error:', error);
    
    let errorText = 'I encountered an error. ';
    if (error instanceof ChatError && error.code === 'RAG_API_ERROR') {
      if (error.metadata?.['statusCode'] === 0) {
        errorText += 'Unable to connect to the AI service. Please ensure the service is running and try again.';
      } else {
        errorText += 'There was an issue processing your request. Please try again in a moment.';
      }
    } else {
      errorText += 'While I specialize in scope 3 emissions and dashboard analysis, I aim to be helpful with any query. Could you try rephrasing your question?';
    }
    
    const errorMessage: ChatMessage = {
      id: Date.now().toString(),
      user: MessageType.SYSTEM,
      text: errorText,
      timestamp: new Date(),
      status: MessageStatus.ERROR,
      metadata: {
        error: error instanceof ChatError ? error : new ChatError('UNKNOWN', 'Unknown error')
      }
    };

    this.state.next({
      ...this.state.value,
      messages: [...this.state.value.messages, errorMessage]
    });
  }

  clearHistory(): void {
    this.messageQueue.clearQueue();
    this.state.next({
      messages: [],
      isTourMode: this.state.value.isTourMode,
      currentContext: {}
    });
  }
}