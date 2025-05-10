import { Component, OnInit } from '@angular/core';
import { ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
  standalone: false
})
export class DashboardComponent implements OnInit {
  isDarkTheme$ = this.themeService.isDarkTheme$;
  errorMessage: string | null = null;
  insights: any[] = [];
  reductionPredictions: any[] = [];
  totalEmissions: number = 1250;
  reductionTarget: number = 15;
  categoriesCount: number = 5;

  constructor(private themeService: ThemeService) {}

  ngOnInit(): void {
    console.log('Dashboard initialized');
  }
}