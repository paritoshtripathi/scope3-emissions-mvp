import { Component, OnInit } from '@angular/core';


@Component({
  selector: 'app-visualization-section',
  templateUrl: './visualization-section.component.html',
  styleUrls: ['./visualization-section.component.scss'],
  standalone: false
})
export class VisualizationSectionComponent implements OnInit {
  pieChartOptions: any;
  barChartOptions: any;

  ngOnInit(): void {
    console.log('VisualizationSectionComponent initialized');
    this.initializePieChart();
    this.initializeBarChart();
  }
 
  initializePieChart(): void {
    this.pieChartOptions = {
      title: { text: 'Emissions Distribution', left: 'center' },
      tooltip: { trigger: 'item' },
      series: [
        {
          name: 'Emissions',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 1048, name: 'Category A' },
            { value: 735, name: 'Category B' },
            { value: 580, name: 'Category C' },
            { value: 484, name: 'Category D' },
            { value: 300, name: 'Category E' }
          ],
          emphasis: {
            itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' }
          }
        }
      ]
    };
  }

  initializeBarChart(): void {
    this.barChartOptions = {
      title: { text: 'Reduction Achievements', left: 'center' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['Category A', 'Category B', 'Category C', 'Category D', 'Category E'] },
      yAxis: { type: 'value' },
      series: [
        {
          data: [820, 932, 901, 934, 1290],
          type: 'bar'
        }
      ]
    };
  }
}
