import { Component, EventEmitter, Input, Output, OnInit, OnDestroy } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AvatarService } from '@services/avatar.service';
import { Subscription } from 'rxjs';

@Component({
    selector: 'app-chat',
    templateUrl: './chat.component.html',
    styleUrls: ['./chat.component.scss'],
    standalone: false
})
export class ChatComponent implements OnInit, OnDestroy {
  @Input() visible: boolean = false;
  isCollapsed = true;
  userMessage: string = '';
  messages: { user: string; text: string }[] = [];
  backendUrl: string = 'http://localhost:5000/query';
  avatarImage: string = '../assets/icons/avatar1.png';
  showChat: boolean = false;
  private subscription: Subscription = new Subscription();

  @Output() updateDashboard = new EventEmitter<string>();

  constructor(
    private http: HttpClient,
    private avatarService: AvatarService
  ) {}

  ngOnInit() {
    // Listen for avatar walkthrough completion
    window.addEventListener('toggleChat', this.handleToggleChat.bind(this));
  }

  ngOnDestroy() {
    window.removeEventListener('toggleChat', this.handleToggleChat.bind(this));
    this.subscription.unsubscribe();
  }

  handleToggleChat(event: any) {
    this.showChat = event.detail;
    if (!this.showChat) {
      this.isCollapsed = true;
    }
  }

  toggleChat(): void {
    if (this.showChat) {
      this.isCollapsed = !this.isCollapsed;
    }
  }

  sendMessage(): void {
    if (this.userMessage.trim()) {
      // Add user message to the chat
      this.messages.push({ user: 'User', text: this.userMessage });

      // Send message to AI-ML backend
      this.subscription.add(
        this.http
          .post<any>(this.backendUrl, { question: this.userMessage })
          .subscribe({
            next: (response) => {
              const botResponse = response.response || 'No response from AI.';
              this.updateDashboard.emit(botResponse);
              this.messages.push({ user: 'Bot', text: botResponse });
            },
            error: () => {
              this.messages.push({ user: 'Bot', text: 'Error connecting to server.' });
            }
          })
      );

      this.userMessage = '';
    }
  }
}