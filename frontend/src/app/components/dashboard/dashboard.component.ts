import { Component, OnInit } from '@angular/core';
import { DashboardService } from '@services/dashboard.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
  standalone: false
})
export class DashboardComponent implements OnInit {
  insights: any[] = [];
  reductionPredictions: any[] = [];
  errorMessage: string | null = null;

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.dashboardService.getInsights().subscribe({
      next: (data) => {
        console.log('data', data);
        this.insights = data.pieData;
        this.reductionPredictions = data.barData;
      },
      error: (error) => {
        console.error('Failed to fetch dashboard data', error);
        this.errorMessage = 'Unable to load dashboard data. Please try again later.';
        
      },
      complete: () => {
        
        console.log('insights', this.insights);
        console.log('predictions', this.reductionPredictions);
        console.log('Dashboard data fetch completed');
      }
   });
  }

  onWalkthroughComplete(): void {
    console.log('Walkthrough completed');
    // Additional actions post walkthrough, if any
  }

  onChatToggle(): void {
    // Emit an event to the AppComponent or call a shared service to trigger visibility
    const appEvent = new CustomEvent('toggleChat', { detail: true });
    window.dispatchEvent(appEvent); // Dispatch event to toggle chat visibility
  }
}
