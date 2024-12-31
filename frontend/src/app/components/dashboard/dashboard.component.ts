import { Component, OnInit, ViewChild } from '@angular/core';
import { DashboardService } from '@services/dashboard.service'; // Updated import path to @services/data.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'], // Updated for SCSS
  standalone: false
})
export class DashboardComponent implements OnInit {
  insights: any[] = [];
  reductionPredictions: any[] = [];
  errorMessage: string | null = null;


  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    // Any additional logic for initializing the dashboard container
    console.log('Dashboard initialized');
    // Fetch data from the service
    this.fetchData();
  }

  fetchData(): void {
    this.dashboardService.getInsights().subscribe({
      next: (data) => {
        this.insights = data.pieData;
        this.reductionPredictions = data.barData;
      },
      error: (err) => console.error('Error fetching insights:', err),
      complete: () => console.log('Insights request complete')
    });
  
    this.dashboardService.predictReduction({ category: 'Employee Commuting', reduction_percentage: 50 }).subscribe({
      next: (data) => {
        console.log('Prediction Data:', data);
      },
      error: (err) => console.error('Error fetching predictions:', err),
      complete: () => console.log('Predictions request complete')
    });
  }

  // Handle updates from app-chat component
  onChatUpdate(updateData: any): void {
    console.log('Chat update received:', updateData);
    // Handle updates or pass them to child components if necessary
  }
}
