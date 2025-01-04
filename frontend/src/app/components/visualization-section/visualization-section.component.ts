import { Component, OnInit, Input, OnChanges, SimpleChanges } from '@angular/core';

@Component({
  selector: 'app-visualization-section',
  templateUrl: './visualization-section.component.html',
  styleUrls: ['./visualization-section.component.scss'],
  standalone: false
})
export class VisualizationSectionComponent implements OnInit, OnChanges {
  @Input() insights: any[] = [];
  @Input() predictions: any[] = [];
  pieChartOptions: any;
  barChartOptions: any;
  dPieChartOptions: any;
  dBarChartOptions: any;
  error: string | null = null;

  ngOnInit(): void {
    console.log('VisualizationSectionComponent initialized');
    this.initializeStaticCharts();
  }

  ngOnChanges(changes: SimpleChanges): void {

    console.log('VisualizationSectionComponent changes', changes);
    if (changes['insights'] && this.insights?.length) {
      this.updateDynamicPieChart();
      console.log('Insights data updated');
    } else {
      this.error = 'Failed to load insights data.';
    }

    if (changes['predictions'] && this.predictions?.length) {
      this.updateDynamicBarChart();
    } else {
      this.error = this.error || 'Failed to load predictions data.';
    }
  }

  initializeStaticCharts(): void {
    this.pieChartOptions = {
      title: { text: 'Emissions Distribution', left: 'center' },
      tooltip: { trigger: 'item' },
      series: [
        {
          name: 'Static Emissions',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 1048, name: 'Category A' },
            { value: 735, name: 'Category B' },
            { value: 580, name: 'Category C' },
            { value: 484, name: 'Category D' },
            { value: 300, name: 'Category E' }
          ]
        }
      ]
    };

    this.barChartOptions = {
      title: { text: 'Reduction Achievements', left: 'center' },
      xAxis: { type: 'category', data: ['A', 'B', 'C', 'D', 'E'] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [500, 400, 300, 200, 100] }]
    };

    this.dPieChartOptions = {
      title: { text: 'Emissions Distribution', left: 'center' },
      tooltip: { trigger: 'item' },
      series: [
        {
          name: 'Static Emissions',
          type: 'pie',
          radius: '50%',
          data: [
            { value: 1048, name: 'Category A' },
            { value: 735, name: 'Category B' },
            { value: 580, name: 'Category C' },
            { value: 484, name: 'Category D' },
            { value: 300, name: 'Category E' }
          ]
        }
      ]
    };

    this.dBarChartOptions = {
      title: { text: 'Reduction Achievements', left: 'center' },
      xAxis: { type: 'category', data: ['A', 'B', 'C', 'D', 'E'] },
      yAxis: { type: 'value' },
      series: [{ type: 'bar', data: [500, 400, 300, 200, 100] }]
    };
  }

  updateDynamicPieChart(): void {
    this.dPieChartOptions = {
      ...this.dPieChartOptions,
      series: [
        {
          ...this.dPieChartOptions.series[0],
          data: this.insights.map((item) => ({ value: item.value, name: item.category }))
        }
      ]
    };
    //this.pieChartOptions.series[0].data = this.insights;
  }

  updateDynamicBarChart(): void {
    this.dBarChartOptions = {
      ...this.dBarChartOptions,
      series: [
        {
          ...this.dBarChartOptions.series[0],
          data: this.predictions.map((item) => item.value)
        }
      ],
      xAxis: {
        ...this.dBarChartOptions.xAxis,
        data: this.predictions.map((item) => item.category)
      }
    };
    //this.barChartOptions.series[0].data = this.predictions.map((item) => item.value);
    //this.barChartOptions.xAxis.data = this.predictions.map((item) => item.category);
  }
}
