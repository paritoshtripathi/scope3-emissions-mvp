import { Component, OnInit, ViewChild } from '@angular/core';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'], // Updated for SCSS
  standalone: false
})
export class DashboardComponent implements OnInit {
  constructor() {}

  ngOnInit(): void {
    // Any additional logic for initializing the dashboard container
  }

  // Handle updates from app-chat component
  onChatUpdate(updateData: any): void {
    console.log('Chat update received:', updateData);
    // Handle updates or pass them to child components if necessary
  }
}
