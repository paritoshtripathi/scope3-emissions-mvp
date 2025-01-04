import { Component, OnInit, ViewChild } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { DashboardComponent } from '@components/dashboard/dashboard.component'; // Adjust the import path as needed

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html', // Use external HTML file
  styleUrls: ['./app.component.scss'], // Include styles
  standalone: false
})
export class AppComponent implements OnInit {
  backendData: number[] = [];
  chatVisible = false;
 
  constructor(private http: HttpClient) {}

  ngOnInit(): void {

    window.addEventListener('toggleChat', (event: any) => {
      this.chatVisible = event.detail;
    });
  }

  toggleChatVisibility(visible: boolean): void {
    this.chatVisible = visible;
  }
}
