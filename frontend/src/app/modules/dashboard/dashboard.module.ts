import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; // Import FormsModule
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatButtonModule } from '@angular/material/button';
import { RouterModule } from '@angular/router';
import { NgxEchartsModule, NGX_ECHARTS_CONFIG } from 'ngx-echarts';
import * as echarts from 'echarts';
import { MatIconModule } from '@angular/material/icon';


import { DashboardRoutingModule } from './dashboard-routing.module';
import { DashboardComponent } from '@components/dashboard/dashboard.component';
import { VisualizationSectionComponent } from '@components/visualization-section/visualization-section.component';
@NgModule({
  declarations: [
    DashboardComponent,
    VisualizationSectionComponent
  ],
  imports: [
    CommonModule,
    RouterModule,
    FormsModule,
    DashboardRoutingModule,
    MatSidenavModule,
    MatListModule,
    MatTooltipModule,
    MatButtonModule,
    MatIconModule,
    MatToolbarModule,
    NgxEchartsModule.forRoot({
      echarts
    })
  ],
  providers: [
    {
      provide: NGX_ECHARTS_CONFIG,
      useValue: { echarts }
    }
  ],
  exports: [
    DashboardComponent] // Export the component so it can be used in AppModule
   
})
export class DashboardModule {}
