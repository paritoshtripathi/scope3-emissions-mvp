import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexDataLabels,
  ApexTitleSubtitle,
  ApexStroke,
  ApexGrid,
  ApexNonAxisChartSeries,
  ApexResponsive,
  ApexLegend
} from "ng-apexcharts";

export type ChartOptions = {
  series: ApexAxisChartSeries | ApexNonAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  dataLabels: ApexDataLabels;
  grid: ApexGrid;
  stroke: ApexStroke;
  title: ApexTitleSubtitle;
  labels: string[];
  legend: ApexLegend;
  responsive: ApexResponsive[];
};

@Component({
  selector: 'app-canvas',
  templateUrl: './canvas.component.html',
  styleUrls: ['./canvas.component.scss'],
  standalone: false
})
export class CanvasComponent implements OnInit {
  insights: any[] = [];
  chartOptions: Partial<ChartOptions> = {};

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    this.http.get<any>('http://localhost:3000/api/agent/insights?persona=CXO&fileId=demo')
      .subscribe(res => {
        this.insights = res.insights;
        this.insights.forEach(insight => {
          if (insight.chartType === 'pie' || insight.chartType === 'donut') {
            insight.chartOptions = {
              series: insight.values,
              chart: {
                type: insight.chartType,
                height: 350
              },
              labels: insight.labels,
              responsive: [{
                breakpoint: 480,
                options: {
                  chart: {
                    width: 300
                  },
                  legend: {
                    position: 'bottom'
                  }
                }
              }]
            };
          } else if (insight.chartType === 'bar') {
            insight.chartOptions = {
              series: [{
                name: 'Emissions',
                data: insight.values
              }],
              chart: {
                type: 'bar',
                height: 350
              },
              xaxis: {
                categories: insight.labels
              }
            };
          }
        });
      });
  }
}