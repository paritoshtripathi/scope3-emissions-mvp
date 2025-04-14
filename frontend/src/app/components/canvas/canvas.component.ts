
import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApexChart, ApexNonAxisChartSeries, ApexResponsive } from 'ng-apexcharts';

@Component({
  selector: 'app-canvas',
  templateUrl: './canvas.component.html',
  styleUrls: ['./canvas.component.scss'],
  standalone: false
})
export class CanvasComponent implements OnInit {
  insights: any[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http.get<any>('http://localhost:3000/api/agent/insights?persona=CXO&fileId=demo')
      .subscribe(res => this.insights = res.insights);
  }
}
