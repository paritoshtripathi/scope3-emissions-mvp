import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
})
export class ChatComponent {
  messages: { user: string; text: string }[] = [];
  userInput: string = '';

  constructor(private http: HttpClient) {}

  sendMessage() {
    if (this.userInput.trim()) {
      this.messages.push({ user: 'User', text: this.userInput });
      this.http
        .post('/api/langchain/query', { question: this.userInput })
        .subscribe((response: any) => {
          this.messages.push({ user: 'Bot', text: response.response });
        });
      this.userInput = '';
    }
  }
}
