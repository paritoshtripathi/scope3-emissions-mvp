import { Component, EventEmitter, Output } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
    selector: 'app-chat',
    templateUrl: './chat.component.html',
    styleUrls: ['./chat.component.scss'],
    standalone: false
})
export class ChatComponent {
  isCollapsed = true;
  userMessage: string = '';
  messages: { user: string; text: string }[] = [];
  backendUrl: string = 'http://localhost:5000/query';

  @Output() updateDashboard = new EventEmitter<string>();

  constructor(private http: HttpClient) {}

  toggleChat(): void {
    this.isCollapsed = !this.isCollapsed;
  }

  sendMessage(): void {
    if (this.userMessage.trim()) {
      // Add user message to the chat
      this.messages.push({ user: 'User', text: this.userMessage });

      // Send message to AI-ML backend
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
        });

      this.userMessage = '';
    }
  }
}
