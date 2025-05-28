import { Component, EventEmitter, Input, Output, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { ChatService } from '../../services/chat.service';
import { ChatMessage, ChatState, MessageType } from '../../services/chat.types';
import { AvatarService } from '@services/avatar.service';
import { Subject, takeUntil } from 'rxjs';

interface ChatToggleEvent extends CustomEvent {
  detail: boolean;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
  standalone: false
})
export class ChatComponent implements OnInit, OnDestroy {
  @Input() visible: boolean = false;
  @Output() updateDashboard = new EventEmitter<string>();
  
  messages: ChatMessage[] = [];
  currentMessage = '';
  isTourMode = true;
  isCollapsed = true;
  avatarImage: string = '../assets/icons/avatar1.png';
  showChat: boolean = false;
  MessageType = MessageType;
  private destroy$ = new Subject<void>();

  @ViewChild('chatMessages') private chatMessagesRef!: ElementRef;
  @ViewChild('messageInput') private messageInput!: ElementRef;

  constructor(
    private chatService: ChatService,
    private avatarService: AvatarService
  ) {
    this.handleToggleChat = this.handleToggleChat.bind(this);
  }

  ngOnInit(): void {
    // Start with chat invisible
    this.visible = false;
    this.showChat = false;
    
    // Subscribe to chat state
    this.chatService.getState()
      .pipe(takeUntil(this.destroy$))
      .subscribe((state: ChatState) => {
        this.messages = state.messages;
        
        // Handle tour mode changes
        if (this.isTourMode !== state.isTourMode) {
          this.isTourMode = state.isTourMode;
          if (state.isTourMode) {
            // Hide chat when tour starts
            this.visible = false;
            this.showChat = false;
            this.isCollapsed = true;
          }
        }
        
        if (!this.isCollapsed) {
          this.scrollToBottom();
        }
        
        // Emit last non-tour message to update dashboard
        const lastMessage = [...state.messages].reverse()
          .find(msg => !msg.isTourMessage && msg.user === MessageType.BOT);
        if (lastMessage) {
          this.updateDashboard.emit(lastMessage.text);
        }
      });

    // Listen for avatar tour messages
    this.avatarService.getTourMessages()
      .pipe(takeUntil(this.destroy$))
      .subscribe(message => {
        if (message) {
          this.chatService.addTourMessage(message);
          // Hide chat during tour
          this.visible = false;
          this.showChat = false;
          this.isCollapsed = true;
        }
      });

    // Listen for chat toggle
    window.addEventListener('toggleChat', this.handleToggleChat as EventListener);
    
    // Listen for tour completion
    this.avatarService.getTourStatus()
      .pipe(takeUntil(this.destroy$))
      .subscribe(isComplete => {
        if (isComplete) {
          this.isTourMode = false;
          this.showChat = true;
          this.visible = true;
          this.isCollapsed = true;
        }
      });
  }

  ngOnDestroy(): void {
    window.removeEventListener('toggleChat', this.handleToggleChat as EventListener);
    this.destroy$.next();
    this.destroy$.complete();
  }

  private handleToggleChat(event: Event): void {
    const customEvent = event as ChatToggleEvent;
    this.showChat = customEvent.detail;
    this.visible = customEvent.detail;
    if (!this.showChat) {
      this.isCollapsed = true;
    }
  }

  toggleChat(): void {
    console.log('Toggle chat clicked', { isTourMode: this.isTourMode, isCollapsed: this.isCollapsed });
    
    // Don't allow expanding during tour mode
    if (this.isTourMode) {
      return;
    }

    this.isCollapsed = !this.isCollapsed;

    if (!this.isCollapsed) {
      setTimeout(() => {
        this.scrollToBottom();
        if (this.messageInput) {
          this.messageInput.nativeElement.focus();
        }
      }, 300);
    }
  }

  async sendMessage(): Promise<void> {
    if (this.currentMessage.trim()) {
      await this.chatService.sendMessage(this.currentMessage);
      this.currentMessage = '';
      if (this.messageInput) {
        this.messageInput.nativeElement.focus();
      }
    }
  }

  private scrollToBottom(): void {
    try {
      setTimeout(() => {
        if (this.chatMessagesRef?.nativeElement) {
          const element = this.chatMessagesRef.nativeElement;
          element.scrollTop = element.scrollHeight;
        }
      });
    } catch (err) {
      console.error('Error scrolling to bottom:', err);
    }
  }
}