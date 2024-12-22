import { Component, OnInit } from '@angular/core';
import { ChartData, ChartOptions } from 'chart.js';
import { DashboardService } from '../../services/dashboard.service';

@Component({
    selector: 'app-dashboard',
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.css'],
    standalone: false
})
export class DashboardComponent implements OnInit {
  insights: any[] = [];
  selectedCategory: string = '';
  reductionPercentage: number = 0;
  predictionResult: any = null;

  // Chart data and options
  public pieChartData: ChartData<'pie'> = { labels: [], datasets: [{ data: [] }] };
  public barChartData: ChartData<'bar'> = { labels: [], datasets: [{ data: [] }] };
  public chartOptions: ChartOptions = { responsive: true };

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.loadInsights();
  }

  // Load emission insights
  loadInsights(): void {
    this.dashboardService.getInsights().subscribe(response => {
      this.insights = response.insights;

      // Populate chart data
      this.pieChartData.labels = this.insights.map(item => item.category);
      this.pieChartData.datasets[0].data = this.insights.map(item => item.total_emissions);

      this.barChartData.labels = this.insights.map(item => item.category);
      this.barChartData.datasets[0].data = this.insights.map(item => item.total_reduction);
    });
  }

  // Predict reduction based on user input
  predictReduction(): void {
    const payload = { category: this.selectedCategory, reduction_percentage: this.reductionPercentage };
    this.dashboardService.predictReduction(payload).subscribe(response => {
      this.predictionResult = response;
    });
  }
}
